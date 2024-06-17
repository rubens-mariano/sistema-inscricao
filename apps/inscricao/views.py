from django.shortcuts import render, redirect
from django.contrib import messages

from apps.inscricao.forms import FormularioSelecaoDisciplina, FormularioSelecaoTurma, FormularioListaEspera
from apps.inscricao.models import SelecaoTemporaria, Aluno, ListaEspera, Disciplina
from apps.inscricao.inscricao_controller import (verifica_creditos, verifica_disponibilidade,
                                                 inscrever, get_inscricao_temporaria,
                                                 get_aluno, adicionar_lista_espera, verifica_choque_horario,
                                                 get_lista_espera)


def list_disciplinas_view(request):
    """
    View para listar disciplinas.
    """
    form = FormularioSelecaoDisciplina()

    if request.method == 'POST':
        form = FormularioSelecaoDisciplina(request.POST)
        aluno = get_aluno(1)
        inscricao_temporaria = SelecaoTemporaria.objects.create(aluno=aluno)

        if form.is_valid() and aluno is not None:
            disciplinas_cursadas = form.cleaned_data['disciplinas']
            inscricao_temporaria.disciplinas.set(disciplinas_cursadas)

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
        return redirect('disciplinas')

    lista_disciplinas = inscricao_temporaria.disciplinas.values_list('id', flat=True)
    form = FormularioSelecaoTurma(disciplinas=lista_disciplinas)

    if request.method == 'POST':
        form = FormularioSelecaoTurma(request.POST, disciplinas=lista_disciplinas)

        if form.is_valid():
            turmas = form.cleaned_data['turmas']
            inscricao_temporaria.turmas.set(turmas)
            lista_turmas = inscricao_temporaria.turmas.values_list('id', flat=True)

            lista_turmas_indisponiveis = verifica_disponibilidade(lista_turmas)
            if len(lista_turmas_indisponiveis) > 0:
                messages.error(request, 'Não há disponibilidade em uma das disciplinas')
                lista_turmas_indisponiveis_ids = [turma.id for turma in lista_turmas_indisponiveis]
                form_lista_espera = FormularioListaEspera(request, lista_turmas=lista_turmas_indisponiveis_ids)
                return render(request, 'inscricao/selecionar-turma.html',
                              {'form': form, 'form_lista_espera': form_lista_espera,
                               'lista_turmas_indisponiveis': lista_turmas_indisponiveis})

            if not verifica_creditos(aluno_id, lista_turmas):
                messages.error(request, 'Ultrapassou a quantidade de créditos disponíveis')
                return redirect('turmas')

            choques = verifica_choque_horario(lista_turmas)
            if len(choques):
                messages.error(request, 'Há choque de horário entre as turmas selecionadas')
                return redirect('turmas')

            inscricao_temporaria.save()

            return redirect('revisar_inscricao')

    return render(request, 'inscricao/selecionar-turma.html',
                  {'form': form, 'lista_turmas_indisponiveis': lista_turmas_indisponiveis})


def revisar_inscricao_view(request):
    """
    View para revisar inscrições.
    """

    aluno = get_aluno(1)
    inscricao_temporaria = get_inscricao_temporaria(aluno)

    if inscricao_temporaria is None:
        messages.error(request, 'Nenhuma inscrição temporária encontrada')
        return redirect('disciplinas')

    if inscricao_temporaria is None or inscricao_temporaria.is_expired():
        lista_turmas = []
    else:
        lista_turmas = inscricao_temporaria.turmas.all()
        lista_espera = get_lista_espera(aluno, lista_turmas).values('turma__codigo')
        if lista_espera:
            lista_turmas = [turma for turma in lista_turmas if turma.codigo not in lista_espera[0]['turma__codigo']]

    if len(lista_turmas) > 0:

        if request.method == 'POST':
            if inscricao_temporaria is not None:
                inscrever(aluno, lista_turmas)
                inscricao_temporaria.delete()
            return redirect('pagamento')
    else:
        return redirect('disciplinas')

    return render(request, 'inscricao/confirmacao.html', {'turmas': lista_turmas})


def adicionar_lista_espera_view(request):
    aluno = get_aluno(1)
    if request.method == 'POST':
        lista_espera = request.POST.getlist('lista_espera')
        form = FormularioListaEspera(request.POST, lista_turmas=lista_espera)

        if form.is_valid():
            lista_espera = form.cleaned_data['lista_espera']
            lista_turma_ja_adicionadas = adicionar_lista_espera(aluno, lista_espera)

            if len(lista_turma_ja_adicionadas) > 0:
                for turma in lista_turma_ja_adicionadas:
                    messages.error(request, f'A turma {turma.codigo} - {turma.nome} '
                                            f'já está adicionada na lista de espera')

                return redirect('turmas')

            return redirect('revisar_inscricao')

        messages.error(request, 'Você não selecionou nenhuma turma para adicionar a fila de espera')
        return redirect('turmas')


def pagamento(request):
    return render(request, 'inscricao/redirect-pagamento.html')
