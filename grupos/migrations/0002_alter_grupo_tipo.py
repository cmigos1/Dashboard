# Generated by Django 5.2 on 2025-04-13 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grupo',
            name='tipo',
            field=models.CharField(choices=[('idoso', 'Idoso'), ('risco', 'Grupo de Risco'), ('crianca', 'Criança'), ('gestante', 'Gestante'), ('tea', 'Transtorno do Espectro Autista')], max_length=20),
        ),
    ]
