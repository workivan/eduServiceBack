# Generated by Django 3.1.12 on 2021-06-24 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_auth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='position',
        ),
        migrations.AddField(
            model_name='student',
            name='place',
            field=models.TextField(default='empty', verbose_name='Место работы'),
        ),
        migrations.AlterField(
            model_name='student',
            name='job',
            field=models.TextField(default='empty', verbose_name='Должность'),
        ),
    ]
