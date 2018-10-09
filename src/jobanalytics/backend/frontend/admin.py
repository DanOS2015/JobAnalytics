from django.contrib import admin
from .models import JobPosting, UserApplication, Requirement, CVUpload, MatchedRequirement

admin.site.register(JobPosting)
admin.site.register(UserApplication)
admin.site.register(Requirement)
admin.site.register(CVUpload)
admin.site.register(MatchedRequirement)
