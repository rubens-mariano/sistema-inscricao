from django.urls import path
from apps.inscricao import views

urlpatterns = [
    path('', views.list_disciplinas_view, name='disciplinas'),
    path('disciplinas/turmas/', views.list_turmas_disciplinas_view, name='turmas'),
    path('disciplinas/turmas/revisao/', views.revisar_inscricao, name='revisar_inscricao'),
    path('pagamento/', views.pagamento, name='pagamento'),
]