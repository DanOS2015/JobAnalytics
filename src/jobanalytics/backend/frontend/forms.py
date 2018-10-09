from django import forms
from django.forms import inlineformset_factory
from .models import JobPosting, UserApplication, Requirement, CVUpload


class JobForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ["job_title", "employer", "address_line_1", "address_line_2", "city", "county", "employer_logo", "job_description"]


class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        exclude = ()


RequirementFormSet = inlineformset_factory(JobPosting, Requirement, form=RequirementForm, extra=1)


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = UserApplication
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone_number": "Phone number",
            "curriculum_vitae": "Please upload your CV (NOTE: Please upload file as a word document (.docx))",
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = UserApplication
        fields = [
            "satisfaction_level",
            "number_of_projects",
            "average_salary",
            "work_accident",
            "promotion_in_last_5_years",
            "average_monthly_hours",
            "time_spent_at_company"
        ]
        labels = {
            "satisfaction_level": "On a scale of 1 - 10 how satisfied were you in your previous job?",
            "number_of_projects": "How many projects did you work on in your previous job?",
            "average_salary": "In your most recent job, how much were you earning?",
            "work_accident": "Have you ever had a work accident or injury?",
            "promotion_in_last_5_years": "Have you acquired a promotion in the last 5 years in any of your jobs?",
            "average_monthly_hours": "How many hours did you work monthly in your previous job?",
            "time_spent_at_company": "How long did you work for your last job?",
        }


class CVUploadForm(forms.ModelForm):
    class Meta:
        model = CVUpload
        fields = ['file']