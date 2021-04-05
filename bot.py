# -*- coding: utf-8 -*-

import config
import keyboard as kb
import func
import telebot
from telebot import types
from collections import defaultdict
import sqlite3

all_products_list = []
db = func.DbFunc('db.sqlite')

bot = telebot.TeleBot(config.token)
_default_data = lambda: defaultdict(_default_data)
user_dict = _default_data()


def error_message(message):
    bot.reply_to(message, config.exception_message)
    bot.send_message(message.chat.id, '/start')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # markup = types.InlineKeyboardMarkup()
    # key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    # key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    # markup.add(key_yes, key_no)
    chat_id = message.chat.id
    global cart
    cart = func.Cart(chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    order_btn = types.KeyboardButton(config.button_order)
    cart_btn = types.KeyboardButton(config.button_cart)
    info_btn = types.KeyboardButton(config.button_more)
    contacts_btn = types.KeyboardButton(config.button_contact)
    markup.add(order_btn, cart_btn)
    markup.add(info_btn, contacts_btn)

    bot.send_message(message.chat.id, config.welcome_message, reply_markup=markup)


# бот отвечает на текстовые сообщения и кнопки types.KeyboardButton
@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == config.button_order or message.text == config.button_back:
        choose_category_step(message)
    elif message.text == config.button_cart:
        bot.send_message(message.chat.id, cart.get_cart_items())
    elif message.text == config.button_more:
        bot.send_message(message.chat.id, config.description_message)
    elif message.text == config.button_contact:
        bot.send_message(message.chat.id, config.contacts_message)
    elif message.text in all_products_list:
        cart.add_to_cart(message.text)
        bot.send_message(message.chat.id, 'Добалено в корзину покупок!')
        bot.send_message(message.chat.id, cart.get_cart_items())

    else:
        bot.send_message(message.chat.id, config.dont_know_message)
        bot.send_message(message.chat.id, '/start')


# бот отвечает на инлайн кнопки types.InlineKeyboardButton
# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
#         # код сохранения данных, или их обработки
#         bot.send_message(call.message.chat.id, 'да')
#     elif call.data == "no":
#         bot.send_message(call.message.chat.id, 'нет')


def choose_category_step(message):
    markup = kb.dynamic_kb(buttons=db.get_categories(), row_width=2)

    msg = bot.send_message(message.chat.id, config.choose_category_message, reply_markup=markup)
    bot.register_next_step_handler(msg, show_products_step)


def show_products_step(message):
    try:
        chat_id = message.chat.id
        items = db.get_products(message.text)
        all_products_list.extend(items)
        if len(items) > 0:
            markup = kb.dynamic_kb(buttons=items, one_time_keyboard=False, row_width=1)
            markup.row(config.button_back)
            msg = bot.send_message(message.chat.id, 'config.products[config.DESCRIPTION]', reply_markup=markup)
            # bot.register_next_step_handler(msg, process_product_step)
        else:
            bot.send_message(message.chat.id, config.no_product_message)
            choose_category_step(message)
    except Exception:
        error_message(message)


def process_product_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Товар'] = message.text

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.full_name_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_fullname_step)
    except Exception:
        error_message(message)


def process_fullname_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['ФИО'] = message.text

        markup = kb.contact_button(config.button_send_phone_number)

        msg = bot.send_message(chat_id, config.phone_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception:
        error_message(message)


def process_phone_step(message):
    try:
        chat_id = message.chat.id

        try:
            # если телефон передали кнопкой
            user_dict[chat_id]['Телефон'] = message.contact.phone_number
        except AttributeError:
            # если телефон передали сообщением
            user_dict[chat_id]['Телефон'] = message.text

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.city_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_city_step)
    except Exception:
        error_message(message)


def process_city_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Город, область'] = message.text

        markup = kb.dynamic_kb(buttons=config.delivery_company, row_width=2)

        msg = bot.send_message(chat_id, config.choose_delivery_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_delivery_company_step)
    except Exception:
        error_message(message)


def process_delivery_company_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Перевозчик'] = message.text

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.warehouse_number_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_warehouse_step)
    except Exception:
        error_message(message)


def process_warehouse_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Отделение'] = message.text

        markup = kb.dynamic_kb(buttons=config.payment_method, row_width=2)

        msg = bot.send_message(chat_id, config.payment_method_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_payment_step)
    except Exception:
        error_message(message)


def process_payment_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Оплата'] = message.text

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, config.comment_order_message, reply_markup=markup)
        bot.register_next_step_handler(msg, process_comment_step)
    except Exception:
        error_message(message)


def process_comment_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id]['Комментарий'] = message.text

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        bot.send_message(chat_id, config.thanks_message, reply_markup=markup)
        bot.send_message(chat_id, get_reg_data(chat_id, 'Ваша заявка', message.from_user.first_name))
        # отправить дубль в группу
        bot.send_message(config.forward_group_id, get_reg_data(chat_id, 'Заявка от бота', bot.get_me().username))
        bot.send_message(message.chat.id, '/start')
    except Exception:
        error_message(message)


def get_reg_data(user_id, title, name):
    response = title + ', ' + name + '\n'
    try:
        for key, value in user_dict[user_id].cart_items():
            response = response + key + ': ' + value + '\n'
        return response
    except Exception:
        print('Ой, неизвестная ошибка.')


# если прислали произвольное фото
@bot.message_handler(content_types=["photo"])
def send_help_text(message):
    bot.send_message(message.chat.id, config.error_image_message)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
# bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
# bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
