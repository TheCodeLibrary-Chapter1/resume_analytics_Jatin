# # from rest_framework import filters
# from django_filters import rest_framework as filters
#
#
# class ResumeFilter(filters.FilterSet):
#     """
#     Filter is used in Post
#     """
#     file_to_process = filters.CharFilter()
#     job_desc_name = filters.CharFilter()
#     job_desc_id = filters.CharFilter()
#     profile_loc = filters.CharFilter()
#
#     class Meta:
#         """
#         Meta class
#         """
#         # model = Achievement
#         fields = ('job_desc_name', 'job_desc_id')
#
#     def filter_queryset(self, queryset):
#         """
#         Filter  queryset for customise filters
#         :param queryset:
#         :return: queryset
#         """
#         return queryset