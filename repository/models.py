from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from pathlib import Path
from shortuuid.django_fields import ShortUUIDField


def DECIMAL_MEASUREMENT_ATTRIBUTE(min=0, max=999):
    return models.DecimalField(
        default=None,
        decimal_places=2,
        max_digits=5,
        null=True,
        blank=True,
        validators=[MaxValueValidator(max), MinValueValidator(min)],
    )


def DECIMAL_COORDINATE_ATTRIBUTE():
    return models.DecimalField(
        decimal_places=8,
        max_digits=12,
        validators=[MaxValueValidator(180), MinValueValidator(-180)],
        null=True)


class Instrument(models.Model):
    platform = models.CharField(max_length=200)
    model = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.platform} {self.model}"


class Organism(models.Model):
    scientific_name = models.CharField(max_length=200, unique=True)
    common_name = models.CharField(max_length=200)
    is_hybrid = models.BooleanField(default=False, blank=True, null=True)
    tax_id = models.IntegerField(default=0)

    @property
    def shortened_genus(self):
        genus, epithet = self.scientific_name.split(" ", 1)
        return f"{genus[0]}. {epithet}"

    def __str__(self):
        return f"{self.common_name} ({self.scientific_name})"


class Age(models.Model):
    label = models.CharField(max_length=4, null="True", blank=True)
    value = models.IntegerField(default=0, null=True, blank=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.label} {self.value}"


class SampleSex(models.Model):
    name = models.CharField(max_length=200)
    gonosomes = models.CharField(max_length=2)
    ontology_term = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.gonosomes})"


class Color(models.Model):
    label = models.CharField(max_length=32)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.label} ({self.description})"


class Person(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    initials = models.CharField(max_length=32, unique=True)
    affiliation = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.initials})"


class ExternalCollection(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    contact_person = models.ForeignKey(Person, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.name} ({self.description})"


class Country(models.Model):
    name = models.CharField(max_length=200)
    label_short = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.name} ({self.label_short})"


class TissuePreservative(models.Model):
    label = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.label} ({self.description})"


class Tissue(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"


class ExternalAccession(models.Model):
    class ExternalArchive(models.TextChoices):
        NCBI_SRA = "NCBI_SRA", "SRA"
        ENA = "ENA", "ENA"
        BIOSTUDIES = "ENA_BIOSTUDIES", "BIOSTUDIES"

    accession_no = models.CharField(max_length=32)
    archive = models.CharField(max_length=16, choices=ExternalArchive.choices)


class Individual(models.Model):
    name_validator = RegexValidator(
        r"[A-Za-z0-9_-]+",
        "Name must only contain letters, numbers, hyphens, and underscores.",
    )

    name = models.CharField(
        max_length=200,
        editable=True,
        unique=True,
        primary_key=True,
        validators=[name_validator],
    )
    name_short = models.CharField(max_length=8, null=True, blank=True, unique=True)
    title = models.CharField(max_length=200, default="", null=True, blank=True)
    registration_date = models.DateField(
        "registration_date", auto_now_add=True, blank=True
    )
    organism = models.ForeignKey(Organism, on_delete=models.PROTECT, blank=True)
    sex = models.ForeignKey(SampleSex, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    individual_number_DOE = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("repository:individual", args=[str(self.name)])


class SamplingEvent(models.Model):
    class Age(models.TextChoices):
        ONEYEAR = "1cy", "1CY"
        ONEYEARPLUS = "1cy+", "1CY+"
        TWOYEAR = "2cy", "2CY"
        TWOYEARPLUS = "2cy+", "2CY+"

    id = ShortUUIDField(
        length=8,
        max_length=12,
        prefix="SE_",
        alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        primary_key=True,
        editable=False,
    )

    individual = models.ForeignKey(
        Individual,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name="sampling_event",
    )
    sampling_date = models.DateField("collection_date", null=True, blank=True)
    sampling_time = models.CharField(max_length=32, null=True, blank=True)

    sampling_location = models.CharField(max_length=200, null=True, blank=True)
    sampling_country = models.ForeignKey(
        Country, on_delete=models.PROTECT, null=True, blank=True
    )
    sampling_latitude = models.CharField(max_length=200, null=True, blank=True)
    sampling_longitude = models.CharField(max_length=200, null=True, blank=True)
    sampling_longitude_dec = DECIMAL_COORDINATE_ATTRIBUTE()
    sampling_latitude_dec = DECIMAL_COORDINATE_ATTRIBUTE()

    age_at_sampling = models.CharField(
        max_length=4, choices=Age.choices, null="True", blank=True
    )

    ringer_name = models.ManyToManyField(Person, blank=True)

    colorring_combination_left = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    colorring_combination_right = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    throat_phenotype = models.ForeignKey(
        Color, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    back_color_score = models.ForeignKey(
        Color, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    neck_color_score = models.ForeignKey(
        Color, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    forehead_length = DECIMAL_MEASUREMENT_ATTRIBUTE()
    bill_length = DECIMAL_MEASUREMENT_ATTRIBUTE(min=10, max=25)
    black_above_eye = DECIMAL_MEASUREMENT_ATTRIBUTE(min=0, max=5)
    length_third_primary = DECIMAL_MEASUREMENT_ATTRIBUTE(min=55, max=100)
    wing_length = DECIMAL_MEASUREMENT_ATTRIBUTE(min=70, max=120)
    tarsus_length = DECIMAL_MEASUREMENT_ATTRIBUTE(min=10, max=40)
    body_mass = DECIMAL_MEASUREMENT_ATTRIBUTE(min=5, max=40)

    projection_first_primary_over_primary_coverts = models.CharField(
        max_length=32, default=None, null=True, blank=True
    )
    picture_ids = models.TextField(default=None, null=True, blank=True)
    attributes = models.JSONField(default=dict, null=True, blank=True)
    ring_number = models.CharField(max_length=128, default=None, null=True, blank=True)
    logger_id = models.CharField(max_length=200, default=None, null=True, blank=True)

    comment = models.TextField(default=None, null=True, blank=True)

    @property
    def label(self):
        return f"{self.individual} sampled on {self.sampling_date}"

    def __str__(self):
        return self.label


class BioSample(models.Model):
    id = ShortUUIDField(
        length=8,
        max_length=12,
        prefix="SAM_",
        alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        primary_key=True,
        editable=False,
    )

    sampling_event = models.ForeignKey(
        SamplingEvent,
        on_delete=models.PROTECT,
        null=False,
        blank=True,
        related_name="biosample",
    )
    tissue_type = models.ForeignKey(
        Tissue, on_delete=models.PROTECT, null=True, blank=True
    )
    preservative = models.ManyToManyField(TissuePreservative, blank=True)
    tissue_sample_box = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    tissue_sample_tube = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    attributes = models.JSONField(default=dict, null=True, blank=True)
    external_sample_id = models.CharField(
        max_length=200, default=None, null=True, blank=True
    )
    external_collection_name = models.ForeignKey(
        ExternalCollection, on_delete=models.PROTECT, null=True, blank=True
    )
    related_sample = models.ManyToManyField("self", blank=True)

    @property
    def label(self):
        return f"{self.tissue_type} from {self.sampling_event.sampling_date}"

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("repository:sample", args=[str(self.id)])


class Measurement(models.Model):
    class NumericMeasurementTypes(models.TextChoices):
        BILL_LENGTH = "bill_length"
        BLACK_ABOVE_EYE = "black_above_eye"
        LENGTH_THIRD_PRIMARY = "length_third_primary"
        WING_LENGTH = "wing_length"
        TARSUS_LENGTH = "tarsus_length"
        BODY_MASS = "body_mass"

    date = models.DateField("collection_date", null=True, blank=True)
    time = models.CharField(max_length=32, null=True, blank=True)
    measurement = models.CharField(
        max_length=32, choices=NumericMeasurementTypes.choices
    )
    value = DECIMAL_MEASUREMENT_ATTRIBUTE()
    # individual = models.ForeignKey(Sample, on_delete=models.PROTECT)


class Experiment(models.Model):
    class LibrarySelection(models.TextChoices):
        """
        LibrarySelection terms matching the ENA vocabulary. Not all terms listed here.
        For convenience copied from:
        https://github.com/usegalaxy-eu/ena-upload-cli/blob/master/ena_upload/templates/ENA_template_LIBRARY_SELECTION.xml
        """

        RANDOM = "RANDOM", "RANDOM"
        PCR = "PCR", "PCR"
        RANDOM_PCR = "RANDOM_PCR"
        UNSPECIFIED = "unspecified"
        REDUCED_REPRESENTATION = "Reduced Representation"
        RESTRICTION_DIGEST = "Restriction Digest"
        POLY_A = "PolyA"
        OTHER = "other"

    class LibraryLayout(models.TextChoices):
        PAIRED = "PAIRED"
        SINGLE = "SINGLE"

    class LibrarySource(models.TextChoices):
        """LibraySource terms matching the ENA vocabulary.
        Copied from
        https://github.com/usegalaxy-eu/ena-upload-cli/blob/master/ena_upload/templates/ENA_template_LIBRARY_SOURCE.xml
        """

        GENOMIC = "GENOMIC"
        TRANSCRIPTOMIC = "TRANSCRIPTOMIC"
        OTHER = "OTHER"

    class LibraryStrategy(models.TextChoices):
        """
        LibraryStrategy terms matching the ENA vocabulary. Not all terms listed here.
        For convienience copied from
        https://github.com/usegalaxy-eu/ena-upload-cli/blob/master/ena_upload/templates/ENA_template_LIBRARY_STRATEGY.xml
        """

        WGS = "WGS", "WGS"
        WGA = "WGA", "WGA"
        WXS = "WXS", "WXS"
        RNA_SEQ = "RNA-Seq", "RNA-Seq"
        HI_C = "Hi-C"
        ATAC_SEQ = "ATAC-Seq", "ATAC-Seq"
        RAD_SEQ = "RAD-Seq", "RAD-Seq"
        BISULFITE_SEQ = "Bisulfite-Seq"
        EM_SEQ = "EM-Seq", "EM-Seq"
        OTHER = "other"

    id = ShortUUIDField(
        length=8,
        max_length=12,
        prefix="EXP_",
        alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        primary_key=True,
        editable=False,
    )
    title = models.CharField(max_length=200)
    sample = models.ForeignKey(
        BioSample, on_delete=models.PROTECT, related_name="experiment"
    )
    library_strategy = models.CharField(max_length=28, choices=LibraryStrategy.choices)
    library_layout = models.CharField(max_length=28, choices=LibraryLayout.choices)
    library_selection = models.CharField(
        max_length=28, choices=LibrarySelection.choices
    )
    library_source = models.CharField(max_length=28, choices=LibrarySource.choices)
    instrument_model = models.ForeignKey(Instrument, on_delete=models.PROTECT)
    design_description = models.CharField(max_length=200)
    exp_attributes = models.JSONField(default=dict, null=True, blank=True)
    external_accession = models.ManyToManyField(ExternalAccession, blank=True)

    def __str__(self):
        return f"{self.id} for {self.sample} ({self.title}) "

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("repository:experiment", args=[str(self.id)])


class SequencingRun(models.Model):
    id = ShortUUIDField(
        length=8,
        max_length=12,
        prefix="RUN_",
        alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        primary_key=True,
        editable=False,
    )

    label = models.CharField(max_length=200)
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id} "


class File(models.Model):
    class HostName(models.TextChoices):
        EVE = "EVE", "EVE (UFZ, iDiv)"
        EULER = "EULER", "Euler (ETH Zürich)"
        UPPMAX = "UPPMAX", "UPPMAX (Uppsala)"

    class FileType(models.TextChoices):
        FASTQ = "fastq", "FASTQ"
        BAM = "bam", "BAM"
        VCF = "vcf", "VCF"
        UNSPECIFIED = "unspecified", "unspecified"

    id = ShortUUIDField(
        length=8,
        max_length=13,
        prefix="FILE_",
        alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        primary_key=True,
        editable=False,
    )

    filepath = models.CharField(max_length=300, unique=True)
    checksum = models.CharField(max_length=200, unique=True)
    checksum_type = models.CharField(max_length=200, choices=[("md5", "md5")])
    host = models.CharField(
        max_length=28, choices=HostName.choices, default=HostName.EULER
    )
    filetype = models.CharField(
        max_length=16, choices=FileType.choices, default=FileType.FASTQ
    )
    experiment = models.ForeignKey(
        Experiment, on_delete=models.PROTECT, related_name="file"
    )
    # run = models.ForeignKey(
    #     SequencingRun, on_delete=models.CASCADE, null=True, blank=True
    # )

    @property
    def filename(self):
        return f"{Path(self.filepath).name}"

    def __str__(self):
        return f"{self.filename} ({self.filetype})"
