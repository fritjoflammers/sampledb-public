# Generated by Django 4.2.1 on 2023-07-06 12:50

from django.db import migrations
import shortuuid.django_fields


class Migration(migrations.Migration):
    dependencies = [
        ("repository", "0004_alter_samplingevent_ring_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="id",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet="ABZDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                editable=False,
                length=8,
                max_length=13,
                prefix="FILE_",
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
