# Generated by Django 2.0.9 on 2019-02-01 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ideax', '0028_ideaphase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phase_history',
            name='current_phase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ideax.IdeaPhase'),
        ),
    ]
