from django import forms
from apps.inscricao.models import Disciplina, Turma, Aluno, SelecaoTemporaria


class FormularioSelecaoDisciplina(forms.Form):
    def __init__(self, *args, **kwargs):
        aluno_id = kwargs.pop('aluno_id', None)
        super(FormularioSelecaoDisciplina, self).__init__(*args, **kwargs)

        if aluno_id:
            aluno = Aluno.objects.get(id=aluno_id)
            disciplinas_cursadas = aluno.disciplinas_cursadas.all()
            self.fields['disciplinas'].queryset = Disciplina.objects.exclude(id__in=disciplinas_cursadas)

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
        aluno_id = kwargs.pop('aluno_id', None)
        disciplinas = kwargs.pop('disciplinas', None)
        super(FormularioSelecaoTurma, self).__init__(*args, **kwargs)

        if aluno_id:
            aluno = Aluno.objects.get(id=aluno_id)
            disciplinas_cursadas = aluno.disciplinas_cursadas.all()
            self.fields['turmas'].queryset = Turma.objects.filter(disciplina__in=disciplinas).exclude(
                disciplina__in=disciplinas_cursadas)

    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'form-check',
            }
        )
    )
