####################################views.py x#######################

from django.shortcuts import render, redirect,get_object_or_404
from django.core.mail import send_mail
from MeuTicket import settings
from .forms import  UsuarioForm,Nova_DemandaForm #, #DemandaForm,
from django.contrib import messages  # Import correto para as mensagens
import logging  # Adiciona o módulo de logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils import timezone  # Para lidar com datas
from .models import Area, Servico, Urgencia, Demanda,Mensagem, Usuario

from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO

from django.template.loader import get_template
from reportlab.lib.pagesizes import A4,letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from textwrap import wrap
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
#import pandas as pd
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
#from xhtml2pdf import pisa
from urllib.parse import urlencode  # Import para construir query strings
import os
from demanda.management_views import run_migrations




MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
def homepage(request):
     return render (request, 'base.html') 
 
 

 
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Autenticar o usuário com email e senha
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Verifica se o usuário tem perfil de operador ou suporte
            if user.perfil.tipo == 'operador':
                return redirect('homepage')  # Redireciona para a home se for operador
            elif user.perfil.tipo == 'suporte':
                return redirect('dashboard_suporte')  # Redireciona para o dashboard de suporte
        else:
            # Mensagem de erro se a autenticação falhar
            messages.error(request, "Email ou senha inválidos")

    return render(request, 'login.html')
 
 
 
 
 
# Configura o logger
logger = logging.getLogger(__name__)
@login_required(login_url='/login/')
# View responsável por exibir e processar o formulário de cadastro de usuário

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')  # Mensagem de sucesso
            logger.info('Usuário cadastrado com sucesso')
            return redirect('cadastrar_usuario')
        else:
            messages.error(request, 'Ocorreu um erro no cadastro. Verifique os dados informados.')  # Mensagem de erro
    else:
        form = UsuarioForm()

    return render(request, 'cadastro_usuario.html', {'form': form})


@login_required
def filtrar_demandas(request):
    # Obtemos os parâmetros de filtro da request
    titulo = request.GET.get('tituloDemanda', '')
    num_demanda = request.GET.get('numDemanda', '')
    status = request.GET.get('status', 'todos')

    # Construímos o queryset de acordo com os filtros
    queryset = Demanda.objects.all()

    if titulo:
        queryset = queryset.filter(titulo__icontains=titulo)
    
    if num_demanda:
        queryset = queryset.filter(id=num_demanda)
    
    if status != 'todos':
        queryset = queryset.filter(status=status.capitalize())

    # Passa os resultados filtrados para o template
    return render(request, 'filtros.html', {
        'demandas': queryset
    })
  
    
 
    
def cadastrar_nova_demanda(request):
    if request.method == 'POST':
        form = Nova_DemandaForm(request.POST, request.FILES)
        if form.is_valid():
            demanda = form.save(commit=False)
            if request.user.area:
                demanda.area = request.user.area
            else:
                messages.error(request, 'Usuário não tem área associada.')
                return render(request, 'cadastrar_nova_demanda.html', {
                    'form': form,
                })

            demanda.operador = request.user
            demanda.save()

            # Enviar e-mail para o usuário
            try:
                assunto = "Nova demanda cadastrada"
                mensagem = (
                    f"Olá, {request.user.nome}!\n\n"
                    f"Você cadastrou uma nova demanda no sistema com o ID {demanda.id}.\n\n"
                    "Detalhes da demanda:\n"
                    f"Título: {demanda.titulo}\n"
                    f"Área: {demanda.area}\n"
                    f"Status: {demanda.status}\n\n"
                    "Obrigado por utilizar o sistema MeuTicket!\n"
                )
                remetente = 'bragasan34@gmail.com'
                destinatario = [request.user.email]

                send_mail(assunto, mensagem, remetente, destinatario)
                messages.success(request, 'Demanda cadastrada com sucesso! E-mail enviado!')
            except Exception as e:
                messages.error(request, f'Erro ao enviar o e-mail: {str(e)}')

            return redirect('cadastrar_nova_demanda')
    else:
        form = Nova_DemandaForm()

    ultima_demanda = Demanda.objects.all().order_by('id').last()
    novo_id = ultima_demanda.id + 1 if ultima_demanda else 1

    return render(request, 'cadastrar_nova_demanda.html', {
        'form': form,
        'novo_id': novo_id,
        'messages': messages.get_messages(request),  # Adiciona mensagens ao contexto
    }) 


   
def historico_demanda(request, id_demanda):
    # Busca a demanda pelo ID ou retorna 404 se não for encontrada
    demanda = get_object_or_404(Demanda, id=id_demanda)
    
    # Renderiza o template ticket_template.html com os dados da demanda
    return render(request, 'ticket_template.html', {'demanda': demanda})



def enviar_mensagem(request, demanda_id):
    # Busca a demanda associada ao ID
    demanda = get_object_or_404(Demanda, id=demanda_id)

    if request.method == 'POST':
        # Obtém o texto da mensagem do formulário
        texto_mensagem = request.POST.get('mensagem')

        # Verifica se o campo da mensagem não está vazio
        if texto_mensagem:
            # Cria uma nova instância de Mensagem e salva no banco de dados
            nova_mensagem = Mensagem(
                demanda=demanda,
                autor=request.user,  # Quem está logado e enviando a mensagem
                texto=texto_mensagem,
                #data_envio=timezone.now()
                data_envio=now() 
            )
            nova_mensagem.save()

            try:
                # Obtém o operador (autor da demanda) para enviar o e-mail
                operador = demanda.operador
                assunto = f"Nova mensagem na demanda {demanda.titulo}"
                mensagem = (
                    f"Olá, {operador.nome}!\n\n"  # Usa o nome do operador
                    f"Você recebeu uma nova mensagem na sua demanda {demanda.titulo}.\n\n"
                    "Detalhes da demanda:\n"
                    f"Título: {demanda.titulo}\n"
                    f"Área: {demanda.area}\n"
                    f"Status: {demanda.status}\n\n"
                    "Obrigado por utilizar o sistema MeuTicket!\n"
                )
                remetente = 'bragasan34@gmail.com'
                destinatario = [operador.email]  # E-mail do operador da demanda

                send_mail(assunto, mensagem, remetente, destinatario)
                messages.success(request, 'Mensagem cadastrada com sucesso! E-mail enviado para o autor da demanda!')
            except Exception as e:
                messages.error(request, f'Erro ao enviar o e-mail: {str(e)}')
                
            
                       
            
            
            # Redireciona para a mesma página, mas usando o nome correto do argumento na URL
            return redirect('historico_demanda', id_demanda=demanda.id)

    # Se for uma requisição GET, apenas renderiza a página com a demanda
    return render(request, 'historico_demanda.html', {'demanda': demanda})



@login_required
def fechar_demanda(request, demanda_id):
    # Buscar a demanda pelo ID
    demanda = get_object_or_404(Demanda, id=demanda_id)
    
    # Verificar se o usuário é suporte
    if request.user.perfil.tipo == 'suporte':
        # Alterar o status da demanda e definir o realizador
        demanda.status = 'Fechado'
        demanda.realizador = request.user
        demanda.realizadoem = timezone.now()
        demanda.save()

        messages.success(request, 'Demanda finalizada com sucesso!')
    else:
        messages.error(request, 'Apenas usuários de suporte podem fechar demandas.')
    
    return redirect('historico_demanda', id_demanda=demanda.id)





def dashboard_suporte(request):
    if request.user.perfil.tipo == 'suporte':
        demandas_abertas = Demanda.objects.filter(status='Aberto', realizador__isnull=True)
        logger.info(f'Demandas em aberto: {demandas_abertas}')  # Verifica quais demandas estão sendo passadas
        return render(request, 'dashboard_suporte.html', {'demandas_abertas': demandas_abertas})
    
    return redirect('home')


@login_required
def iniciar_atendimento(request, demanda_id):
    demanda = get_object_or_404(Demanda, id=demanda_id)

    if request.user.perfil.tipo == 'suporte':
        # Iniciar atendimento, muda o status da demanda
        demanda.status = 'Em Atendimento'
        demanda.realizador = request.user
        demanda.save()

        # Enviar e-mail para o autor da demanda
        try:
            operador = demanda.operador  # Autor da demanda
            assunto = f"Atendimento iniciado na demanda: {demanda.titulo}"
            mensagem = (
                f"Olá, {operador.nome}!\n\n"
                f"O operador {request.user.nome} iniciou o atendimento da sua demanda.\n\n"
                "Detalhes da demanda:\n"
                f"Título: {demanda.titulo}\n"
                f"Área: {demanda.area}\n"
                f"Status: {demanda.status}\n\n"
                "Obrigado por utilizar o sistema MeuTicket!\n"
            )
            remetente = 'bragasan34@gmail.com'
            destinatario = [operador.email]  # E-mail do operador da demanda

            send_mail(assunto, mensagem, remetente, destinatario)
            messages.success(request, 'Atendimento iniciado com sucesso! E-mail enviado ao autor da demanda.')
        except Exception as e:
            messages.error(request, f'Erro ao enviar o e-mail: {str(e)}')
    else:
        messages.error(request, 'Apenas usuários de suporte podem iniciar atendimentos.')

    return redirect('historico_demanda', id_demanda=demanda.id)



@login_required
def reabrir_demanda(request, demanda_id):
    demanda = get_object_or_404(Demanda, id=demanda_id)

    if request.user.perfil.tipo == 'suporte':
        # Verifica se a demanda está fechada
        if demanda.status == 'Fechado':
            demanda.status = 'Aberto'
            demanda.realizador = None  # Remove o realizador ao reabrir
            demanda.save()

            messages.success(request, 'Demanda reaberta com sucesso!')
        else:
            messages.error(request, 'Apenas demandas fechadas podem ser reabertas.')
    else:
        messages.error(request, 'Apenas usuários de suporte podem reabrir demandas.')

    return redirect('historico_demanda', id_demanda=demanda.id)



def relatorio(request):
    # Pegando os filtros dos parâmetros da requisição
    status = request.GET.get('status', 'todos')
    area = request.GET.get('area', 'todos')
    usuario = request.GET.get('usuario', 'todos')
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Se não for passado, define as datas de início e fim como o dia atual
    if not data_inicio:
        data_inicio = datetime.today().strftime('%Y-%m-%d')
    if not data_fim:
        data_fim = datetime.today().strftime('%Y-%m-%d')

    # Conversão das datas para o formato datetime
    data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
    data_fim = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)

    # Base para filtragem
    demandas = Demanda.objects.all()

    # Aplicando os filtros
    if status and status != "todos":
        demandas = demandas.filter(status=status)
    if area and area != "todos":
        demandas = demandas.filter(area_id=area)
    if usuario and usuario != "todos":
        demandas = demandas.filter(operador_id=usuario)
    if data_inicio and data_fim:
        demandas = demandas.filter(data_criacao__range=[data_inicio, data_fim])

    # Paginação
    page_number = request.GET.get('page', 1)
    paginator = Paginator(demandas, 30)  # Exibe 30 registros por página
    try:
        demandas_paginadas = paginator.page(page_number)
    except PageNotAnInteger:
        demandas_paginadas = paginator.page(1)
    except EmptyPage:
        demandas_paginadas = paginator.page(paginator.num_pages)

    # Carregando dados adicionais para os filtros
    areas = Area.objects.all()
    usuarios = Usuario.objects.all()

    # Preparando o contexto
    context = {
        'page_obj': demandas_paginadas,
        'areas': areas,
        'usuarios': usuarios,
        'status_options': Demanda.STATUS_CHOICES,
        'filtros': {
            'status': status,
            'area': area,
            'usuario': usuario,
            'data_inicio': data_inicio.strftime('%d/%m/%Y'),
            'data_fim': (data_fim - timedelta(days=1) + timedelta(seconds=1)).strftime('%d/%m/%Y'),
        },
        'exportar_pdf': False  # Indica que é visualização normal
    }

    return render(request, 'relatorio.html', context)


def relatorio_preview_view(request):
    # Obter filtros da requisição GET
    status = request.GET.get('status', 'todos')
    area = request.GET.get('area', 'todos')
    usuario = request.GET.get('usuario', 'todos')
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Conversão das datas para datetime
    data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d') if data_inicio else None
    data_fim_dt = (
        datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        if data_fim
        else None
    )

    # Base para filtragem
    demandas = Demanda.objects.all()

    # Aplicar filtros
    if status and status != "todos":
        demandas = demandas.filter(status=status)
    if area and area != "todos":
        demandas = demandas.filter(area_id=area)
    if usuario and usuario != "todos":
        demandas = demandas.filter(operador_id=usuario)
    if data_inicio_dt:
        demandas = demandas.filter(data_criacao__gte=data_inicio_dt)
    if data_fim_dt:
        demandas = demandas.filter(data_criacao__lte=data_fim_dt)

    # Verifica se o relatório é para exportação
    exportar_pdf = request.GET.get('exportar_pdf', 'false').lower() == 'true'

    if exportar_pdf:
        # Sem paginação: retorna todos os itens
        page_obj = demandas
    else:
        # Paginação para preview
        page_number = request.GET.get('page', 1)
        paginator = Paginator(demandas, 33)  # 30 registros por página
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

    # Dados adicionais para os filtros
    usuario_obj = None
    if usuario and usuario != "todos":
        usuario_obj = get_object_or_404(Usuario, id=usuario)

    area_obj = None
    if area and area != "todos":
        area_obj = get_object_or_404(Area, id=area)

    # Criar a query string com os filtros atuais
    filtros_atualizados = {
        'status': status,
        'area': area,
        'usuario': usuario,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    filtros_query = urlencode(filtros_atualizados)

    # Preparar o contexto
    context = {
        'page_obj': page_obj,  # Paginação ou todos os itens
        'filtros': {
            'status': status,
            'area': area_obj.nomearea if area_obj else 'Todos',
            'usuario': usuario_obj.nome if usuario_obj else 'Todos',
            'data_inicio': data_inicio_dt.strftime('%d/%m/%Y') if data_inicio_dt else 'Não especificado',
            'data_fim': data_fim_dt.strftime('%d/%m/%Y') if data_fim_dt else 'Não especificado',
        },
        'filtros_query': filtros_query,
        'exportar_pdf': exportar_pdf,  # Define se é PDF ou preview
    }

    return render(request, 'relatorio_preview.html', context)

 
def gerar_pdf_relatorio(request):
    # Pegando os mesmos filtros da visualização
    status = request.GET.get('status', 'todos')
    area = request.GET.get('area', 'todos')
    usuario = request.GET.get('usuario', 'todos')
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Conversão das datas
    data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d') if data_inicio else None
    data_fim_dt = (
        datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
        if data_fim
        else None
    )

    # Filtrando as demandas
    demandas = Demanda.objects.all()
    if status and status != "todos":
        demandas = demandas.filter(status=status)
    if area and area != "todos":
        demandas = demandas.filter(area_id=area)
    if usuario and usuario != "todos":
        demandas = demandas.filter(operador_id=usuario)
    if data_inicio_dt:
        demandas = demandas.filter(data_criacao__gte=data_inicio_dt)
    if data_fim_dt:
        demandas = demandas.filter(data_criacao__lte=data_fim_dt)

    # Configurações do PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_demandas.pdf"'

    # Configuração do documento
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=30, rightMargin=30)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Cabeçalho com logo
    logo_path = os.path.join(settings.STATIC_ROOT, "img/MeuTicket.png")
    elements.append(Image(logo_path, width=80, height=40))
    elements.append(Paragraph("Relatório de Demandas", title_style))
    elements.append(Spacer(1, 12))

    # Filtros utilizados
    filtros = [
        f"Status: {status if status != 'todos' else 'Todos'}",
        f"Área: {area if area != 'todos' else 'Todas'}",
        f"Usuário: {usuario if usuario != 'todos' else 'Todos'}",
        f"Data Inicial: {data_inicio if data_inicio else 'Não especificada'}",
        f"Data Final: {data_fim if data_fim else 'Não especificada'}",
    ]
    for filtro in filtros:
        elements.append(Paragraph(filtro, normal_style))
    elements.append(Spacer(1, 12))

    # Tabela de demandas
    table_data = [["ID", "Título", "Status", "Operador", "Aberto em"]]
    for demanda in demandas:
        table_data.append([
            demanda.id,
            demanda.titulo,
            demanda.status,
            demanda.operador.nome,
            demanda.data_criacao.strftime("%d/%m/%Y"),
        ])

    # Estilo da tabela
    table = Table(table_data, colWidths=[40, 200, 80, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(table)

    # Renderizar o PDF
    doc.build(elements)

    return response


def gerar_pdf(request):
    # Filtros da requisição GET
    status = request.GET.get('status', 'todos')
    area = request.GET.get('area', 'todos')
    usuario = request.GET.get('usuario', 'todos')
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)

    # Capturar o nome do usuário logado
    nome_usuario_logado = request.user.nome  # Nome do usuário obtido do request

    # Conversão das datas
    try:
        data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y') if data_inicio else None
    except ValueError:
        data_inicio_dt = None

    try:
        data_fim_dt = (
            datetime.strptime(data_fim, '%d/%m/%Y') + timedelta(days=1) - timedelta(seconds=1)
            if data_fim
            else None
        )
    except ValueError:
        data_fim_dt = None

    # Consulta inicial
    demandas = Demanda.objects.all()

    # Aplicar filtros
    if status and status != "todos":
        demandas = demandas.filter(status=status)
    if area and area != "todos":
        try:
            area_id = int(area)
            demandas = demandas.filter(area_id=area_id)
        except ValueError:
            pass
    if usuario and usuario != "todos":
        try:
            usuario_id = int(usuario)
            demandas = demandas.filter(operador_id=usuario_id)
        except ValueError:
            pass
    if data_inicio_dt:
        demandas = demandas.filter(data_criacao__gte=data_inicio_dt)
    if data_fim_dt:
        demandas = demandas.filter(data_criacao__lte=data_fim_dt)

    # Criar PDFs
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margem_esquerda = 30
    margem_direita = 30
    margem_superior = 70
    margem_inferior = 30

    largura_util = width - margem_esquerda - margem_direita

    # Cabeçalhos da tabela
    headers = ["ID", "Título", "Status", "Operador", "Data Abertura"]
    col_widths = [40, 250, 75, 100, 78]
    x_positions = [margem_esquerda]
    for w in col_widths:
        x_positions.append(x_positions[-1] + w)

    # Função para desenhar o cabeçalho
    def draw_header():
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'MeuTicket.png')
        p.drawImage(logo_path, margem_esquerda, height - margem_superior + 10, width=80, height=40)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(margem_esquerda + 200, height - margem_superior + 25, "Relatório de Demandas")
        p.setFont("Helvetica", 9)
        p.drawString(
            margem_esquerda,
            height - margem_superior - 10,
            f"Status: {status} | Área: {area} | Usuário: {usuario}",
        )
        p.drawString(
            margem_esquerda,
            height - margem_superior - 25,
            f"Data Inicial: {data_inicio or 'Não especificado'} | Data Final: {data_fim or 'Não especificado'}",
        )

    # Função para desenhar o rodapé
    def draw_footer(page_number, total_paginas):
        """
        Adiciona o rodapé ao PDF com informações sobre o sistema, usuário e número de páginas.

        Args:
            page_number (int): Número da página atual.
            total_paginas (int): Total de páginas do documento.
        """
        # Define a fonte do rodapé
        p.setFont("Helvetica", 9)

        # Texto do lado esquerdo: "MeuTicket - Relatório gerado por [Usuário] em [Data Atual]"
        texto_esquerda = (
            f"MeuTicket - Relatório gerado por {nome_usuario_logado} "
            f"em {datetime.now().strftime('%d/%m/%Y')}"
        )
        p.drawString(margem_esquerda, margem_inferior, texto_esquerda)

        # Texto do lado direito: "Página [Número Atual] de [Total de Páginas]"
        texto_direita = f"Página {page_number} de {total_paginas}"
        largura_texto_direita = p.stringWidth(texto_direita, "Helvetica", 9)
        p.drawString(width - margem_direita - largura_texto_direita, margem_inferior, texto_direita)

    # Função para desenhar cabeçalhos de tabela
    def draw_table_header(y):
        p.setFillColor(colors.grey)
        p.rect(margem_esquerda, y, largura_util, 20, fill=1)
        p.setFillColor(colors.white)
        for i, header in enumerate(headers):
            p.drawString(x_positions[i] + 5, y + 5, header)
        p.setFillColor(colors.black)
        return y - 20

    # Função para desenhar linhas da tabela
    def draw_table_row(y, data, row_color=colors.white):
        p.setFillColor(row_color)
        p.rect(margem_esquerda, y, largura_util, 20, fill=1)
        p.setFillColor(colors.black)

        # Iterar pelas células da linha
        for i, cell in enumerate(data):
            # Quebra de texto para a coluna "Título"
            if i == 1:  # Coluna "Título"
                max_width = col_widths[i] - 10
                wrapped_lines = wrap(cell, width=int(max_width / 5))
                line_height = 10
                for line in wrapped_lines:
                    p.drawString(x_positions[i] + 5, y + 5, line)
                    y -= line_height
                y += len(wrapped_lines) * line_height  # Ajustar a posição vertical
            else:
                p.drawString(x_positions[i] + 5, y + 5, cell)

            # Desenhar borda direita da célula, exceto na última coluna
            if i < len(data) - 1:
                p.line(x_positions[i + 1], y + 20, x_positions[i + 1], y)

        # Linha inferior da linha da tabela
        p.line(margem_esquerda, y, largura_util + margem_esquerda, y)
        return y - 20

    # Gerar PDF
    y = height - margem_superior - 50
    page_number = 1
    total_paginas = 1  # Inicialize o total de páginas (ajuste isso se necessário)
    draw_header()
    draw_footer(page_number, total_paginas)
    y = draw_table_header(y)

    if demandas.exists():
        for demanda in demandas:
            if y < margem_inferior + 20:  # Verificar se cabe mais uma linha
                p.showPage()
                page_number += 1
                total_paginas += 1  # Incrementar o total de páginas
                draw_header()
                draw_footer(page_number, total_paginas)
                y = height - margem_superior - 50
                y = draw_table_header(y)

            # Dados da linha
            row_data = [
                str(demanda.id),
                demanda.titulo,
                demanda.status,
                demanda.operador.nome,
                demanda.data_criacao.strftime('%d/%m/%Y'),
            ]
            y = draw_table_row(y, row_data)
    else:
        p.drawString(margem_esquerda, y, "Nenhuma demanda encontrada com os filtros aplicados.")

    # Atualizar o rodapé com o total de páginas
    draw_footer(page_number, total_paginas)

    # Finalizar PDF
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_demandas.pdf"'
    return response














# Create your views here.
