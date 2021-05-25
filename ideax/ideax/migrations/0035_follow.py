# Generated by Django 2.0.9 on 2019-07-31 19:15
 
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_authconfiguration'),
        ('ideax', '0034_comment_edited'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('idea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ideax.Idea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UserProfile')),
            ],
        ),
    ]