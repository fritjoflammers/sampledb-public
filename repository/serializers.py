from rest_framework import serializers
from .models import BioSample, Experiment, File, Individual, SamplingEvent

class ExperimentSerializer(serializers.HyperlinkedModelSerializer):
    #    file = FileSerializer()
    class Meta:
        model = Experiment
        fields = ["id", "title", "library_strategy"]


class SampleSerializer(serializers.ModelSerializer):
    # experiment = ExperimentSerializer()
    # experiment = serializers.StringRelatedField(many=True, read_only=True)
    experiment = serializers.CharField()

    class Meta:
        model = BioSample
        fields = ["id", "tissue_type", "experiment"]


class SamplingEventSerializer(serializers.ModelSerializer):
    biosample = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = SamplingEvent
        fields = ("id", "sampling_date", "sampling_location", "biosample")


class IndividualSerializer(serializers.ModelSerializer):
    sampling_event = SamplingEventSerializer()

    class Meta:
        model = Individual
        fields = ["name", "title", "sampling_event"]


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ["filename"]