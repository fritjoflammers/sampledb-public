from django.urls import path, include, re_path
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import routers, serializers, viewsets

from .models import BioSample, Experiment, File, Individual, SamplingEvent
from .serializers import IndividualSerializer, SampleSerializer, FileSerializer, SamplingEventSerializer, ExperimentSerializer
from . import views

app_name = "repository"




# ViewSets define the view behavior.
class IndividualViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class BioSampleViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = BioSample.objects.all()
    serializer_class = SampleSerializer


class FileViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer


class SamplingEventViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = SamplingEvent.objects.all()
    serializer_class = SamplingEventSerializer


class ExperimentViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"individual", IndividualViewSet)
router.register(r"sample", BioSampleViewSet)
router.register(r"sampling_events", SamplingEventViewSet)
router.register(r"experiment", ExperimentViewSet)
router.register(r"file", FileViewSet)


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("get_started", views.GettingStartedView.as_view(), name="get_started"),

    path("individuals/", views.IndividualListView.as_view(), name="individual_list"),
    path("samples/", views.SampleListView.as_view(), name="samples_list"),
    path("experiments/", views.ExperimentListView.as_view(), name="experiments_list"),
    path("files/", views.FileListView.as_view(), name="files_list"),
    path("experiment/<slug:id>/", views.ExperimentView.as_view(), name="experiment"),
    path("file/<str:pk>/", views.FileView.as_view(), name="file"),
    path("sample/<str:pk>/", views.SampleView.as_view(), name="sample"),
    re_path(
        "individual/(?P<name>[A-Za-z-0-9_]+)/",
        views.IndividualView.as_view(),
        name="individual",
    ),
    path("sample/<str:sample_id>/modify", views.modify_sample, name="modify_sample"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
