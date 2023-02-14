# Generated by Django 3.2.9 on 2023-02-12 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('city', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('country_code_iso2', models.CharField(max_length=7)),
                ('country_code_iso3', models.CharField(max_length=7)),
                ('state', models.CharField(max_length=50)),
            ],
            options={
                'unique_together': {('city', 'country', 'state')},
            },
        ),
    ]
