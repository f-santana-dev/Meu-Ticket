
# urls.py

from django.urls import path
from . import views  # Supondo que todas as views estejam no mesmo módulo `views`
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    # Outras rotas
    path('', views.login_view, name='login'),  # Página de login
    path('homepage/', views.homepage, name='homepage'),  # Página inicial após login
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('demanda/<int:id_demanda>/', views.historico_demanda, name='historico_demanda'),
    path('filtrar_demandas/', views.filtrar_demandas, name='filtrar_demandas'),
    path('demanda/<int:demanda_id>/enviar_mensagem/', views.enviar_mensagem, name='enviar_mensagem'),
    path('cadastrar_nova_demanda/', views.cadastrar_nova_demanda, name='cadastrar_nova_demanda'),
    path('fechar_demanda/<int:demanda_id>/', views.fechar_demanda, name='fechar_demanda'),
    path('dashboard-suporte/', views.dashboard_suporte, name='dashboard_suporte'),
    path('demanda/<int:demanda_id>/iniciar_atendimento/', views.iniciar_atendimento, name='iniciar_atendimento'),
    path('demanda/<int:demanda_id>/reabrir/', views.reabrir_demanda, name='reabrir_demanda'),
 

    # URLs do relatório
    path('relatorio/', views.relatorio, name='relatorio'),  # Página principal do relatório
    path('relatorio/preview/', views.relatorio_preview_view, name='relatorio_preview'),  # Pré-visualização do relatório    
    path('gerar_pdf/', views.gerar_pdf, name='gerar_pdf'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
