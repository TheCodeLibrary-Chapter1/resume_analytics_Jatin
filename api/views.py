from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.generic.base import View
from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from api.serializers import UserSerializer, GroupSerializer, ResumeSerializer
from rest_framework.parsers import MultiPartParser

from api.resume_parser import parse_resume


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CheckIndexApi(APIView):
    """ Check if everything working fine """
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """ Dummy get function """
        return JsonResponse({'status': status.HTTP_200_OK, 'message': 'All okay'})

    def post(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        content_type = file_uploaded.content_type
        response = "POST API and you have uploaded a {} file".format(content_type)
        return Response(response)


class AnalyseResume(CreateModelMixin, viewsets.GenericViewSet):
    """ Uploads a resume file and returns the appropriate response after analysing it """
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser]

    status_flag = None
    message = None
    data = None
    response_data = dict()
    file_path = None

    def create(self, request, *args, **kwargs):
        """ Process a resume file and returns the keywords found in json response """
        try:
            data = request.data
            if request.FILES['file_to_process']:
                file_to_process = request.FILES['file_to_process']

                fs = FileSystemStorage()
                filename = fs.save(file_to_process.name, file_to_process)
                self.data = parse_resume(
                     filename,
                     job_desc_name=data.get('job_desc_name'),
                     job_desc_id=data.get('job_desc_id'),
                     comp_id=data.get('comp_id'),
                     created_by=data.get('created_by'),
                     profile_loc=data.get('profile_loc')
                 )
                self.file_path = fs.url(filename)
                self.status_flag = status.HTTP_200_OK
                self.message = 'File processed'

        except Exception as err_except:
            self.status_flag = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.message = str(err_except)
        self.response_data['status'] = self.status_flag
        self.response_data['message'] = self.message
        self.response_data['file_path'] = self.file_path
        self.response_data['data'] = self.data
        return JsonResponse(self.response_data)


class GetResumeSummary(View):
    """ Loads the resume upload form """

    def get(self, request):
        """ Loads the form to upload a resume file and get file summary """
        return render(request, 'resume_parser.html')