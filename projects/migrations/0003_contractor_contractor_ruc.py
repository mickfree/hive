# Generated by Django 5.0.6 on 2024-06-02 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_contractor_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractor',
            name='contractor_ruc',
            field=models.CharField(default=666, max_length=20),
            preserve_default=False,
        ),
    ]
