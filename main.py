import os
import telebot
from telebot import types
from models import engine, Session
from handlers import register_handlers


TOKEN = "8104879861:AAEu8DGjBeocnwQ4xkyp48GOoC0kZshwf30"
bot = telebot.TeleBot(TOKEN)


register_handlers(bot)

if __name__ == '__main__':
    bot.polling(none_stop=True)
