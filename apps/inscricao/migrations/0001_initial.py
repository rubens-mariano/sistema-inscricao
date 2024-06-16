# Generated by Django 5.0.6 on 2024-06-12 12:54

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=20, unique=True)),
                ('nome', models.CharField(max_length=200)),
                ('creditos', models.IntegerField(default=20, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)])),
            ],
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20)),
                ('capacidade', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10)),
                ('nome', models.CharField(max_length=200)),
                ('credito', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('pre_requisito', models.ManyToManyField(blank=True, related_name='requisitada_por', to='inscricao.disciplina')),
            ],
        ),
        migrations.CreateModel(
            name='OfertaDisciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vagas', models.IntegerField(default=40, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(40)])),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.disciplina')),
            ],
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10)),
                ('nome', models.CharField(max_length=200)),
                ('professor', models.CharField(max_length=250)),
                ('dia_semana', models.CharField(choices=[('SEGUNDA', 'Segunda-Feira'), ('TERÇA', 'Terça-Feira'), ('QUARTA', 'Quarta-Feira'), ('QUINTA', 'Quinta-Feira'), ('SEXTA', 'Sexta-Feira'), ('SÁBADO', 'Sábado'), ('DOMINGO', 'Domingo')], default='', max_length=150)),
                ('horario_inicial', models.TimeField()),
                ('horario_final', models.TimeField()),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.disciplina')),
                ('sala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.sala')),
            ],
        ),
        migrations.CreateModel(
            name='ListaEspera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now=True)),
                ('posicao', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.aluno')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.disciplina')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inscricao.turma')),
            ],
        ),
        migrations.AddField(
            model_name='aluno',
            name='turmas',
            field=models.ManyToManyField(blank=True, to='inscricao.turma'),
        ),
    ]
