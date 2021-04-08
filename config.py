# -*- coding: utf-8 -*-

token = '1799386569:AAFkgamK2NDPPI1ljH4oHjkMn6TX1bxGn7w'
forward_group_id = -1001469759769

# цены на коптильни
small_koptilnya_price = 1150
small_koptilnya_thermo_price = 1300
big_koptilnya_price = 1450
big_koptilnya_thermo_price = 1600

PRODUCTS = "Товары"

products = {
    'Коптильни': {
        PRODUCTS:
            [f'Маленькая - {small_koptilnya_price} грн',
             f'Маленькая с термометром - {small_koptilnya_thermo_price} грн',
             f'Большая - {big_koptilnya_price} грн',
             f'Большая с термометром - {big_koptilnya_thermo_price} грн']
    },
}
# кнопки
button_menu = '📋 Меню ресторана'
button_cart = '🛒 Что в корзине?'
button_checkout = '🛵 Оформить заказ'
button_back = '⏪ Назад'
button_start = '⏫ В начало'
button_send_phone_number = "☎ Отправить номер телефона"
button_send_location = "☎ Отправить местоположение"

# доставка, оплата
payment_method = ['💵 Наложенный платеж', '💳 Предоплата на карту']

# сообщения от бота
no_product_message = "В этой категории пока нет товаров."
choose_category_message = "Пожалуйста, выберите, что хотите заказать"
welcome_message = "Здравствуйте. Я - бот по приему заявок на доставку еды с ресторана, чтобы вы хотели сделать?"
choose_koptilni_message = 'Какую хотите заказать?\n Пакет щепы в подарок к каждой коптильне.\n' \
                          '- Маленькая (внутренний размер 400х200х200 мм, наружный - 450х240х290 мм)\n' \
                          '- Большая (внутренний размер 450х250х250 мм, наружный - 500х300х340 мм)\n' \
                          'Также, можем установить термометр в любую коптильню.'
full_name_message = 'Для оформления заказа напишите Ваши: фамилию, имя, отчество'
phone_message = 'Ваш номер телефона?\n Нажмите на кнопку ниже или введите его (только цифры)'
city_message = 'Введите город и область доставки 🗺'
choose_delivery_message = 'Какой службой доставки отправить? 🚚'
warehouse_number_message = 'Введите номер отделения службы доставки или адрес'
payment_method_message = 'Как хотите оплатить покупку?'
comment_order_message = 'Есть ли еще какие-либо пожелания или вопросы?'
thanks_message = '🔥 Спасибо, заявка создана! Скоро мы с Вами обязательно свяжемся.'

# сообщения от бота об ошибках
dont_know_message = "Я не обучен отвечать на такие сообщения..."
error_image_message = 'Я не понимаю фото, напишите текст'
exception_message = 'Ой, какая-то ошибка. Если ничего не происходит попробуйте меня перезапустить.'
