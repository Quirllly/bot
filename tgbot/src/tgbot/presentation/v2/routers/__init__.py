__all__ = [
    "start_router",
    "main_router",
    "farm_stars_router",
    "get_link_router",
    "reviews_router",
    "faq_router",
    "boost_router",
    "profile_router",
    "mini_games_router",
    "tasks_router",
    "withdraw_router",
    "rating_router",
    "admin_router",
]

from .start import start_router
from .main import main_router
from .farm_stars import farm_stars_router
from .get_link import get_link_router
from .reviews import reviews_router
from .faq import faq_router
from .boost import boost_router
from .profile import profile_router
from .mini_games import mini_games_router
from .tasks import tasks_router
from .withdraw import withdraw_router
from .rating import rating_router
from .admin import admin_router