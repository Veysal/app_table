import sqlite3
import flet as ft

# Функция для обновления данных в БД
def update_order_in_db(order_id, new_date,new_payment_status):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET order_date = ?, payment_status = ?
        WHERE order_id = ?
    """, (new_date,new_payment_status, order_id)
    )
    conn.commit()
    conn.close()

# Функция для поиска заказа по ID
def get_order_by_id(order_id):
    conn = sqlite3
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders
        WHERE order_id = ?
    """, (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order

# Функция для создания вкладки Редактирования
def create_edit_tab(page):
    # Поле для ввода ID заказа
    order_id_input = ft.TextField(
        label="ID заказа",
        hint_text="Введите ID заказа",
        width=200,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.BLUE,
        border_width=2,
        text_style=ft.TextStyle(color=ft.colors.YELLOW)
    )

    # Поле для отображения текущей даты заказа
    current_date_display = ft.Text(
        value="Текущая дата заказа",
        color=ft.colors.YELLOW,
        size=18,
        weight=ft.FontWeight.BOLD    
    )

    # Поле для редактирования даты
    edit_date_input = ft.TextField(
        label="Новая дата заказа",
        hint_text="Введите новую дату",
        width=200,
        text_align=ft.TextAlign.CENTER,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.YELLOW,
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
        border_width=2    
    )

    # Поле для отображения текущего статуса оплаты
    current_payment_status_display = ft.Text(
        value="Текущий статус оплаты",
        color=ft.colors.YELLOW,
        size=18,
        weight=ft.FontWeight.BOLD
    )

    edit_payment_status_dropdown = ft.Dropdown(
        label="Новый статус оплаты",
        hint_text="Выберите новый статус оплаты",
        width=200,
        options=[
            ft.dropdown.Option("Оплачено"),
            ft.dropdown.Option("Не оплачено"),
            ft.dropdown.Option("Отменено")
        ],
        border=ft.InputBorder.OUTLINE,
        value="Не оплачен",
        text_style=ft.TextStyle(color=ft.colors.RED),
    )