# Deploy do MeuTicket no Render

Guia objetivo para publicar o projeto `MeuTicket` (Django) no Render usando Gunicorn + PostgreSQL.

## 1. Criar o banco PostgreSQL

1. No Render, clique em `New +` -> `PostgreSQL`.
2. Sugestao de preenchimento:
   - `Name`: `meu-ticket-db`
   - `Database`: `meuticket`
   - `User`: `meuticket_user`

## 2. Criar o Web Service

1. `New +` -> `Web Service`.
2. Conecte o repositorio do GitHub.
3. Configure:
   - `Runtime`: Python
   - `Branch`: `main`

## 3. Build e Start Command

### Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```bash
gunicorn MeuTicket.wsgi:application
```

## 4. Variaveis de ambiente (Render)

Minimas:
```env
SECRET_KEY=gere-uma-chave-forte
DEBUG=False
ALLOWED_HOSTS=meu-ticket.onrender.com
CSRF_TRUSTED_ORIGINS=https://meu-ticket.onrender.com
DATABASE_URL=postgresql://...
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SERVE_MEDIA_IN_PROD=True
```

Email (opcional; necessario para envio de emails na aplicacao):
```env
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

## 6. Criar admin sem terminal (Render free)

Como no plano free voce nao tem shell/terminal, o projeto tem um comando automatico:
`python manage.py bootstrap_admin`

Ele cria um superusuario somente se:
- `AUTO_CREATE_ADMIN=True`
- e as variaveis abaixo estiverem preenchidas

```env
AUTO_CREATE_ADMIN=True
ADMIN_EMAIL=seuemail@exemplo.com
ADMIN_PASSWORD=senha-forte-aqui
ADMIN_NOME=Seu Nome
ADMIN_CPF=12345678901
```

Recomendacao: depois do primeiro login no `/admin/`, volte `AUTO_CREATE_ADMIN` para `False`.

## 5. Observacao sobre arquivos em `media/`

Para demo/portfolio, `SERVE_MEDIA_IN_PROD=True` ajuda a nao quebrar imagens.
Para producao real com uploads, o ideal e usar storage externo (S3/Cloudinary), porque o disco do Render nao e um storage persistente para uploads.
