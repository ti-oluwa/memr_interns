# Generated by Django 5.1.5 on 2025-01-20 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interns', '0003_alter_internship_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internship',
            name='date_of_birth',
        ),
    ]
