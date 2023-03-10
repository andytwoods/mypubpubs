# Generated by Django 4.1.5 on 2023-02-05 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0006_remove_groupuserthru_enabled_groupuserthru_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.TextField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='safe_domains',
            field=models.ManyToManyField(to='group.domainnames'),
        ),
    ]