import sqlite3
import flet as ft
from datetime import datetime

# Функция для обновления данных в БД
def update_order_in_db(order_id, new_date,new_payment_status):
    with sqlite3.connect('work_tracker.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET order_date = ?, payment_status = ?
            WHERE order_id = ?
        """, (new_date,new_payment_status, order_id))
        conn.commit()

# Функция для поиска заказа по ID
def get_order_by_id(order_id):
    with sqlite3.connect('work_tracker.db') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM orders WHERE order_id = ?""", (order_id,))
        order = cursor.fetchone()
        return order

# Функция для создания вкладки Редактирования
def create_edit_tab(page):
    # Поле для ввода ID заказа
    order_id_input = ft.TextField(
        label="ID заказа для поиска",
        hint_text="Введите ID заказа",
        width=300,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        autofocus=True,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        border_width=2,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW)
    )

    # Поле для отображения текущей даты заказа
    current_date_display = ft.Text(
        value="Текущая дата заказа",
        color=ft.Colors.YELLOW,
        size=16,
    )

    # Поле для редактирования даты
    edit_date_input = ft.TextField(
        label="Новая дата заказа (ДД.ММ.ГГГГ)",
        hint_text="Введите новую дату",
        width=300,
        text_align=ft.TextAlign.CENTER,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border_width=2    
    )

    # Поле для отображения текущего статуса оплаты
    current_payment_status_display = ft.Text(
        value="Текущий статус оплаты",
        color=ft.Colors.YELLOW,
        size=16,
    )

    # Выпадающий список для редактирования статуса оплаты
    edit_payment_status_dropdown = ft.Dropdown(
        label="Новый статус оплаты",
        hint_text="Выберите новый статус оплаты",
        width=300,
        options=[
            ft.dropdown.Option("Оплачено"),
            ft.dropdown.Option("Не оплачено"),
            ft.dropdown.Option("Отменено")
        ],
        border=ft.InputBorder.OUTLINE,
        value="Не оплачено",
        text_style=ft.TextStyle(color=ft.Colors.RED),
    )

    def update_payment_status_color(e):
        status = edit_payment_status_dropdown.value
        if status == "Оплачено":
            edit_payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.GREEN)
        elif status == "Не оплачено":
            edit_payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.RED)
        elif status == "Отменено":
            edit_payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.ORANGE)
        page.update()

    edit_payment_status_dropdown.on_change = update_payment_status_color

    # Функция для поиска заказа по ID
    def handle_search(e):
        order_id = order_id_input.value.strip()
        if not order_id.isdigit():
            page.snack_bar = ft.SnackBar(
                ft.Text("ID заказа должно быть числом", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            edit_form.visible = False
            page.update()
            return
        order_data = get_order_by_id(int(order_id))
        if not order_data:
            page.snack_bar = ft.SnackBar(
                ft.Text("Заказ не найден", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            edit_form.visible = False
            page.update()
            return
        
        current_date_display.value = f"Текущая дата заказа: {order_data['order_date']}"
        current_payment_status_display.value = f"Текущий статус оплаты: {order_data['payment_status']}"
        
        # Заполняем поля для редактирования
        edit_date_input.value = order_data['order_date']
        edit_payment_status_dropdown.value = order_data['payment_status']
        update_payment_status_color(None) # Обновляем цвет

        edit_form.visible = True
        page.update()

    # Функция для сохранения изменений
    def handle_save(e):
        order_id = order_id_input.value.strip()
        new_date = edit_date_input.value.strip()
        new_payment_status = edit_payment_status_dropdown.value

        if not new_date or not new_payment_status or not order_id:
            page.snack_bar = ft.SnackBar(
                ft.Text("Все поля должны быть заполнены", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            datetime.strptime(new_date, "%d.%m.%Y")
        except ValueError:
            page.snack_bar = ft.SnackBar(
                ft.Text("Неверный формат даты. Используйте ДД.ММ.ГГГГ", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        update_order_in_db(int(order_id), new_date, new_payment_status)
        page.snack_bar = ft.SnackBar(
            ft.Text("Изменения сохранены", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN,
            duration=2000,
        )
        page.snack_bar.open = True

        # Сбрасываем форму
        order_id_input.value = ""
        edit_date_input.value = ""
        edit_payment_status_dropdown.value = "Не оплачено"
        update_payment_status_color(None)
        edit_form.visible = False
        order_id_input.focus()
        page.update()

    # Кнопка для сохранения изменений
    save_button = ft.ElevatedButton(
        content=ft.Text("Сохранить", size=20, color=ft.Colors.WHITE),
        on_click=handle_save,
        width=300,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    # Контейнер для формы редактирования, изначально скрыт
    edit_form = ft.Column(
        controls=[
            ft.Divider(),
            current_date_display,
            edit_date_input,
            ft.Container(height=10),
            current_payment_status_display,
            edit_payment_status_dropdown,
            ft.Container(height=20),
            save_button,
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # Кнопка для поиска заказа
    search_button = ft.ElevatedButton(
        content=ft.Text("Поиск", size=20, color=ft.Colors.WHITE),
        on_click=handle_search,
        width=300,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    edit_content = ft.Column(
        [
            ft.Container(height=20),
            ft.Text("Редактирование заказа", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW),
            ft.Container(height=20),
            order_id_input,
            search_button,
            edit_form,
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        expand=True
    )

    return edit_content

    