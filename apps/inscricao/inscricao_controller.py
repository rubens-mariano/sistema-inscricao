from django.db.models import Sum
from apps.inscricao.models import Aluno, OfertaDisciplina, Turma, SelecaoTemporaria, ListaEspera
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


def verifica_choque_horario(lista_turmas):
    """
    Função para verificar se há choque de horários entre as turmas.
    """

    choques = []
    lista_turmas = [get_turma(turma) for turma in lista_turmas]
    horarios = []
    dias_semana = []
    for turma in lista_turmas:
        horarios.append((turma.horario_inicial, turma.horario_final))
        dias_semana.append(turma.dia_semana)

    for i in range(len(horarios)):
        for j in range(i + 1, len(horarios)):
            if ((horarios[i][0] < horarios[j][1] and horarios[i][1] > horarios[j][0]) and
                    (dias_semana[i] == dias_semana[j])):
                choques.append((lista_turmas[i], lista_turmas[j]))
    return choques


def get_espera(aluno_id, turma):
    try:
        return ListaEspera.objects.get(aluno=aluno_id, turma=turma)
    except ListaEspera.DoesNotExist:
        return None


def get_lista_espera(aluno_id, lista_turmas):
    try:
        return ListaEspera.objects.filter(aluno=aluno_id, turma__in=lista_turmas)
    except ListaEspera.DoesNotExist:
        return None


def adicionar_lista_espera(aluno_id, lista_turmas):
    try:
        lista = ListaEspera.objects.all()
        ultima_posicao = 0
        em_espera = []

        if lista:
            ultima_posicao = lista.last().posicao

        for turma in lista_turmas:
            espera = get_espera(aluno_id, turma)
            if not espera:
                ListaEspera.objects.create(aluno=aluno_id, turma=turma,
                                           disciplina=turma.disciplina, posicao=ultima_posicao + 1)
            else:
                em_espera.append(turma)

        return em_espera

    except ListaEspera.DoesNotExist:
        raise ListaEspera.DoesNotExist


def inscrever(aluno, lista_turmas):
    """
    Função para inscrever o aluno nas turmas.
    """

    if aluno and lista_turmas:
        aluno.turmas.set(lista_turmas)

        disciplinas = [turma.disciplina for turma in lista_turmas]
        turmas_ofertadas = OfertaDisciplina.objects.filter(disciplina__in=disciplinas)

        for turma in turmas_ofertadas:
            turma.inscritos = turma.inscritos + 1
            turma.save()

        aluno.save()
        return True
    else:
        return False
