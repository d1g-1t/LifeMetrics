from .base import *

ENV = os.getenv('DJANGO_ENV', 'dev')

if ENV == 'production':
    from .prod import *
else:
    from .dev import *
