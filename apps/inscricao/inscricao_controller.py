from django.db.models import Sum
from apps.inscricao.models import Aluno, OfertaDisciplina, Turma, SelecaoTemporaria
from django.core.exceptions import ObjectDoesNotExist


def get_aluno(aluno_id):
    """
    Retorna uma instância de Aluno para o dado aluno_id.

    :param aluno_id: O ID do aluno.
    :return: Uma instância de Aluno se o aluno for encontrado.
             None se nenhum aluno for encontrado.
    """

    try:
        return Aluno.objects.get(id=aluno_id)
    except Aluno.DoesNotExist:
        return None


def get_inscricao_temporaria(aluno_id):
    """
    Retorna a última inscrição temporária de um aluno.

    :param aluno_id: O ID do aluno.
    :return: Uma instância de SelecaoTemporaria para o dado aluno_id.
             None se nenhum registro de SelecaoTemporaria for encontrado.
    """

    try:
        return SelecaoTemporaria.objects.filter(aluno=aluno_id).last()
    except ObjectDoesNotExist:
        return None


def get_turma(turma_id):
    """
    Função para recuperar a turma através do id.
    """
    try:
        return Turma.objects.get(id=turma_id)
    except Turma.DoesNotExist:
        print("Turma não encontrada")
        return None


def get_oferta_disciplina(turma):
    """
    Função para recuperar a oferta de disciplina da turma.
    """
    try:
        return OfertaDisciplina.objects.filter(disciplina=turma.disciplina).first()
    except OfertaDisciplina.DoesNotExist:
        print("Oferta de disciplina não encontrada")
        return None


def get_total_consumo_creditos(lista_turmas):
    """
    Função para obter o consumo total de créditos.
    """
    return Turma.objects.filter(disciplina__in=lista_turmas).aggregate(
        total_consumo_creditos=Sum('disciplina__credito'))


def tem_vagas_disponiveis(oferta_disciplina):
    """
    Função para verificar se ainda há vagas disponíveis em uma oferta de disciplina.
    """
    return oferta_disciplina.vagas > oferta_disciplina.inscritos


def verifica_disponibilidade(lista_turmas):
    """
    Função para verificar a disponibilidade das turmas.
    """
    lista_turmas_indisponiveis = []

    for turma_id in lista_turmas:
        turma = get_turma(turma_id)
        oferta_disciplina = get_oferta_disciplina(turma)
        if oferta_disciplina and not tem_vagas_disponiveis(oferta_disciplina):
            lista_turmas_indisponiveis.append(turma)

    return lista_turmas_indisponiveis


def verifica_creditos(aluno_id, lista_turmas):
    """
    Função para verificar os créditos do aluno.
    """
    aluno = get_aluno(aluno_id)
    turmas = get_total_consumo_creditos(lista_turmas)

    if aluno and turmas:
        total_consumo_creditos = turmas['total_consumo_creditos'] or 0
        return (aluno.creditos - total_consumo_creditos) >= 0
    return False


def inscrever(aluno_id, lista_turmas):
    """
    Função para inscrever o aluno nas turmas.
    """
    inscricao_temporaria = SelecaoTemporaria.objects.filter(aluno=aluno_id).last()
    aluno = get_aluno(aluno_id)

    if aluno and inscricao_temporaria:
        aluno.turmas.set(inscricao_temporaria.turmas.all())

        disciplinas = [turma.disciplina for turma in lista_turmas]
        turmas_ofertadas = OfertaDisciplina.objects.filter(disciplina__in=disciplinas)

        for turma in turmas_ofertadas:
            turma.inscritos = turma.inscritos + 1
            turma.save()

        aluno.save()
    else:
        print('Não foi possível inscrever o aluno. Verifique a inscrição temporária e os dados do aluno.')