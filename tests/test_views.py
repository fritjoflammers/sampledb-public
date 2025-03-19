import pytest

from repository.views import SampleView
from django.urls import reverse
from django.test import RequestFactory


@pytest.mark.django_db  #
def test_sampleview():
    path = reverse("index")
    request = RequestFactory().get(path)  # get the path for the list of contacts
    response = SampleView(request)

    # assert status code from requesting the view
    # is 200(OK success status response code)
    assert response.status_code == 200
