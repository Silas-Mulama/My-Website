# Generated by Django 5.0.6 on 2024-07-31 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(default='avatar.svg', null=True),
        ),
    ]
