# Generated by Django 5.2 on 2025-04-13 18:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grupos', '0004_alter_grupo_tipo'),
        ('vacinas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacinacao',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacinacoes', to='grupos.pessoa'),
        ),
    ]
