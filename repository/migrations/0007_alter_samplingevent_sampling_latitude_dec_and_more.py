# Generated by Django 4.2.1 on 2023-08-14 11:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0006_alter_individual_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="samplingevent",
            name="sampling_latitude_dec",
            field=models.DecimalField(decimal_places=8, max_digits=11, null=True),
        ),
        migrations.AlterField(
            model_name="samplingevent",
            name="sampling_longitude_dec",
            field=models.DecimalField(decimal_places=8, max_digits=11, null=True),
        ),
    ]
