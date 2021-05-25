# Generated by Django 2.0.1 on 2018-03-21 14:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ideax', '0005_category_discarded'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_comment', models.TextField(blank=True)),
                ('date', models.DateTimeField()),
                ('comment_phase', models.PositiveSmallIntegerField()),
                ('deleted', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('idea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ideax.Idea')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='ideax.Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]