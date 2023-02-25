# Generated by Django 4.1.5 on 2023-02-05 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0005_groupuserthru_enabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupuserthru',
            name='enabled',
        ),
        migrations.AddField(
            model_name='groupuserthru',
            name='status',
            field=models.CharField(choices=[('WA', 'Waiting for admins to OK'), ('AC', 'Active member'), ('BA', 'Banned')], default='WA', max_length=2),
        ),
    ]
