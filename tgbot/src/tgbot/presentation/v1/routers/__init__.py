__all__ = (
    "start_router",
    "main_router",
    "profile_router",
    "rating_router",
    "withdraw_router",
    "tasks_router",
    "gain_stars_router",
)

from .start import start_router
from .main import main_router
from .profile import profile_router
from .rating import rating_router
from .withdraw import withdraw_router
from .tasks import tasks_router
from .gain_stars import gain_stars_router
