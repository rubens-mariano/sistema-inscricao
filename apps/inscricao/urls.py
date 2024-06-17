from django.urls import path
from apps.inscricao import views

urlpatterns = [
    path('', views.list_disciplinas_view, name='disciplinas'),
    path('disciplinas/turmas/', views.list_turmas_disciplinas_view, name='turmas'),
    path('disciplinas/turmas/add-lista-espera/', views.adicionar_lista_espera_view, name='lista_de_espera'),
    path('disciplinas/turmas/revisao/', views.revisar_inscricao_view, name='revisar_inscricao'),
    path('pagamento/', views.pagamento, name='pagamento'),
]