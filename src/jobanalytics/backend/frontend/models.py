import os
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from tinymce.models import HTMLField
from django.core.validators import RegexValidator


class JobPosting(models.Model):
    user = models.ForeignKey(User, default=1)
    job_title = models.CharField(max_length=500)
    employer = models.CharField(max_length=500)

    # employer address
    address_line_1 = models.CharField(max_length=1024)
    address_line_2 = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField("City/Town", max_length=1024)
    county = models.CharField(max_length=1024)

    employer_logo = models.FileField(
        upload_to='logos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])],
        default='logos/default.png'
    )
    job_description = HTMLField()

    def __str__(self):
        return self.job_title + ' posted by ' + self.employer


class Requirement(models.Model):
    job = models.ForeignKey(JobPosting, default=1)
    requirement_detail = models.CharField(max_length=150)
    REQUIREMENT_TYPE = (
        ('0', 'Skill Requirement'),
        ('1', 'Experience Requirement'),
        ('2', 'Education Requirement'),
    )
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPE, default=0)
    requirement_keyword = models.CharField(max_length=50)

    def __str__(self):
        return self.requirement_keyword + " requirement for " + self.job.job_title + " job"


class CVUpload(models.Model):
    file = models.FileField(storage=FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'cvs')),
                                        validators=[FileExtensionValidator(allowed_extensions=['docx'])])
    education_section = models.TextField()
    work_experience_section = models.TextField()
    skills_section = models.TextField()

    def __str__(self):
        return self.file.name


class UserApplication(models.Model):
    job = models.ForeignKey(JobPosting, default=1)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=70)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    curriculum_vitae = models.ForeignKey(CVUpload, default=1)
    education = models.TextField()
    work_experience = models.TextField()
    skills = models.TextField()

    # questions for dataset
    AVERAGE_SALARY = (
        ('low', 'Less than or equal to 30,000 annually'),
        ('medium', 'Between 30,000 and 40,000 annually'),
        ('high', 'More than 40,000 annually'),
    )
    WORK_ACCIDENT = (
        ('1', 'Yes'),
        ('0', 'No'),
    )
    PROMOTION_IN_LAST_5_YEARS = (
        ('1', 'Yes'),
        ('0', 'No'),
    )
    satisfaction_level = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    number_of_projects = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    average_salary = models.CharField(max_length=50, choices=AVERAGE_SALARY, default='medium')
    work_accident = models.CharField(max_length=10, choices=WORK_ACCIDENT, default='0')
    promotion_in_last_5_years = models.CharField(max_length=10, choices=PROMOTION_IN_LAST_5_YEARS, default='0')
    average_monthly_hours = models.IntegerField()
    time_spent_at_company = models.IntegerField()
    performance = models.CharField(max_length=50)
    match_ratio = models.FloatField(null=True, default=0)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' user application for ' + self.job.job_title


class MatchedRequirement(models.Model):
    application = models.ForeignKey(UserApplication, default=1, related_name='application')
    requirement = models.ForeignKey(Requirement, default=1, related_name='requirement')
    matched = models.BooleanField(default=False)

    @classmethod
    def create(cls, app, req, match):
        return cls(application = app, requirement = req, matched = match)

    def __str__(self):
        return self.application.first_name + ' ' + self.application.last_name + "'s match for requirement: " + self.requirement.requirement_detail
