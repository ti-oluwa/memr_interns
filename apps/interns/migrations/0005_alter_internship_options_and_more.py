# Generated by Django 5.1.5 on 2025-01-20 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interns', '0004_remove_internship_date_of_birth'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='internship',
            options={'ordering': ['start_date'], 'verbose_name': 'Internship', 'verbose_name_plural': 'Internships'},
        ),
        migrations.RemoveField(
            model_name='internship',
            name='date_joined',
        ),
    ]
