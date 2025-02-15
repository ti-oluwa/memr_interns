# Generated by Django 5.1.5 on 2025-02-06 20:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interns', '0005_alter_internship_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internship',
            name='duration',
        ),
        migrations.AlterField(
            model_name='internship',
            name='department',
            field=models.CharField(choices=[('oil_and_gas', 'Oil and Gas Department'), ('solid_minerals', 'Solid Minerals Department'), ('geological_services', 'Geological Services Department'), ('power', 'Power Department'), ('procurement', 'Procurement Department'), ('admin_hr', 'Admin and HR'), ('accounts', 'Accounts Department'), ('public_relations', 'Public Relations Unit'), ('ps_office', "Permanent Secretary's Office"), ('dredging_unit', 'Dredging Unit')], db_index=True, max_length=120),
        ),
        migrations.AlterField(
            model_name='internship',
            name='end_date',
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
