# Generated by Django 5.0.6 on 2024-05-30 02:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_rename_ultima_revalorizacion_inventario_precio_diario_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventario',
            old_name='precio_diario',
            new_name='precio_unitario_diario',
        ),
    ]
