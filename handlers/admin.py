from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db_manager import update_game_status, get_pending_game
from config import ADMIN_ID
from handlers.game import pending_games