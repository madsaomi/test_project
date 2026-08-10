from .base import *  # noqa: F401,F403

DEBUG = True

try:
    import debug_toolbar  # noqa: F401
except ImportError:
    pass
else:
    INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
