# -*- coding: utf-8 -*-

import config
import keyboard as kb
import func
import telebot
from telebot import types
from collections import defaultdict
import sqlite3

db = func.DbFunc('db.sqlite')

bot = telebot.TeleBot(config.token)
_default_data = lambda: defaultdict(_default_data)
user_dict = _default_data()

all_products_list = []
cart = func.Cart()


def error_message(message):
    bot.reply_to(message, config.exception_message)
    bot.send_message(message.chat.id, '/start')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # markup = types.InlineKeyboardMarkup()
    # key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    # key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    # markup.add(key_yes, key_no)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_btn = types.KeyboardButton(config.button_menu)
    cart_btn = types.KeyboardButton(config.button_cart)
    checkout_btn = types.KeyboardButton(config.button_checkout)
    markup.add(menu_btn)
    markup.add(checkout_btn, cart_btn)

    bot.send_message(message.chat.id, config.welcome_message, reply_markup=markup)


# бот отвечает на текстовые сообщения и кнопки types.KeyboardButton
@bot.message_handler(content_types=['text'])
def send_text(message):
    chat_id = message.chat.id
    if message.text == config.button_menu or message.text == config.button_back:
        choose_category_step(message)
    elif message.text == config.button_cart:
        bot.send_message(chat_id, show_products_in_cart(message))
    elif message.text in all_products_list:
        cart.add_to_cart(chat_id, message.text)
        bot.send_message(chat_id, 'Добалено в корзину покупок!')
        # bot.send_message(chat_id, show_products_in_cart(message))
    else:
        bot.send_message(chat_id, config.dont_know_message)
        bot.send_message(chat_id, '/start')


# бот отвечает на инлайн кнопки types.InlineKeyboardButton
# @bot.callback_query_handler(func=lambda call: True)
# def callback_worker(call):
#     if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
#         # код сохранения данных, или их обработки
#         bot.send_message(call.message.chat.id, 'да')
#     elif call.data == "no":
#         bot.send_message(call.message.chat.id, 'нет')


def choose_category_step(message):
    """отображаем категории товаров"""
    markup = kb.dynamic_kb(buttons=db.get_categories(), row_width=2)
    markup.add(config.button_back, config.button_start, config.button_checkout, config.button_cart)
    if message.text == config.button_back:
        send_welcome(message)
    else:
        msg = bot.send_message(message.chat.id, config.choose_category_message, reply_markup=markup)
        bot.register_next_step_handler(msg, show_products_step)


def show_products_step(message):
    """отображаем все товары категории"""
    try:
        items = db.get_products(message.text)
        all_products_list.extend(items)
        if len(items) > 0:
            markup = kb.dynamic_kb(buttons=items, one_time_keyboard=False, row_width=1)
            markup.add(config.button_back, config.button_start, row_width=2)
            msg = bot.send_message(message.chat.id, 'Выберите:', reply_markup=markup)
            # bot.register_next_step_handler(msg, process_product_step)
        else:
            bot.send_message(message.chat.id, config.no_product_message)
            choose_category_step(message)
    except Exception:
        error_message(message)


def show_products_in_cart(message):
    """отображаем все товары в корзине"""
    try:
        chat_id = message.chat.id
        result = cart.get_cart_items(chat_id)
        if len(result) > 0:
            kb.dynamic_kb(buttons=result, one_time_keyboard=False, row_width=1)
            text_result = '\n'.join(result)
            return f'В корзине:\n{text_result}'
            # print(result)
        else:
            return 'Корзина покупок пуста... Давайте что-то в нее положим.'
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
