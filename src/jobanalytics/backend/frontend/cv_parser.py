import docx2txt
import re
import json
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd


def prep_text(text_path):
    text = docx2txt.process(text_path)
    split = re.split(r'\n+', text)
    split = [re.sub(r'(\t+)|(\xa0+)', ' ', line).strip() for line in split]
    split = [line for line in split if line]
    return split


def normalize_text(text):
    return [line.lower() for line in text if line]


def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    filtered_lines = []
    for line in text:
        words = re.split(r' ', line)
        new_line = [word for word in words if not word in stop_words]
        new_line = ' '.join(new_line)
        filtered_lines.append(new_line)
    return filtered_lines


def check_format(file):
    text = prep_text(file)
    tmp = normalize_text(text)
    mand_sections = ['profile', 'education', 'work experience', 'skills']
    profile_check = False
    full_check = False
    for line in tmp:
        if profile_check:
            if line in mand_sections:
                mand_sections.remove(line)
            if not mand_sections:
                full_check = True
                break
        if line == mand_sections[0]:
            profile_check = True
            mand_sections.remove(line)
    return full_check


def order_sections(sections, text):
    indexes = []
    tmp = normalize_text(text)
    for section in sections:
        if section in tmp:
            indexes.append(tmp.index(section))
    indexes.sort()
    existing_sections = [tmp[index] for index in indexes]
    return existing_sections


def next_heading(heading, sections):
    return sections[sections.index(heading)+1]


def get_heading_index(heading, text):
    for line in text:
        if line.lower() == heading:
            return text.index(line)
    return False


def separate_sections(text):
    sections_headings = ['profile', 'objective', 'education', 'work experience', 'skills', 'qualifications',
                         'references']
    sections = {}
    ordered_sections = order_sections(sections_headings, text)
    profile_index = get_heading_index(ordered_sections[0], text)
    sections['personal'] = [text[i] for i in range(profile_index)]
    for heading in ordered_sections:
        if heading == ordered_sections[len(ordered_sections) - 1]:
            index = get_heading_index(heading, text)
            sections[heading] = [text[i] for i in range(index+1, len(text))]
        else:
            first_index = get_heading_index(heading, text)
            end_section = next_heading(heading, ordered_sections)
            end_index = get_heading_index(end_section, text)
            sections[heading] = [text[i] for i in range(first_index + 1, end_index)]
    return sections


def get_section(section, key):
    if key in section:
        return section[key]
    else:
        return None


def split_date_sections(section):
    tmp = section[0]
    section.remove(tmp)
    jobs = []
    for line in section:
        if re.findall(r'\d{4}', line):
            jobs.append(tmp)
            tmp = line
        else:
            tmp += ' ' + line
    jobs.append(tmp)
    return jobs


def n_grams(input_string, n):
    result_list = []
    input_list = [word for line in input_string for word in word_tokenize(line) if word]
    for i in range(len(input_list)-n+1):
        result_list.append(input_list[i:i+n])
    return result_list


def time_spent(job):
    years = re.findall(r'\d{4}', job)
    if len(years) == 1:
        return 1
    elif len(years) == 2:
        return int(years[1]) - int(years[0])


def compare_grade(school, req_grade):
    college_grades = ['1:1', '2:1', '2:2', '3rd']
    college = False
    if ':' in req_grade or req_grade == '3rd':
        college = True
        if re.search(r'\d:\d', school):
            grade = re.findall(r'\d:\d', school)[0].strip()
        elif re.search(r'3rd', school):
            grade = '3rd'
        else:
            return False
    else:
        school = re.sub(r'\d{4}', '', school)
        grade = int(re.findall(r'\d{1,3}', school)[0])
    if college:
        if college_grades.index(grade) <= college_grades.index(req_grade):
            return True
    else:
        if grade >= int(req_grade):
            return True
    return False


def check_skill_requirements(file, requirements):
    keyword_checks = {}
    for requirement in requirements:
        keyword = requirement.requirement_keyword.strip()
        keyword_checks[keyword.lower()] = False
    text = prep_text(file)
    text = normalize_text(text)
    skills = get_section(separate_sections(text), 'skills')
    skills = remove_stop_words(skills)
    for keywords in keyword_checks:
        n = len(word_tokenize(keywords))
        for i in range(n, 0, -1):
            tmp = n_grams(skills, i)
            if fuzzy_matching(keywords, tmp):
                keyword_checks[keywords] = True
                break
    return keyword_checks


def check_experience_requirements(file, requirements):
    keyword_checks = {}
    for requirement in requirements:
        split_keywords = requirement.requirement_keyword.split(',')
        inner_key = split_keywords[1].strip()
        keyword_checks[requirement.requirement_keyword.lower()] = {inner_key.lower(): False}
    text = prep_text(file)
    text = normalize_text(text)
    sections = separate_sections(text)
    experience = get_section(sections, 'work experience')
    experience = remove_stop_words(experience)
    jobs = split_date_sections(experience)
    returned = {}
    for digit in keyword_checks:
        num_req = re.findall(r'^\d', digit)[0]
        num_req = int(num_req)
        for keywords in keyword_checks[digit]:
            for job in jobs:
                time = time_spent(job)
                if time >= num_req:
                    n = len(word_tokenize(keywords))
                    for i in range(n, 0, -1):
                        job_arr = word_tokenize(job)
                        tmp = n_grams(job_arr, i)
                        if fuzzy_matching(keywords, tmp):
                            keyword_checks[digit][keywords] = True
                            break
                    if keyword_checks[digit][keywords]:
                        break
                if keyword_checks[digit][keywords]:
                    break
            returned[digit] = keyword_checks[digit][keywords]
            if keyword_checks[digit][keywords]:
                break
    return returned


def check_education_requirements(file, requirements):
    keyword_checks = {}
    for requirement in requirements:
        split_keywords = requirement.requirement_keyword.split(',')
        inner_key = split_keywords[1].strip()
        keyword_checks[split_keywords[0].lower()] = {inner_key.lower(): False}
    text = prep_text(file)
    text = normalize_text(text)
    text = remove_stop_words(text)
    sections = separate_sections(text)
    education = get_section(sections, 'education')
    schools = split_date_sections(education)
    returned = {}
    for grade in keyword_checks:
        for keywords in keyword_checks[grade]:
            for school in schools:
                if compare_grade(school, grade):
                    n = len(word_tokenize(keywords))
                    for i in range(n, 0, -1):
                        school_arr = word_tokenize(school)
                        tmp = n_grams(school_arr, i)
                        if fuzzy_matching(keywords, tmp):
                            keyword_checks[grade][keywords] = True
                            break
                    if keyword_checks[grade][keywords]:
                        break
                if keyword_checks[grade][keywords]:
                    break
            key = grade + ', ' + keywords
            returned[key] = keyword_checks[grade][keywords]
            if keyword_checks[grade][keywords]:
                break
    return returned


def fuzzy_matching(keywords, tmp):
    for grams in tmp:
        if len(grams) > 1:
            grams = ' '.join(grams)
        p1 = fuzz.ratio(keywords, grams)
        p2 = fuzz.partial_ratio(keywords, grams)
        p3 = fuzz.token_sort_ratio(keywords, grams)
        p4 = fuzz.token_set_ratio(keywords, grams)
        result = (p1 + p2 + p3 + p4) / 4
        if result >= 75:
            return True
    return False


def find_initial(file):
    text = prep_text(file)
    sections = separate_sections(text)
    initial = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'phone_number': None,
    }
    name = re.split(r' ', sections['personal'][0])
    initial['first_name'] = name[0].strip()
    initial['last_name'] = name[1].strip()
    for line in sections['personal']:
        if '@' in line:
            tmp = re.split(r' ', line)
            for word in tmp:
                if '@' in word:
                    initial['email'] = word.strip()
                    break
        if initial['email']:
            break
    for line in sections['personal']:
        if re.search(r'\+?1?\d{9,15}', line):
            initial['phone_number'] = re.findall(r'\+?1?\d{9,15}', line)[0].strip()
            break
    return initial


nonspace = re.compile(r'\S')


def iterparse(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = nonspace.search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded


def get_skills(skills_section):
    with open("frontend/static/frontend/datasets/cleaned_related_skills.json") as f:
        data = list(iterparse(f.read()))
    dataset = pd.DataFrame(data)
    skills = []
    skills_section = [skill.lower() for skill in skills_section]
    for i in range(1, 7):
        grams = n_grams(skills_section, i)
        for word in grams:
            if len(word) == 1:
                skill = word[0]
            else:
                skill = ' '.join(word)
            if skill not in skills:
                if skill in dataset['name'].values:
                    skills.append(skill)
    return skills


def get_summarised_section(section):
    summary = []
    section_list = section.split('\n')
    for line in section_list:
        if re.search(r'\d{4}', line):
            summary.append(line)
    return summary










