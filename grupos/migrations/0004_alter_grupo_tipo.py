# Generated by Django 5.2 on 2025-04-13 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0003_alter_grupo_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupo',
            name='tipo',
            field=models.CharField(choices=[('idoso', 'Idoso'), ('risco', 'Grupo de Risco'), ('crianca', 'Criança')], max_length=20),
        ),
    ]
