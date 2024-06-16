from django.shortcuts import render, redirect
from django.contrib import messages

from apps.inscricao.forms import FormularioSelecaoDisciplina, FormularioSelecaoTurma
from apps.inscricao.models import SelecaoTemporaria, Aluno
from apps.inscricao.inscricao_controller import (verifica_creditos, verifica_disponibilidade,
                                                 inscrever, get_inscricao_temporaria, get_aluno)


def list_disciplinas_view(request):
    """
    View para listar disciplinas.
    """

    aluno_id = 1
    form = FormularioSelecaoDisciplina(aluno_id=aluno_id)

    if request.method == 'POST':
        form = FormularioSelecaoDisciplina(request.POST, aluno_id=aluno_id)
        aluno = get_aluno(aluno_id)

        if form.is_valid() and aluno is not None:
            disciplinas = form.cleaned_data['disciplinas']
            inscricao_temporaria = SelecaoTemporaria.objects.create(aluno=aluno)
            inscricao_temporaria.disciplinas.set(disciplinas)
            inscricao_temporaria.save()
            return redirect('turmas')

    return render(request, 'inscricao/disciplinas-completas.html', {'form': form})


def list_turmas_disciplinas_view(request):
    """
    View para listar turmas e disciplinas.
    """

    aluno_id = 1
    inscricao_temporaria = get_inscricao_temporaria(aluno_id)
    lista_turmas_indisponiveis = []

    if inscricao_temporaria is None:
        messages.error(request, 'Nenhuma inscrição temporária encontrada')
        return redirect('turmas')

    lista_disciplinas = inscricao_temporaria.disciplinas.values_list('id', flat=True)
    form = FormularioSelecaoTurma(aluno_id=aluno_id, disciplinas=lista_disciplinas)

    if request.method == 'POST':
        form = FormularioSelecaoTurma(request.POST, aluno_id=aluno_id, disciplinas=lista_disciplinas)

        if form.is_valid():
            turmas = form.cleaned_data['turmas']
            inscricao_temporaria.turmas.set(turmas)
            lista_turmas = inscricao_temporaria.turmas.values_list('id', flat=True)

            lista_turmas_indisponiveis = verifica_disponibilidade(lista_turmas)
            if len(lista_turmas_indisponiveis) > 0:
                messages.error(request, 'Não há disponibilidade em uma das disciplinas')
                return redirect('adicionar_lista_espera')

            if not verifica_creditos(aluno_id, lista_turmas):
                messages.error(request, 'Ultrapassou a quantidade de créditos disponíveis')
                return redirect('disciplinas')

            inscricao_temporaria.save()
            return redirect('revisar_inscricao')

    return render(request, 'inscricao/selecionar-turma.html', {'form': form})


def revisar_inscricao(request):
    """
    View para revisar inscrições.
    """

    aluno_id = 1
    inscricao_temporaria = get_inscricao_temporaria(aluno_id)

    if inscricao_temporaria is None or inscricao_temporaria.is_expired():
        lista_turmas = []
    else:
        lista_turmas = inscricao_temporaria.turmas.all()

    if len(lista_turmas) > 0:

        if request.method == 'POST':
            if inscricao_temporaria is not None:
                inscrever(aluno_id, lista_turmas)
                inscricao_temporaria.delete()
            return redirect('pagamento')
    else:
        return redirect('disciplinas')

    return render(request, 'inscricao/confirmacao.html', {'turmas': lista_turmas})


def adicionar_lista_espera(request):
    aluno_id = 1
    inscricao_temporaria = get_inscricao_temporaria(aluno_id)

    if inscricao_temporaria is None or inscricao_temporaria.is_expired():
        lista_turmas = []
    else:
        lista_turmas = inscricao_temporaria.turmas.all()

    lista_turmas_indisponiveis = verifica_disponibilidade(lista_turmas)

    if request.method == 'POST':
        if inscricao_temporaria is not None:
            print(lista_turmas_indisponiveis)
        return redirect('pagamento')

    return render(request, 'inscricao/confirmacao.html',
                  {'turmas': lista_turmas_indisponiveis})


def pagamento(request):
    return render(request, 'inscricao/redirect-pagamento.html')
