# Generated by Django 3.0.5 on 2020-05-07 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dm_demo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='new_relation_tab',
            fields=[
                ('a_id', models.AutoField(primary_key=True, serialize=False)),
                ('auth_id', models.IntegerField(default=0)),
                ('ach_id', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'new_relation_tab',
            },
        ),
    ]
