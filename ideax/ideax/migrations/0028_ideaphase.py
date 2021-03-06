# Generated by Django 2.0.9 on 2019-02-01 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ideax', '0027_auto_20190124_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='IdeaPhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, max_length=500, null=True)),
                ('order', models.PositiveSmallIntegerField(default=False)),
            ],
            options={
                'verbose_name': 'Idea Phase',
            },
        ),
    ]
