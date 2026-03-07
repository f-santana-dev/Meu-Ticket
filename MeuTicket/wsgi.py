"""
WSGI config for MeuTicket project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MeuTicket.settings')

application = get_wsgi_application()

# Render free: nao ha shell. Para a demo, criamos/promovemos o admin no startup quando habilitado por env.
# A funcao e idempotente e nao duplica usuario.
try:
    from demanda.bootstrap_admin import ensure_admin_from_env

    ensure_admin_from_env(stdout_write=print)
except Exception as exc:
    # Nao derruba o app se a base ainda nao estiver pronta ou se a config estiver incompleta.
    print(f"[bootstrap_admin] ignorado: {exc}")

