# Generated by Django 3.1.7 on 2021-06-07 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210607_0455'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='number',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='answer',
            name='cases',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='answers', to='core.test'),
        ),
    ]