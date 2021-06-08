# Generated by Django 3.1.7 on 2021-06-07 04:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service_auth', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseprogress',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='service_auth.student'),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(to='service_auth.Student'),
        ),
        migrations.AddField(
            model_name='answer',
            name='cases',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.test'),
        ),
    ]
