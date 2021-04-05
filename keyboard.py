# -*- coding: utf-8 -*-

from telebot import types


def dynamic_kb(buttons, one_time_keyboard=True, row_width=2):
    """динамические кнопки с настраиваемым кол-вом на строке и настраиваемым скрытием после клика"""
    btns = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard, row_width=row_width)\
        .add(*buttons)
    return btns


def contact_button(text):
    """кнопка отправки номера телефона"""
    btn = types.KeyboardButton(text=text, request_contact=True)
    button_phone = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(btn)
    return button_phone
