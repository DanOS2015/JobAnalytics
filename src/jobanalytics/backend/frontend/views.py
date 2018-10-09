from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import ApplicationForm, RequirementForm, RequirementFormSet, JobForm, CVUploadForm, ApplicantForm
from .models import JobPosting, UserApplication, Requirement, MatchedRequirement, CVUpload
from django.views.generic import CreateView, ListView, View
from django.db import transaction
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .random_forest_classifier import predict_performance
from django.contrib import messages
from .cv_parser import check_format, check_skill_requirements, \
    check_experience_requirements, \
    check_education_requirements, \
    separate_sections, \
    prep_text, \
    split_date_sections, \
    get_section, \
    find_initial, \
    get_skills, \
    get_summarised_section
from django.db.models import Q
from django.forms import inlineformset_factory
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
import docx2txt
import re
import operator


def index(request):
    return render(request, 'frontend/index.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created! Now please login.')
            return redirect('index')
        else:
            args = {
                'form': form,
            }
            return render(request, 'frontend/registration_form.html', args)
    else:
        form = UserCreationForm()
        args = {
            'form': form,
        }
        return render(request, 'frontend/registration_form.html', args)


def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST or None)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            args = {
                'username': user.username,
            }
            return redirect(reverse('user_dashboard', kwargs=args))

        else:
            messages.error(request, 'Information Invalid. Please Try Again.')
            args = {
                'form': form,
            }
            return render(request, 'frontend/login_page.html', args)
    else:
        form = AuthenticationForm()
        args = {
            'form': form,
        }
        return render(request, 'frontend/login_page.html', args)


def logout_user(request):
    logout(request)
    messages.success(request, 'Successfully logged out user.')
    return redirect('index')


@login_required(login_url='/login/')
def data_report(request):
    return render(request, 'frontend/data_report.html')


def cv_format(request):
    return render(request, 'frontend/cv_format.html')


class JobBoard(View):
    model = JobPosting

    def get(self, request):
        jobs = JobPosting.objects.all()
        query = request.GET.get("search")
        if query:
            jobs = jobs.filter(Q(job_title__icontains=query)).distinct()
            if not jobs:
                messages.error(request, 'No jobs matched your query.')
            args = {
                "jobs": jobs,
            }
            return render(request, 'frontend/jobposting_list.html', args)
        else:
            args = {
                "jobs": jobs,
            }
            return render(request, 'frontend/jobposting_list.html', args)


@login_required(login_url='/login/')
def user_dashboard(request, username):
    u = User.objects.get(username=username)
    posted_jobs = get_posted_jobs(username)
    args = {
        'username': u.username,
        'posted_jobs': posted_jobs,
    }
    return render(request, "frontend/user_dashboard.html", args)


@login_required(login_url='/login/')
def add_job_with_previous(request, employer):
    request.session['initial'] = request.session[employer]
    return redirect(reverse('add_job'))


@login_required(login_url='/login/')
def previous_posts(request, username):
    jobs = request.user.jobposting_set.all().distinct('employer')
    if len(jobs):
        posts = {}
        for job in jobs:
            posts[job.employer] = {
                'employer': job.employer,
                'address_line_1': job.address_line_1,
                'address_line_2': job.address_line_2,
                'city': job.city,
                'county': job.county,
                #'employer_logo': job.employer_logo.url,
            }
            request.session[job.employer] = posts[job.employer]
        args = {
            'posts': posts,
        }
        return render(request, 'frontend/previous_posts.html', args)
    else:
        return redirect('add_job')


class AddJob(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = JobPosting
    fields = ["job_title", "employer", "address_line_1", "address_line_2", "city", "county", "employer_logo", "job_description"]
    success_url = reverse_lazy('job_board')

    def get_context_data(self, **kwargs):
        data = super(AddJob, self).get_context_data(**kwargs)
        if self.request.POST:
            data['requirements'] = RequirementFormSet(self.request.POST, self.request.FILES)
        else:
            data['requirements'] = RequirementFormSet()
        return data

    def get_initial(self):
        initial = super(AddJob, self).get_initial()
        initial = initial.copy()
        initial = self.request.session.get('initial')
        self.request.session['initial'] = {}
        return initial

    def form_valid(self, form):
        context = self.get_context_data()
        requirements = context['requirements']
        with transaction.atomic():
            current_user = self.request.user
            self.object = form.save(commit=False)
            self.object.user = current_user
            if requirements.is_valid():
                for requirement in requirements:
                    cd = requirement.cleaned_data
                    req_type = cd.get('requirement_type')
                    if req_type == '1' or req_type == '2':
                        if not check_requirement_format(cd.get('requirement_keyword')):
                            messages.error(self.request, 'Requirement keyword not formatted properly. '
                                                         'Please read instructions and try again.')
                            return self.form_invalid(form)
                self.object.save()
                requirements.instance = self.object
                requirements.save()
                messages.success(self.request, "Successfully posted job.")
                return super(AddJob, self).form_valid(form)
            else:
                messages.error(self.request, "Requirement details missing or are invalid.")
                return self.form_invalid(form)


def job_info(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    args = {
        'job': job,
        'requirements': Requirement.objects.filter(job__job_title=job.job_title),
    }
    if request.user.is_authenticated():
        posted_user = job.user
        current_user = request.user
        if posted_user.id == current_user.id:
            args = {
                'job': job,
                'is_posted_user': True,
                'requirements': Requirement.objects.filter(job__job_title=job.job_title),
            }
            return render(request, 'frontend/job_info.html', args)

    return render(request, 'frontend/job_info.html', args)


def cv_upload(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    if request.method == 'POST':
        form = CVUploadForm(request.POST or None, request.FILES)
        if form.is_valid():
            cv = form.save(commit=False)
            file_check = check_format(cv.file)
            if file_check:
                sections = separate_sections(prep_text(cv.file))
                cv.work_experience_section = '\n'.join(sections['work experience'])
                cv.education_section = '\n'.join(sections['education'])
                cv.skills_section = '\n'.join(sections['skills'])
                cv.save()
                initial = find_initial(cv.file)
                cv_info = {
                    'skills': ','.join(get_skills(sections['skills'])),
                    'work experience': '\n'.join(get_summarised_section(cv.work_experience_section)),
                    'education': '\n'.join(get_summarised_section(cv.education_section)),
                }
                request.session['cv_initial'] = initial
                request.session['cv_info'] = cv_info
                args = {
                    'job_id': job_id,
                    'cv_id': cv.pk,
                }
                return redirect(reverse(applicant_form, kwargs=args))
            else:
                messages.error(request, "CV contents not formatted properly.")
                args = {
                    'job': job,
                    'form': form,
                }
                return render(request, 'frontend/cv_upload.html', args)
        else:
            args = {
                'job': job,
                'form': form,
            }
            return render(request, 'frontend/cv_upload.html', args)
    else:
        form = CVUploadForm()
        args = {
            'job': job,
            'form': form,
        }
        return render(request, 'frontend/cv_upload.html', args)


def applicant_form(request, job_id, cv_id):
    initial = request.session.get('cv_initial')
    job = get_object_or_404(JobPosting, pk=job_id)
    if request.method == 'POST':
        form = ApplicantForm(request.POST or None, request.FILES, initial=initial)
        if form.is_valid():
            applicant = form.save(commit=False)
            existing_applicants = UserApplication.objects.filter(email=applicant.email, job__pk=job_id)
            if existing_applicants:
                messages.error(request, 'You have already applied for this job. You cannot apply again.')
                args = {
                    'job_id': job_id,
                }
                return redirect(reverse('cv_upload', kwargs=args))
            else:
                request.session['first_name'] = applicant.first_name
                request.session['last_name'] = applicant.last_name
                request.session['email'] = applicant.email
                request.session['phone_number'] = applicant.phone_number
                args = {
                    'job_id': job_id,
                    'cv_id': cv_id,
                }
                return redirect(reverse('job_application', kwargs=args))
        else:
            args = {
                'job': job,
                'form': form,
            }
            return render(request, 'frontend/applicant_form.html', args)
    else:
        form = ApplicantForm(initial=initial)
        args = {
            'job': job,
            'form': form,
        }
        return render(request, 'frontend/applicant_form.html', args)


def job_application(request, job_id, cv_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    cv = get_object_or_404(CVUpload, pk=cv_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST or None)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.curriculum_vitae = cv
            application.first_name = request.session.get('first_name')
            application.last_name = request.session.get('last_name')
            application.email = request.session.get('email')
            application.phone_number = request.session.get('phone_number')
            cv_info = request.session.get('cv_info')
            application.skills = cv_info['skills']
            application.education = cv_info['education']
            application.work_experience = cv_info['work experience']
            application.performance = predict_performance(application)[0]
            application.save()
            req_list = Requirement.objects.filter(job__pk=application.job.pk)
            key_list = [req for req in req_list if req.requirement_type == '0']
            exp_list = [req for req in req_list if req.requirement_type == '1']
            edu_list = [req for req in req_list if req.requirement_type == '2']
            if len(exp_list):
                exp_matches = check_experience_requirements(application.curriculum_vitae.file, exp_list)
            if len(key_list):
                key_matches = check_skill_requirements(application.curriculum_vitae.file, key_list)
            if len(edu_list):
                edu_matches = check_education_requirements(application.curriculum_vitae.file, edu_list)
            for requirement in req_list:
                if requirement.requirement_type == '0':
                    matched_requirement = MatchedRequirement.create(
                        application,
                        requirement,
                        key_matches[requirement.requirement_keyword.lower()]
                    )
                elif requirement.requirement_type == '1':
                    matched_requirement = MatchedRequirement.create(
                        application,
                        requirement,
                        exp_matches[requirement.requirement_keyword.lower()]
                    )
                else:
                    matched_requirement = MatchedRequirement.create(
                        application,
                        requirement,
                        edu_matches[requirement.requirement_keyword.lower()]
                    )
                matched_requirement.save()
            messages.success(request, 'Successfully applied to job!')
            return redirect('index')
        else:
            args = {
                'job': job,
                'form': form,
            }
            return render(request, 'frontend/application_form.html', args)
    else:
        form = ApplicationForm()
        args = {
            'job': job,
            'form': form,
        }
        return render(request, 'frontend/application_form.html', args)


@login_required(login_url='/login/')
def applicants_list(request, job_id, username):
    applicants = get_match_ratio(job_id)
    job = get_object_or_404(JobPosting, pk=job_id)
    request.session['job_data_id'] = {'job_id': job_id}
    args = {
        'applicants': applicants,
        'job': job,
    }
    return render(request, 'frontend/applicants_list.html', args)


class FrequentSkillsData(LoginRequiredMixin, APIView):

    def get(self, request):
        session_data = request.session['job_data_id']
        job_id = session_data['job_id']
        applications = UserApplication.objects.filter(job__pk=job_id)
        freq = skill_freq(applications)
        sorted_freq = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
        labels = []
        default = []
        if len(sorted_freq) < 5:
            for tup in sorted_freq:
                labels.append(tup[0])
                default.append(tup[1])
        else:
            for i in range(5):
                labels.append(sorted_freq[i][0])
                default.append(sorted_freq[i][1])
        data = {
            'labels': labels,
            'default': default,
        }
        return Response(data)


class MatchRatioData(LoginRequiredMixin, APIView):

    def get(self, request):
        session_data = request.session['job_data_id']
        job_id = session_data['job_id']
        applications = UserApplication.objects.filter(job__pk=job_id)
        top = []
        below_top = []
        middle = []
        just_above_bottom = []
        bottom = []
        for applicant in applications:
            if applicant.match_ratio >= 79.5:
                top.append(applicant)
            elif applicant.match_ratio >= 59.5:
                below_top.append(applicant)
            elif applicant.match_ratio >= 39.5:
                middle.append(applicant)
            elif applicant.match_ratio >= 19.5:
                just_above_bottom.append(applicant)
            else:
                bottom.append(applicant)
        labels = ['100-80', '80-60', '60-40', '40-20', '20-0']
        default = [len(top), len(below_top), len(middle), len(just_above_bottom), len(bottom)]
        data = {
            'labels': labels,
            'default': default,
        }
        return Response(data)


class WorkEthicData(LoginRequiredMixin, APIView):
    
    def get(self, request):
        session_data = request.session['job_data_id']
        job_id = session_data['job_id']
        applications = UserApplication.objects.filter(job__pk=job_id)
        excellent_worker = applications.filter(performance='Excellent Worker').count()
        satisfactory_worker = applications.filter(performance='Satisfactory Worker').count()
        poor_worker = applications.filter(performance='Poor Worker').count()
        labels = ['Excellent Worker', 'Satisfactory Worker', 'Poor Worker']
        default = [excellent_worker, satisfactory_worker, poor_worker]
        data = {
            'labels': labels,
            'default': default,
        }
        return Response(data)


@login_required(login_url='/login/')
def delete_user_check(request, username):
    user = request.user
    jobs = user.jobposting_set.all()
    args = {
        'user': user,
        'jobs': jobs,
    }
    return render(request, 'frontend/delete_user_check.html', args)


@login_required(login_url='/login/')
def delete_user(request, user_id):
    logout(request)
    user = User.objects.get(pk=user_id)
    user.delete()
    messages.success(request, 'Successfully deleted user.')
    return redirect('index')


@login_required(login_url='/login/')
def delete_job_check(request, job_id):
    job = JobPosting.objects.get(pk=job_id)
    args = {
        "job": job,
        'requirements': Requirement.objects.filter(job__job_title=job.job_title),
    }
    return render(request, "frontend/delete_job_check.html", args)


@login_required(login_url='/login/')
def delete_job(request, job_id):
    job = JobPosting.objects.get(pk=job_id)
    job.delete()
    messages.success(request, 'Successfully deleted job posting.')
    args = {
        'username': request.user.username,
    }
    return redirect(reverse('user_dashboard', kwargs=args))


@login_required(login_url='/login/')
def delete_applicant_check(request, application_id):
    applicant = get_object_or_404(UserApplication, pk=application_id)
    args = {
        'applicant': applicant,
    }
    return render(request, 'frontend/delete_applicant_check.html', args)


@login_required(login_url='/login/')
def delete_applicant(request, application_id):
    applicant = get_object_or_404(UserApplication, pk=application_id)
    applicant.delete()
    messages.success(request, 'Successfully deleted applicant.')
    args = {
        'username': applicant.job.user.username,
        'job_id': applicant.job.id,
    }
    return redirect(reverse('applicants_list', kwargs=args))


@login_required(login_url='/login/')
def update_job(request, job_id):
    job = get_object_or_404(JobPosting, pk=job_id)
    RequirementsFormSet = inlineformset_factory(JobPosting, Requirement, form=RequirementForm, extra=0)
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        requirements = RequirementsFormSet(request.POST, instance=job)
        with transaction.atomic():
            if form.is_valid() and requirements.is_valid():
                job = form.save(commit=False)
                job.user = request.user
                job.save()
                requirements.instance = job
                requirements.save()
                messages.success(request, "Successfully edited job posting!")
                args = {
                    "username": job.user.username,
                }
                return redirect(reverse('user_dashboard', kwargs=args))
            else:
                args = {
                    'job_id': job.pk,
                    'form': form,
                    'requirements': requirements,
                }
                return render(request, 'frontend/update_job.html', args)
    else:
        form = JobForm(instance=job)
        requirements = RequirementsFormSet(instance=job)
        args = {
            'form': form,
            'requirements': requirements,
        }
        return render(request, 'frontend/update_job.html', args)


class ApplicantInfo(LoginRequiredMixin, View):

    def get(self, request, username, job_id, application_id):
        applicant = get_object_or_404(UserApplication, pk=application_id)
        matched_requirements = MatchedRequirement.objects.filter(application__pk=application_id)
        matched = [req for req in matched_requirements if req.matched]
        not_matched = [req for req in matched_requirements if not req.matched]
        skills = applicant.skills.split(',')
        education = applicant.education.split('\n')
        work_experience = applicant.work_experience.split('\n')
        cv = docx2txt.process(applicant.curriculum_vitae.file)
        lines = cv.replace('\n', '<br>')
        education_section = applicant.curriculum_vitae.education_section.split('\n')
        work_section = applicant.curriculum_vitae.work_experience_section.split('\n')
        skills_section = applicant.curriculum_vitae.skills_section.split('\n')
        args = {
            'lines': lines,
            'matched': matched,
            'not_matched': not_matched,
            'applicant': applicant,
            'skills': skills,
            'skills_section': skills_section,
            'education': education,
            'education_section': education_section,
            'work_experience': work_experience,
            'work_section': work_section
        }
        return render(request, 'frontend/applicant_info.html', args)


def get_posted_jobs(username):
    user = User.objects.get(username=username)
    return user.jobposting_set.all()


def count_requirements(matches):
    count = 0
    for key in matches:
        tmp = [match for match in matches[key] if match]
        count += len(tmp)
    return count


def skill_freq(applications):
    freq = {}
    for app in applications:
        skills = app.skills.split(',')
        for skill in skills:
            if skill in freq:
                freq[skill] += 1
            else:
                freq[skill] = 1
    return freq


def get_match_ratio(job_id):
    applications = UserApplication.objects.filter(job__pk=job_id)
    for application in applications:
        if not application.match_ratio:
            requirements = MatchedRequirement.objects.filter(application__pk=application.pk)
            true_matches = [req for req in requirements if req.matched]
            application.match_ratio = round(len(true_matches) / len(requirements) * 100, 2)
            application.save()
    return applications


def check_requirement_format(requirement):
    if ',' in requirement:
        tmp = requirement.split(',')
        if any(char.isdigit() for char in tmp[0]):
            return True
    return False


