from django import forms
from apps.inscricao.models import Disciplina, Turma, Aluno, SelecaoTemporaria


class FormularioSelecaoDisciplina(forms.Form):
    disciplinas = forms.ModelMultipleChoiceField(
        queryset=Disciplina.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check',
            }
        )
    )


class FormularioSelecaoTurma(forms.Form):
    def __init__(self, *args, **kwargs):
        disciplinas = kwargs.pop('disciplinas', None)
        super(FormularioSelecaoTurma, self).__init__(*args, **kwargs)

        if disciplinas:
            self.fields['turmas'].queryset = Turma.objects.all().exclude(disciplina__in=disciplinas)

    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check',
            }
        )
    )


class FormularioListaEspera(forms.Form):
    def __init__(self, *args, **kwargs):
        lista_turmas = kwargs.pop('lista_turmas', None)
        super(FormularioListaEspera, self).__init__(*args, **kwargs)

        if lista_turmas:
            self.fields['lista_espera'].queryset = Turma.objects.filter(id__in=lista_turmas)

    lista_espera = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check',
            }
        )
    )
