from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import random
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Disciplina(models.Model):
    codigo = models.CharField(max_length=10, null=False, blank=False)
    nome = models.CharField(max_length=200, null=False, blank=False)
    pre_requisito = models.ManyToManyField('self', symmetrical=False, related_name='requisitada_por', blank=True)
    credito = models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(0)]
    )
    ano = models.IntegerField(null=False, blank=False, default=timezone.now().year)

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class Sala(models.Model):
    numero = models.CharField(max_length=20, null=False, blank=False)
    capacidade = models.IntegerField()

    def __str__(self):
        return f'{self.numero}, {self.capacidade}'


class OfertaDisciplina(models.Model):
    disciplina = models.ForeignKey(to=Disciplina, on_delete=models.CASCADE, null=False, blank=False)
    vagas = models.IntegerField(
        null=False,
        blank=False,
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(40)]
    )
    inscritos = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.disciplina.nome}, {self.vagas}'


class Turma(models.Model):
    DIAS_DA_SEMANA = [
        ('SEGUNDA', 'Segunda-Feira'),
        ('TERÇA', 'Terça-Feira'),
        ('QUARTA', 'Quarta-Feira'),
        ('QUINTA', 'Quinta-Feira'),
        ('SEXTA', 'Sexta-Feira'),
        ('SÁBADO', 'Sábado'),
        ('DOMINGO', 'Domingo'),
    ]

    codigo = models.CharField(max_length=10, null=False, blank=False)
    nome = models.CharField(max_length=200, null=False, blank=False)
    disciplina = models.ForeignKey(to=Disciplina, on_delete=models.CASCADE, null=False, blank=False)
    professor = models.CharField(max_length=250, null=False, blank=False)
    dia_semana = models.CharField(max_length=150, choices=DIAS_DA_SEMANA, default='')
    horario_inicial = models.TimeField(null=False, blank=False)
    horario_final = models.TimeField(null=False, blank=False)
    sala = models.ForeignKey(to=Sala, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return f'{self.codigo}, {self.nome}, {self.disciplina}'


class Aluno(models.Model):
    matricula = models.CharField(max_length=20, unique=True, null=False, blank=False)
    nome = models.CharField(max_length=200, null=False, blank=False)
    creditos = models.IntegerField(
        null=False,
        blank=False,
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
    turmas = models.ManyToManyField(Turma, blank=True)
    disciplinas_cursadas = models.ManyToManyField(Disciplina, blank=True)

    def __str__(self):
        return f'{self.matricula}, {self.nome}'


class ListaEspera(models.Model):
    aluno = models.ForeignKey(to=Aluno, on_delete=models.CASCADE, null=False, blank=False)
    disciplina = models.ForeignKey(to=Disciplina, on_delete=models.CASCADE, null=False, blank=False)
    data = models.DateTimeField(auto_now=True)
    posicao = models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(0)]
    )
    turma = models.ForeignKey(to=Turma, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return f'{self.aluno.matricula}, {self.disciplina.nome}, {self.posicao}, {self.turma}'


class SelecaoTemporaria(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    disciplinas = models.ManyToManyField('Disciplina')
    turmas = models.ManyToManyField('Turma')
    criado_em = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.criado_em + timedelta(hours=1)

    @classmethod
    def clean_expired_selections(cls):
        expiration_time = timezone.now() - timedelta(minutes=2)
        expired_selections = SelecaoTemporaria.objects.filter(criado_em__lt=expiration_time)
        count = expired_selections.count()
        expired_selections.delete()
        print(f'{count} seleções temporárias expiradas foram removidas.')
