# Generated by Django 3.1.7 on 2021-03-10 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userApp', '0007_goal_is_personal_goal'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goal',
            old_name='user',
            new_name='created_by',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='is_personal_goal',
        ),
    ]