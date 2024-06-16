from django.contrib import admin
from apps.inscricao.models import Disciplina, Aluno, ListaEspera, OfertaDisciplina, Sala, Turma, SelecaoTemporaria

# Register your models here.
admin.site.register(Disciplina)
admin.site.register(Aluno)
admin.site.register(ListaEspera)
admin.site.register(OfertaDisciplina)
admin.site.register(Sala)
admin.site.register(Turma)
admin.site.register(SelecaoTemporaria)
