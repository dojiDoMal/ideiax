# Generated by Django 2.0.9 on 2019-04-22 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ideax', '0029_auto_20190201_1946'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dimension',
            old_name='final_date',
            new_name='last_update',
        ),
        migrations.AddField(
            model_name='category_dimension',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='dimension',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='dimension',
            name='init_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
