# Generated by Django 4.1.5 on 2023-02-04 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='groupuserthru',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='groupadminthru',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.group'),
        ),
        migrations.AddField(
            model_name='groupadminthru',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='group',
            name='admins',
            field=models.ManyToManyField(related_name='admins', through='group.GroupAdminThru', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='members', through='group.GroupUserThru', to=settings.AUTH_USER_MODEL),
        ),
    ]
