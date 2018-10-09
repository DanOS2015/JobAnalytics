from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^login/$', views.login_page, name='login_page'),
    url(r'^cv_format/$', views.cv_format, name='cv_format'),
    url(r'^job_board/$', views.JobBoard.as_view(), name='job_board'),
    url(r'^data_report/', views.data_report, name='data_report'),
    url(r'^user_dashboard/(?P<username>\w+)/$', views.user_dashboard, name='user_dashboard'),
    url(r'^add_job/$', views.AddJob.as_view(), name='add_job'),
    url(r'^job_board/(?P<job_id>[0-9]+)/$', views.job_info, name='job_info'),
    url(r'^(?P<job_id>[0-9]+)/cv_upload/$', views.cv_upload, name='cv_upload'),
    url(r'^(?P<job_id>[0-9]+)/(?P<cv_id>[0-9]+)/application/$', views.job_application, name='job_application'),
    url(r'^(?P<job_id>[0-9]+)/(?P<cv_id>[0-9]+)/applicant/$', views.applicant_form, name='applicant_form'),
    url(r'^user_dashboard/(?P<username>\w+)/(?P<job_id>[0-9]+)/$', views.applicants_list, name='applicants_list'),
    url(
        r'^user_dashboard/(?P<username>\w+)/(?P<job_id>[0-9]+)/(?P<application_id>[0-9]+)/$',
        views.ApplicantInfo.as_view(),
        name='applicant_info'
    ),
    url(r'^delete_user_check/(?P<username>\w+)/$', views.delete_user_check, name="delete_user_check"),
    url(r'^delete_user/(?P<user_id>[0-9]+)/$', views.delete_user, name="delete_user"),
    url(r'^delete_job/(?P<job_id>[0-9]+)/$', views.delete_job, name="delete_job"),
    url(r'^delete_job_check/(?P<job_id>[0-9]+)/$', views.delete_job_check, name="delete_job_check"),
    url(r'^delete_applicant_check/(?P<application_id>[0-9]+)/$', views.delete_applicant_check, name="delete_applicant_check"),
    url(r'^delete_applicant/(?P<application_id>[0-9]+)/$', views.delete_applicant, name="delete_applicant"),
    url(r'^update_job/(?P<job_id>[0-9]+)/$', views.update_job, name="update_job"),
    url(r'^(?P<username>\w+)/previous_posts/$', views.previous_posts, name="previous_posts"),
    url(r'^([?P<employer>\w ]+)/add_job/$', views.add_job_with_previous, name="add_job_with_previous"),
    url(r'^api/chart/data/freq_skills/$', views.FrequentSkillsData.as_view(), name="chart_data_freq_skills"),
    url(r'^api/chart/data/match_ratio/$', views.MatchRatioData.as_view(), name="chart_data_match_ratio"),
    url(r'^api/chart/data/work_ethic/$', views.WorkEthicData.as_view(), name="chart_data_work_ethic"),
]
