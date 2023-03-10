# Generated by Django 4.1.5 on 2023-02-11 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0009_domainnames_remove_groupuserthru_enabled_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='safe_domains',
            field=models.ManyToManyField(blank=True, to='group.domainnames'),
        ),
        migrations.AlterField(
            model_name='groupuserthru',
            name='status',
            field=models.CharField(choices=[('WA', 'Waiting for admins to OK'), ('AC', 'Active member'), ('BA', 'Banned'), ('DE', 'User declines membership')], default='WA', max_length=2),
        ),
    ]
