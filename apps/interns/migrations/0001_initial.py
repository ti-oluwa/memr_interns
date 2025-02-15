# Generated by Django 5.1.5 on 2025-01-17 07:34

import django.db.models.deletion
import uuid_extensions.uuid7
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Intern',
            fields=[
                ('id', models.UUIDField(default=uuid_extensions.uuid7, editable=False, primary_key=True, serialize=False)),
                ('internship_type', models.CharField(choices=[('industrial_training', 'Industrial Training'), ('nysc', 'NYSC'), ('volunteering', 'Volunteering')], db_index=True, max_length=120)),
                ('department', models.CharField(db_index=True, max_length=120)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('internship_start_date', models.DateField(db_index=True)),
                ('internship_end_date', models.DateField(blank=True, db_index=True, null=True)),
                ('internship_duration', models.DurationField(db_index=True)),
                ('date_joined', models.DateField(auto_now_add=True, db_index=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='internships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Intern',
                'verbose_name_plural': 'Interns',
                'ordering': ['-date_joined'],
            },
        ),
    ]
