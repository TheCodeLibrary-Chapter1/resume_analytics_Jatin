from django.urls import path
from api import views
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'resume_analysis', views.AnalyseResume, basename='resume_analysis')

urlpatterns = [
    path('', include(router.urls)),
    # path('', views.CheckIndexApi.as_view()),
    # path('resume_analysis/', views.AnalyseResume.as_view()),
    # path('resume_tool/', views.GetResumeSummary.as_view())
]