from django.test import SimpleTestCase, TestCase, RequestFactory
from unittest.mock import MagicMock, patch
from ..models import JobPosting, CVUpload, UserApplication, Requirement
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import reverse
from django.test.client import Client
from ..views import AddJob
from django.core.files.uploadedfile import SimpleUploadedFile

class ViewTests(TestCase):

    def setUp(self):
        self.test_user1_credentials = {
            'username': 'testuser',
            'password': 'secret'
        }
        self.test_user = User.objects.create_user(**self.test_user1_credentials)
        self.test_user2_credentials = {
            'username': 'testuser2',
            'password': 'secret2'
        }
        self.test_user2 = User.objects.create_user(**self.test_user2_credentials)
        self.job_details = {
            'user': self.test_user,
            'job_title': 'Test Model Job',
            'employer': 'Model Test',
            'address_line_1': 'Test road',
            'address_line_2': 'Test road 2',
            'city': 'Test city',
            'county': 'Carlow',
            'job_description': 'Model test for JobPosting'
        }
        self.job = JobPosting.objects.create(**self.job_details)
        self.cv_upload_details = {
            'file': SimpleUploadedFile(
                name='SampleCV.docx',
                content=open('C:/Users/dan36/Desktop/2018-ca400-osulld42/src/CVParser/venv/SampleCV.docx', 'rb').read()),
            'education_section': '1900-2000 Test School',
            'work_experience_section': '1939-1945 Test Job, Army',
            'skills_section': 'Teamwork, Communication, Testing'
        }
        self.cv_upload = CVUpload.objects.create(**self.cv_upload_details)
        self.applicant_detials = {
            'job': self.job,
            'first_name': 'test',
            'last_name': 'user',
            'email': 'existing@email.com',
            'phone_number': '0871234567',
            'curriculum_vitae': self.cv_upload,
            'education': 'Education test section',
            'work_experience': 'Work experience test section',
            'skills': 'Skills test section',
            'satisfaction_level': 7,
            'number_of_projects': 3,
            'average_salary': 'Between 30,000 and 40,000 annually',
            'work_accident': 'No',
            'promotion_in_last_5_years': 'No',
            'average_monthly_hours': 250,
            'time_spent_at_company': 3,
            'performance': 'Satisfactory Worker',
            'match_ratio': 70.0,
        }
        self.applicant = UserApplication.objects.create(**self.applicant_detials)
        self.req_details1 = {
            'job': self.job,
            'requirement_detail': 'This is details for a test job requirement',
            'requirement_type': '0',
            'requirement_keyword': 'test',
        }
        self.requirement1 = Requirement.objects.create(**self.req_details1)
        self.req_details2 = {
            'job': self.job,
            'requirement_detail': 'This is details for a test job requirement',
            'requirement_type': '1',
            'requirement_keyword': '4, test',
        }
        self.requirement2 = Requirement.objects.create(**self.req_details2)
        self.req_details3 = {
            'job': self.job,
            'requirement_detail': 'This is details for a test job requirement',
            'requirement_type': '2',
            'requirement_keyword': '4, test',
        }
        self.requirement3 = Requirement.objects.create(**self.req_details3)

    def tearDown(self):
        Requirement.objects.all().delete()
        JobPosting.objects.all().delete()
        User.objects.all().delete()
        CVUpload.objects.all().delete()
        UserApplication.objects.all().delete()

    def test_index_view(self):
        url = reverse('index')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_register_view(self):
        url = reverse('register')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_login_page_view(self):
        url = reverse('login_page')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_logout_view(self):
        url = reverse('logout')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

    def test_job_board_view(self):
        url = reverse('job_board')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_job_board_view_query(self):
        url = reverse('job_board')
        resp = self.client.get(url, {'search': 'Test'})
        self.assertEquals(resp.status_code, 200)
        resp = self.client.get(url, {'search': 'Nothing'})
        self.assertEquals(resp.status_code, 200)

    def test_add_job(self):
        url = reverse('add_job')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_add_job_with_post(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('add_job')
        resp = self.client.post(url, data={
            'job_title': 'Test Model Job',
            'employer': 'Model Test',
            'address_line_1': 'Test road',
            'address_line_2': 'Test road 2',
            'city': 'Test city',
            'county': 'Carlow',
            'job_description': 'Model test for JobPosting',
            'requirement_set-TOTAL_FORMS': 1,
            'requirement_set-INITIAL_FORMS': 0,
            'requirement_set-0-requirement_detail': 'Test Requirement',
            'requirement_set-0-requirement_type': '0',
            'requirement_set-0-requirement_keyword': 'Test',
        })
        self.assertEquals(resp.status_code, 302)

    def test_cv_format(self):
        url = reverse('cv_format')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_data_report_with_redirect(self):
        url = reverse('data_report')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

    def test_data_report_with_access(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('data_report')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_previous_posts(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('previous_posts', args=['testuser'])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_previous_posts_with_redirect(self):
        user_login = self.client.login(username='testuser2', password='secret2')
        self.assertTrue(user_login)
        url = reverse('previous_posts', args=['testuser2'])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

    def test_add_job_with_previous_posts(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('add_job_with_previous', args=['Model Test'])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

    def test_user_dashboard_redirect_if_not_logged_in(self):
        url = reverse('user_dashboard', args=['testuser'])
        resp = self.client.get(url)
        self.assertRedirects(resp, '/login/?next=/user_dashboard/testuser/')

    def test_login_with_valid_data(self):
        response = self.client.post('/login/', self.test_user1_credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)

    def test_login_with_invalid_data(self):
        response = self.client.post('/login/', {
            'username': 'doesnt_exist',
            'password': 'not_gonna_work',
        }, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_registration(self):
        resp = self.client.post('/register/', {
            'username': 'test',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertEquals(resp.status_code, 302)

    def test_registration_with_invalid_data(self):
        resp = self.client.post('/register/', {
            'username': 'test',
            'password1': 'password123',
        })
        self.assertTrue('error: true' in resp.content)

    def test_job_info(self):
        url = reverse('job_info', args=[self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_job_info_with_logged_in_user(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('job_info', args=[self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_cv_upload_view(self):
        url = reverse('cv_upload', args=[self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_cv_upload_post_with_valid_data(self):
        url = reverse('cv_upload', args=[self.job.pk])
        resp = self.client.post(url, {
            'file': SimpleUploadedFile(
                name='SampleCV.docx',
                content=open('C:/Users/dan36/Desktop/2018-ca400-osulld42/src/CVParser/venv/SampleCV.docx', 'rb').read())
        })
        self.assertEquals(resp.status_code, 302)

    def test_cv_upload_post_with_invalid_data1(self):
        url = reverse('cv_upload', args=[self.job.pk])
        resp = self.client.post(url, {})
        self.assertEquals(resp.status_code, 200)

    def test_cv_upload_post_with_invalid_data2(self):
        url = reverse('cv_upload', args=[self.job.pk])
        resp = self.client.post(url, {
            'file': SimpleUploadedFile(
                name='SampleCV.docx',
                content=open('C:/Users/dan36/Desktop/2018-ca400-osulld42/src/CVParser/venv/Cover Letter.docx', 'rb').read())
        })
        self.assertEquals(resp.status_code, 200)

    def test_applicant_form_view(self):
        url = reverse('applicant_form', args=[self.job.pk, self.cv_upload.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_applicant_form_view_with_valid_data(self):
        url = reverse('applicant_form', args=[self.job.pk, self.cv_upload.pk])
        resp = self.client.post(url, {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'test@user.com',
            'phone_number': '0871234567'
        })
        self.assertEquals(resp.status_code, 302)

    def test_applicant_form_view_with_invalid_data(self):
        url = reverse('applicant_form', args=[self.job.pk, self.cv_upload.pk])
        resp = self.client.post(url, {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'test@user.com',
            'phone_number': '5'
        })
        self.assertEquals(resp.status_code, 200)

    def test_applicant_form_view_with_existing_applicant(self):
        url = reverse('applicant_form', args=[self.job.pk, self.cv_upload.pk])
        resp = self.client.post(url, {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'existing@email.com',
            'phone_number': '0871234567'
        })
        self.assertEquals(resp.status_code, 302)

    def test_application_form_view(self):
        url = reverse('cv_upload', args=[self.job.pk])
        resp = self.client.post(url, {
            'file': SimpleUploadedFile(
                name='SampleCV.docx',
                content=open('C:/Users/dan36/Desktop/2018-ca400-osulld42/src/CVParser/venv/SampleCV.docx', 'rb').read())
        })
        self.assertEquals(resp.status_code, 302)
        url1 = reverse('applicant_form', args=[self.job.pk, self.cv_upload.pk])
        resp1 = self.client.post(url1, {
            'first_name': 'test',
            'last_name': 'user',
            'email': 'test@user.com',
            'phone_number': '0871234567'
        })
        self.assertEquals(resp1.status_code, 302)
        url2 = reverse('job_application', args=[self.job.pk, self.cv_upload.pk])
        resp2 = self.client.post(url2, {
            "satisfaction_level": 1,
            "number_of_projects": 2,
            "average_salary": "low",
            "work_accident": "0",
            "promotion_in_last_5_years": "0",
            "average_monthly_hours": 250,
            "time_spent_at_company": 2,
        })
        self.assertEquals(resp2.status_code, 302)

    def test_applicant_list_view_with_redirect(self):
        url = reverse('applicants_list', args=[self.test_user.username, self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 302)

    def test_applicant_list_view_with_login(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('applicants_list', args=[self.test_user.username, self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_update_job_view(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('update_job', args=[self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_update_job_form(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('update_job', args=[self.job.pk])
        resp = self.client.post(url, {
            'job_title': 'Test Model Job',
            'employer': 'Model Test',
            'address_line_1': 'Test road',
            'address_line_2': 'Test road 2',
            'city': 'Test city',
            'county': 'Carlow',
            'job_description': 'Model test for JobPosting',
            'requirement_set-TOTAL_FORMS': 1,
            'requirement_set-INITIAL_FORMS': 0,
            'requirement_set-0-requirement_detail': 'Test Requirement',
            'requirement_set-0-requirement_type': '0',
            'requirement_set-0-requirement_keyword': 'Test',
        })
        self.assertEquals(resp.status_code, 302)

    def test_applicant_info_view(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('applicant_info', args=[self.test_user.username, self.job.pk, self.applicant.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_delete_job_view(self):
        user_login = self.client.login(username='testuser', password='secret')
        self.assertTrue(user_login)
        url = reverse('delete_job_check', args=[self.job.pk])
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)







