from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django_filters import rest_framework as filters


from .models import BioSample, File, Experiment, Individual
from .filters import ExperimentFilter, IndividualFilter
from .tables import ExperimentTable, IndividualTable


from typing import Any, List


class IndexView(LoginRequiredMixin, TemplateView):
    """
    View for the index page.
    """

    template_name = "repository/index.html"


class GettingStartedView(LoginRequiredMixin, TemplateView):
    """
    View for the index page.
    """

    template_name = "repository/get_started.html"


class SampleListView(LoginRequiredMixin, ListView):
    """
    View for listing all samples.
    """

    template_name = "repository/list_samples.html"
    context_object_name = "all_samples_list"

    def get_queryset(self) -> List[Any]:
        """Return all samples ordered by sampling event."""
        return BioSample.objects.order_by("sampling_event")


class IndividualListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """
    View for listing all individuals.
    """

    template_name = "repository/list_individuals.html"
    context_object_name = "all_individuals_list"


    model = Individual
    table_class = IndividualTable

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IndividualFilter

    def get_queryset(self) -> List[Any]:
        """Return all individuals."""
        return Individual.objects.all()


class ExperimentListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """
    View for listing all experiments.
    """

    template_name = "repository/list_experiments.html"
    context_object_name = "all_experiments_list"

    model = Experiment
    table_class = ExperimentTable

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ExperimentFilter

    def get_queryset(self) -> List[Any]:
        """Return all experiments."""
        return Experiment.objects.all()


class FileListView(LoginRequiredMixin, ListView):
    """
    View for listing all files.
    """

    template_name = "repository/list_files.html"
    context_object_name = "all_files_list"

    def get_queryset(self) -> List[Any]:
        """Return all files."""
        return File.objects.all()


class SampleView(LoginRequiredMixin, DetailView):
    """
    View for displaying a sample.
    """

    model = BioSample
    template_name = "repository/sample.html"


class IndividualView(LoginRequiredMixin, View):
    """
    View for displaying an individual.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for individual view.

        Args:
            request: The HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HTTP response with the rendered individual template.
        """
        # Get the arbitrary string from the URL parameters
        name = kwargs.get("name")
        individual = get_object_or_404(Individual, name=name)

        return render(request, "repository/individual.html", {"individual": individual})


class ExperimentView(LoginRequiredMixin, View):
    """
    View for displaying an experiment.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for experiment view.

        Args:
            request: The HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HTTP response with the rendered experiment template.
        """
        # Get the arbitrary string from the URL parameters
        id = kwargs.get("id")

        experiment = get_object_or_404(Experiment, id=id)
        return render(request, "repository/experiment.html", {"experiment": experiment})


class FileView(LoginRequiredMixin, View):
    """
    View for displaying a file.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for file view.

        Args:
            request: The HTTP request.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HTTP response with the rendered file template.
        """
        # Get the arbitrary string from the URL parameters
        id = kwargs.get("id")

        file = get_object_or_404(File, id=id)
        return render(request, "repository/file.html", {"file": file})


def modify_sample(request, sample_id):
    sample = get_object_or_404(BioSample, pk=sample_id)
    print(sample)
    try:
        sample.title = request.POST["sample_title"]
    except (KeyError, BioSample.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "repository/sample.html",
            {
                "Sample": sample,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        sample.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(
            reverse("repository:modify_sample", args=(sample_id,))
        )
