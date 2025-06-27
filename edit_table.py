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

    # Выпадающий список для редактирования статуса оплаты
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

    # Функция для поиска заказа по ID
    def handle_search(e):
        order_id = order_id_input.value.strip()
        if not order_id.isdigit():
            page.snack_bar = ft.SnackBar(
                ft.Text("ID заказа должно быть числом", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        order_data = get_order_by_id(int(order_id))
        if not order_data:
            page.snack_bar = ft.SnackBar(
                ft.Text("Заказ не найден", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        current_date_display.value = f"Текущая дата заказа: {order_data[2]}"
        current_payment_status_display.value = f"Текущий статус оплаты: {order_data[5]}"
        page.update()

    # Функция длс сохранения изменений
    def handle_save(e):
        order_id = order_id_input.value.strip()
        new_date = edit_date_input.value.strip()
        new_payment_status = edit_payment_status_dropdown.value
        if not new_date or not new_payment_status or not order_id:
            page.snack_bar = ft.SnackBar(
                ft.Text("Новая дата не может быть пустой", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            day, month, year = map(int, new_date.split("."))
            if not (1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError
        except ValueError:
            page.snack_bar = ft.SnackBar(
                ft.Text("Новая дата должна быть в формате День.Месяц.Год", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        update_order_in_db(int(order_id), new_date, new_payment_status)
        page.snack_bar = ft.SnackBar(
            ft.Text("Изменения сохранены", color=ft.colors.WHITE),
            bgcolor=ft.colors.GREEN,
            duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    # Кнопка для поиска заказа
    search_button = ft.ElevatedButton(
        content=ft.Text("Поиск", size=20, color=ft.colors.WHITE),
        on_click=handle_search,
        width=200,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    # Кнопка для сохранения изменений
    save_button = ft.ElevatedButton(
        content=ft.Text("Сохранить", size=20, color=ft.colors.WHITE),
        on_click=handle_save,
        width=200,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    edit_content = ft.Column(
        [
            ft.Row(
                [
                    order_id_input,
                    search_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    current_date_display,
                    edit_date_input
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    current_payment_status_display,
                    edit_payment_status_dropdown
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    save_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )

    return edit_content

    