# -*- coding: utf-8 -*-
import sqlite3
from collections import defaultdict


class DbFunc:

    def __init__(self, database):
        try:
            self.connection = sqlite3.connect(database, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as exc:
            print(f"Ошибка соединения с БД {exc}")

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    def get_categories(self) -> list:
        self.cursor.execute('SELECT category FROM products GROUP BY category')
        result = self.cursor.fetchall()
        result = [item for t in result for item in t]
        # print(result)
        return result

    def get_products(self, category) -> list:
        self.cursor.execute('SELECT name, price FROM products WHERE category LIKE ' + f'"{category}"')
        res = self.cursor.fetchall()
        result = []
        for item in res:
            x = item[0] + ' - ' + str(item[1]) + ' грн'
            result.append(x)
        # print(result)
        return result

    def place_order(self, user_id, user_name, products, location):
        order_info = (user_id, user_name, *products, location)
        self.cursor.execute("INSERT INTO orders VALUES (?,?,?,?)", order_info)
        self.connection.commit()


class Cart:
    def __init__(self):
        self.cart_items = defaultdict(list)

    def add_to_cart(self, user_id, product):
        self.cart_items[user_id].append(product)
        #
        # for key, value in self.cart_items.items():
        #     print(f'Здесь: {key}, {value}')

    def get_cart_items(self, user_id) -> list:
        cart_list = self.cart_items[user_id]
        return cart_list

    def remove_from_cart(self, user_id, item):
        cart_list = self.cart_items[user_id]
        cart_list.remove(item)
        return cart_list

    def clear_cart(self, user_id):
        cart_list = self.cart_items[user_id]
        cart_list.clear()
        return cart_list
