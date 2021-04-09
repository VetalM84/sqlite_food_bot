# -*- coding: utf-8 -*-

import config
import keyboard as kb
import func
import telebot
from telebot import types
from collections import defaultdict

db = func.DbFunc('db.sqlite')

bot = telebot.TeleBot(config.token)
_default_data = lambda: defaultdict(_default_data)
user_dict = _default_data()

all_products_list = []
cart = func.Cart()
step = ''


def error_message(message):
    bot.reply_to(message, config.exception_message)
    bot.send_message(message.chat.id, '/start')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global step
    step = 'welcome'
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
    if message.text == config.button_menu:
        choose_category_step(message)
    elif message.text == config.button_back:
        if step == 'categories' or step == 'cart':
            send_welcome(message)
        elif step == 'products':
            choose_category_step(message)
    elif message.text == config.button_cart:
        bot.send_message(chat_id, show_products_in_cart(message))
    elif message.text == config.button_clear_cart:
        remove_all_from_cart(message)
    elif message.text in all_products_list:
        cart.add_to_cart(chat_id, message.text)
        bot.send_message(chat_id, 'Добалено в корзину покупок!')
        # bot.send_message(chat_id, show_products_in_cart(message))
    elif step == 'cart' and message.text.startswith('❌ '):
        remove_product_from_cart(message)
    else:
        bot.send_message(chat_id, config.dont_know_message)
        bot.send_message(chat_id, '/start')


def choose_category_step(message):
    """отображаем категории товаров"""
    chat_id = message.chat.id
    global step
    step = 'categories'
    markup = kb.dynamic_kb(buttons=db.get_categories(), row_width=2)
    markup.add(config.button_checkout, config.button_cart)

    if message.text == config.button_cart:
        bot.send_message(chat_id, show_products_in_cart(message))
    else:
        msg = bot.send_message(message.chat.id, config.choose_category_message, reply_markup=markup)
        bot.register_next_step_handler(msg, show_products_step)


def show_products_step(message):
    """отображаем все товары категории"""
    global step
    chat_id = message.chat.id
    step = 'products'
    try:
        if message.text == config.button_cart:
            bot.send_message(chat_id, show_products_in_cart(message))
        else:
            items = db.get_products(message.text)
            all_products_list.extend(items)
            if len(items) > 0:
                markup = kb.dynamic_kb(buttons=items, one_time_keyboard=False, row_width=1)
                markup.add(config.button_back, row_width=2)
                bot.send_message(message.chat.id, 'Выберите:', reply_markup=markup)
                # bot.register_next_step_handler(msg, process_product_step)
            else:
                bot.send_message(message.chat.id, config.no_product_message)
                choose_category_step(message)
    except Exception:
        error_message(message)


def show_products_in_cart(message):
    """отображаем все товары в корзине"""
    global step
    step = 'cart'
    try:
        chat_id = message.chat.id
        result = sorted(cart.get_cart_items(chat_id))
        result_for_remove = map(lambda x: '❌ ' + x, result)
        if len(result) > 0:
            markup = kb.dynamic_kb(buttons=result_for_remove, one_time_keyboard=False, row_width=1)
            markup.add(config.button_back, config.button_clear_cart, row_width=2)
            bot.send_message(message.chat.id, 'Для удаления товара из корзины нажмите на его кнопку',
                             reply_markup=markup)
            text_result = '\n'.join(result)
            return f'В корзине:\n{text_result}'
        else:
            return 'Корзина покупок пуста... Давайте что-то в нее положим.'
    except Exception:
        error_message(message)


def remove_product_from_cart(message):
    try:
        chat_id = message.chat.id
        result = sorted(cart.get_cart_items(chat_id))
        item_to_remove = message.text.removeprefix('❌ ')
        if item_to_remove in result:
            cart.remove_from_cart(chat_id, item_to_remove)
            bot.send_message(message.chat.id, 'Товар удален')
            show_products_in_cart(message)
            # return f''
        else:
            return 'Такого товара в корзине нет.'
    except Exception:
        error_message(message)


def remove_all_from_cart(message):
    try:
        chat_id = message.chat.id
        cart.clear_cart(chat_id)
        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Корзина товаров очищена', reply_markup=markup)
        choose_category_step(message)
        # return result
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
        # bot.register_next_step_handler(msg, process_delivery_company_step)
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


if __name__ == '__main__':
    bot.polling(none_stop=True)
