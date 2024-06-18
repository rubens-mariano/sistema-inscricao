from django.test import TestCase
from datetime import time
from apps.inscricao.inscricao_controller import verifica_creditos, verifica_disponibilidade
from apps.inscricao.models import Aluno, Disciplina, Turma, Sala, OfertaDisciplina


class InscricaoTest(TestCase):
    def setUp(self):
        self._aluno_jon = Aluno.objects.create(matricula='BP3030199', nome="John Doe", creditos=20)

        self._disciplina_qsw = Disciplina.objects.create(nome="Qualidade de Software", credito=10, codigo='QSW',
                                                         ano=2024)
        self._disciplina_mtf = Disciplina.objects.create(nome="Matemática Financeiras", credito=10, codigo='MTF',
                                                         ano=2024)
        self._disciplina_esw = Disciplina.objects.create(nome="Engenharia de Software", credito=10, codigo='ESW',
                                                         ano=2024)
        self._sala = Sala.objects.create(numero='101', capacidade=40)

        self._turma_qsw = Turma.objects.create(disciplina=self._disciplina_qsw, horario_inicial=time(8, 0),
                                               horario_final=time(10, 0),
                                               codigo='QSW1', dia_semana='QUARTA', professor='Willson Vendramel',
                                               nome='Qualidade de Software 1', sala=self._sala)

        self._turma_mtf = Turma.objects.create(disciplina=self._disciplina_mtf, horario_inicial=time(8, 0),
                                               horario_final=time(10, 0),
                                               codigo='MTF', dia_semana='QUINTA', professor='Maria Lourdes',
                                               nome='Matemática Financeira 1', sala=self._sala)

        self._turma_esw = Turma.objects.create(disciplina=self._disciplina_esw, horario_inicial=time(8, 0),
                                               horario_final=time(10, 0),
                                               codigo='ESW', dia_semana='SEXTA', professor='Julio Ferraz',
                                               nome='Engenharia de Software 1', sala=self._sala)

        self.oferta_qsw = OfertaDisciplina.objects.create(disciplina=self._disciplina_qsw, inscritos=10, vagas=10)
        self.oferta_mtf = OfertaDisciplina.objects.create(disciplina=self._disciplina_mtf, inscritos=5, vagas=10)
        self.oferta_esw = OfertaDisciplina.objects.create(disciplina=self._disciplina_esw, inscritos=8, vagas=10)

    def test_valida_creditos_acima_do_limite_de_20_creditos_do_aluno(self):
        lista_turmas = [self._turma_qsw.id, self._turma_esw.id, self._turma_mtf.id]
        result = verifica_creditos(self._aluno_jon, lista_turmas)
        self.assertFalse(result)

    def test_valida_creditos_abaixo_do_limite_de_20_creditos_do_aluno(self):
        lista_turmas = [self._turma_qsw.id, self._turma_esw.id]
        result = verifica_creditos(self._aluno_jon, lista_turmas)
        self.assertTrue(result)

    def test_acima_do_limite_de_inscricao_disponivel(self):
        lista_turmas = [self._turma_qsw.id]
        result = verifica_disponibilidade(lista_turmas)
        self.assertListEqual(result, [self._turma_qsw])

    def test_abaixo_do_limite_de_inscricao_disponivel(self):
        lista_turmas = [self._turma_esw.id]
        result = verifica_disponibilidade(lista_turmas)
        self.assertListEqual(result, [])
