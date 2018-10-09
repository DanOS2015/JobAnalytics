from django.contrib.auth.models import User
from django.test import TestCase
from ..models import JobPosting, Requirement, UserApplication, CVUpload, MatchedRequirement
from django.core.files.uploadedfile import SimpleUploadedFile


class ModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='test_user',
            password='test',
        )

        cls.job = JobPosting.objects.create(
            job_title='Test Model Job',
            employer='Model Test',
            address_line_1='Test road',
            address_line_2='Test road 2',
            city='Test city',
            county='Carlow',
            job_description='Model test for JobPosting'
        )

        cls.requirement = Requirement.objects.create(
            requirement_detail='Test for requirement model',
            requirement_type='Skill Requirement',
            requirement_keyword='Test'
        )

        cls.cv = CVUpload.objects.create(
            file=SimpleUploadedFile(
                name='SampleCV.docx',
                content=open('C:/Users/dan36/Desktop/2018-ca400-osulld42/src/CVParser/venv/SampleCV.docx', 'rb').read()),
            education_section='1900-2000 Test School',
            work_experience_section='1939-1945 Test Job, Army',
            skills_section='Teamwork, Communication, Testing',
        )

        cls.application = UserApplication.objects.create(
            first_name='Test',
            last_name='Applicant',
            email='test@applicant.com',
            phone_number='+353871234567',
            education='Education test section',
            work_experience='Work experience test section',
            skills='Skills test section',
            satisfaction_level=7,
            number_of_projects=3,
            average_salary='Between 30,000 and 40,000 annually',
            work_accident='No',
            promotion_in_last_5_years='No',
            average_monthly_hours=250,
            time_spent_at_company=3,
            performance='Satisfactory Worker',
            match_ratio=70.0,
        )

        cls.matched_requirement = MatchedRequirement.objects.create(
            matched=False
        )

    def tearDown(self):
        User.objects.all().delete()
        JobPosting.objects.all().delete()
        Requirement.objects.all().delete()
        CVUpload.objects.all().delete()
        UserApplication.objects.all().delete()
        MatchedRequirement.objects.all().delete()

    # jobposting tests
    def test_job_title(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('job_title').verbose_name
        self.assertEquals(field_label, 'job title')

    def test_employer(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('employer').verbose_name
        self.assertEquals(field_label, 'employer')

    def test_address_line_1(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('address_line_1').verbose_name
        self.assertEquals(field_label, 'address line 1')

    def test_address_line_2(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('address_line_2').verbose_name
        self.assertEquals(field_label, 'address line 2')

    def test_city(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('city').verbose_name
        self.assertEquals(field_label, 'City/Town')

    def test_county(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('county').verbose_name
        self.assertEquals(field_label, 'county')

    def test_employer_logo(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('employer_logo').verbose_name
        self.assertEquals(field_label, 'employer logo')

    def test_job_description(self):
        job = JobPosting.objects.get(id=1)
        field_label = job._meta.get_field('job_description').verbose_name
        self.assertEquals(field_label, 'job description')

    def test_jobposting_str(self):
        job = JobPosting.objects.get(id=1)
        expected_name = '%s posted by %s' % (job.job_title, job.employer)
        self.assertEquals(expected_name, str(job))

    def test_jobposting_valid_creation(self):
        self.assertTrue(JobPosting.objects.create(
            job_title='Creation test',
            employer='Creation company',
            address_line_1='Creation road',
            city='Creation city',
            county='Antrim',
            employer_logo='default.png',
            job_description='This job post was created for a test.'
        ))

    # requirement tests
    def test_requirement_detail(self):
        requirement = Requirement.objects.get(id=1)
        field_label = requirement._meta.get_field('requirement_detail').verbose_name
        self.assertEquals(field_label, 'requirement detail')

    def test_requirement_type(self):
        requirement = Requirement.objects.get(id=1)
        field_label = requirement._meta.get_field('requirement_type').verbose_name
        self.assertEquals(field_label, 'requirement type')

    def test_requirement_keyword(self):
        requirement = Requirement.objects.get(id=1)
        field_label = requirement._meta.get_field('requirement_keyword').verbose_name
        self.assertEquals(field_label, 'requirement keyword')

    def test_requirement_str(self):
        requirement = Requirement.objects.get(id=1)
        expected_name = '%s requirement for %s job' % (requirement.requirement_keyword, requirement.job.job_title)
        self.assertEquals(expected_name, str(requirement))

    # userapplication tests

    def test_first_name(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_email(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('email').verbose_name
        self.assertEquals(field_label, 'email')

    def test_phone_number(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('phone_number').verbose_name
        self.assertEquals(field_label, 'phone number')

    def test_education(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('education').verbose_name
        self.assertEquals(field_label, 'education')

    def test_work_experience(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('work_experience').verbose_name
        self.assertEquals(field_label, 'work experience')

    def test_skills(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('skills').verbose_name
        self.assertEquals(field_label, 'skills')

    def test_satisfaction_level(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('satisfaction_level').verbose_name
        self.assertEquals(field_label, 'satisfaction level')

    def test_number_of_projects(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('number_of_projects').verbose_name
        self.assertEquals(field_label, 'number of projects')

    def test_average_salary(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('average_salary').verbose_name
        self.assertEquals(field_label, 'average salary')

    def test_work_accident(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('work_accident').verbose_name
        self.assertEquals(field_label, 'work accident')

    def test_promotion_in_last_5_years(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('promotion_in_last_5_years').verbose_name
        self.assertEquals(field_label, 'promotion in last 5 years')

    def test_average_monthly_hours(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('average_monthly_hours').verbose_name
        self.assertEquals(field_label, 'average monthly hours')

    def test_time_spent_at_company(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('time_spent_at_company').verbose_name
        self.assertEquals(field_label, 'time spent at company')

    def test_performance(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('performance').verbose_name
        self.assertEquals(field_label, 'performance')

    def test_match_ratio(self):
        application = UserApplication.objects.get(id=1)
        field_label = application._meta.get_field('match_ratio').verbose_name
        self.assertEquals(field_label, 'match ratio')

    def test_userapplication_str(self):
        application = UserApplication.objects.get(id=1)
        expected_name = '%s %s user application for %s' % (application.first_name, application.last_name, application.job.job_title)
        self.assertEquals(expected_name, str(application))

    # matchedrequirement tests
    def test_match(self):
        matched_requirement = MatchedRequirement.objects.get(id=1)
        field_label = matched_requirement._meta.get_field('matched').verbose_name
        self.assertEquals(field_label, 'matched')


    # cvupload tests
    def test_file_field(self):
        cvupload = CVUpload.objects.get(id=1)
        field_label = cvupload._meta.get_field('file').verbose_name
        self.assertEquals(field_label, 'file')

    def test_education_section(self):
        cvupload = CVUpload.objects.get(id=1)
        field_label = cvupload._meta.get_field('education_section').verbose_name
        self.assertEquals(field_label, 'education section')

    def test_work_experience_section(self):
        cvupload = CVUpload.objects.get(id=1)
        field_label = cvupload._meta.get_field('skills_section').verbose_name
        self.assertEquals(field_label, 'skills section')

    def test_cvupload_str(self):
        cvupload = CVUpload.objects.get(id=1)
        expected_name = cvupload.file.name
        self.assertEquals(expected_name, str(cvupload))


















