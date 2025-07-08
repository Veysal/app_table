import flet as ft
import sqlite3
import os
import csv
from datetime import datetime
from edit_table import create_edit_tab


# Инициализация базы данных SQLite3
def init_db():
    conn = sqlite3.connect("work_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            client_name TEXT NOT NULL,
            work_status TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            payment_amount REAL
        )
    """
    )
    conn.commit()
    conn.close()

# Функциф для добавления данных в базу данных
def add_order_to_db(order_id, order_date, client_name, work_status, payment_status, payment_amount):
    with sqlite3.connect("work_tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, order_date, client_name, work_status, payment_status, payment_amount)
            VALUES (?, ?, ?, ?, ?, ?)
    """,(order_id, order_date, client_name, work_status, payment_status, payment_amount))
        conn.commit()

def export_to_csv():
    try:
        with sqlite3.connect("work_tracker.db") as conn:
            cursor = conn.cursor()
            # Выбираем столбцы в нужном порядке, исключая первичный ключ `id`
            cursor.execute("SELECT order_id, order_date, client_name, work_status, payment_status, payment_amount FROM orders")
            rows = cursor.fetchall()
            headers = ["ID заказа", "Дата заказа", "Имя клиента", "Статус работы", "Статус оплаты", "Сумма оплаты"]
            file_path =("orders.csv")
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            return file_path
    except Exception as ex:
        print(f"Ошибка при экспорте в CSV: {ex}")
        return None
    

# Агрегирующие функции
def get_total_payment():
    """Получаем общую сумму всех оплат клиентов"""
    with sqlite3.connect("work_tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(payment_amount) FROM orders")
        total = cursor.fetchone()[0]
        return total or 0

def get_average_payment():
    """Получаем среднюю сумму всех оплат клиентов"""
    with sqlite3.connect("work_tracker.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(payment_amount) FROM orders")
        average = cursor.fetchone()[0]
        return average or 0

def get_max_payment():
    """Получаем максимальную сумму оплаты клиента"""
    with sqlite3.connect("work_tracker.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Используем подзапрос для эффективности
        cursor.execute("SELECT * FROM orders WHERE payment_amount = (SELECT MAX(payment_amount) FROM orders)")
        rows = cursor.fetchall()
        return rows

def get_min_payment():
    """Получаем минимальную сумму оплаты клиента"""
    with sqlite3.connect("work_tracker.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE payment_amount = (SELECT MIN(payment_amount) FROM orders)")
        rows = cursor.fetchall()
        return rows


# Функция для поиска по имени клиента
def search_orders_by_client_name(client_name):
    with sqlite3.connect("work_tracker.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Добавляем % для поиска по частичному совпадению
        cursor.execute("SELECT * FROM orders WHERE client_name LIKE ?", (f"%{client_name}%",))
        rows = cursor.fetchall()
        return rows





# Основное приложение
def main(page: ft.Page):
    page.title = "User table"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK

    # Инициализация базы данных
    init_db()

    #Создание таблицы для отображения данных
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID заказа", color=ft.Colors.YELLOW)),
            ft.DataColumn(ft.Text("Дата заказа", color=ft.Colors.YELLOW)),
            ft.DataColumn(ft.Text("Имя клиента", color=ft.Colors.YELLOW)),
            ft.DataColumn(ft.Text("Статус работы", color=ft.Colors.YELLOW)),
            ft.DataColumn(ft.Text("Статус оплаты", color=ft.Colors.YELLOW)),
            ft.DataColumn(ft.Text("Сумма оплаты", color=ft.Colors.YELLOW)),
        ],
        rows=[]
    )

    # Поля для ввода данных
    order_id_input = ft.TextField(
        label="ID заказа",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )
    
    order_date_input = ft.TextField(
        label="Дата заказа",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    ) 


    client_name_input = ft.TextField(
        label="Имя клиента",
        width=200,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )


    #Установка цвета статуса работы для выпадающего списка
    def update_work_status_color(e):
        if work_status_dropdown.value == "В работе":
            work_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.ORANGE)
        elif work_status_dropdown.value == "Выполнено":
            work_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.GREEN)
        elif work_status_dropdown.value == "Отменено":
            work_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.RED)            
        page.update()

    # Выпадающий список
    work_status_dropdown = ft.Dropdown(
        label="Статус работы",
        width=200,
        options=[
            ft.dropdown.Option("В работе"),
            ft.dropdown.Option("Выполнено"),
            ft.dropdown.Option("Отменено")
        ],
        value = "В работе",
        on_change=update_work_status_color,
        text_style=ft.TextStyle(color=ft.Colors.ORANGE),
    )

    #Установка цвета статуса оплаты для выпадающего списка
    def update_payment_status_color(e):
        if payment_status_dropdown.value == "Оплачено":
            payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.GREEN)
        elif payment_status_dropdown.value == "Не оплачено":
            payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.RED)
        elif payment_status_dropdown.value == "Долг":
            payment_status_dropdown.text_style = ft.TextStyle(color=ft.Colors.ORANGE)            
        page.update()
 
    # Выпадающий список - статус оплаты
    payment_status_dropdown = ft.Dropdown(
        label="Статус оплаты",
        width=200,
        options=[
            ft.dropdown.Option("Оплачено"),
            ft.dropdown.Option("Не оплачено"),
            ft.dropdown.Option("Долг"),
        ],
        value = "Не оплачено",
        on_change=update_payment_status_color,
        text_style=ft.TextStyle(color=ft.Colors.RED),
    )

    payment_amount_input = ft.TextField(
        label="Сумма оплаты",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )

    # Функция для обработки нажатия кнопки "Добавить"
    def add_order(e):
        order_id = order_id_input.value.strip()
        order_date = order_date_input.value.strip()
        client_name = client_name_input.value.strip()
        work_status = work_status_dropdown.value
        payment_status = payment_status_dropdown.value
        payment_amount = payment_amount_input.value.strip()

        # Проверка заполнения всех полей
        if not all([order_id, order_date, client_name, work_status, payment_status, payment_amount]):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Заполните все поля", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Проверка формата ID заказа
        if not order_id.isdigit():
            page.snack_bar = ft.SnackBar(
                content=ft.Text("ID заказа должно быть числом", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Проверка формата даты
        try:
            datetime.strptime(order_date, "%d.%m.%Y")
        except ValueError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Неверный формат даты. Используйте ДД.ММ.ГГГГ", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Проверка формата суммы оплаты
        try:
            payment_amount = float(payment_amount)
        except ValueError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Сумма оплаты должна быть числом", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
                )
            page.snack_bar.open = True
            page.update()
            return
        
        # Добавление данных в базу данных
        add_order_to_db(order_id, order_date, client_name, work_status, payment_status, payment_amount)

        # Обновление таблицы
        data_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(order_id, color=ft.Colors.YELLOW)),
                    ft.DataCell(ft.Text(order_date, color=ft.Colors.YELLOW)),
                    ft.DataCell(ft.Text(client_name, color=ft.Colors.YELLOW)),
                    ft.DataCell(ft.Text(work_status, color=ft.Colors.YELLOW)),
                    ft.DataCell(ft.Text(payment_status, color=ft.Colors.YELLOW)),
                    ft.DataCell(ft.Text(f"{payment_amount:.2f}", color=ft.Colors.YELLOW))
                ]
            )
        )
        page.update()
        order_id_input.value = ""
        order_date_input.value = ""
        client_name_input.value = ""
        work_status_dropdown.value = "В работе"
        payment_status_dropdown.value = "Не оплачено"
        payment_amount_input.value = ""

    # Кнопка для добавления данных
    add_button = ft.ElevatedButton(
        text="Добавить",
        on_click=add_order,
        width=200,
        height=50,
        style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=7)
        ),
    )

    # Результат агрегации
    aggregation_result = ft.TextField(
        label="Результат агрегации",
        width=550,
        read_only=True,
        multiline=True,
        min_lines=2,
        max_lines=5,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width=2,
        border_radius=10,
    )

    # Функции для кнопок агрегации
    def total_handler(e):
        total = get_total_payment()
        aggregation_result.value = f"Общая сумма оплаты: {total:.2f} руб."
        page.update()

    def average_handler(e):
        average = get_average_payment()
        aggregation_result.value = f"Средняя сумма оплаты: {average:.2f} руб."
        page.update()

    def max_handler(e):
        max_payment = get_max_payment()
        if not max_payment:
            aggregation_result.value = "Нет данных"
        else:
            result_lines = []
            for row in max_payment:
                result_lines.append(f"Клиент: {row['client_name']}\nСумма: {row['payment_amount']:.2f} руб.")
            aggregation_result.value = "\n\n".join(result_lines)
        page.update()

    def min_handler(e):
        min_payment = get_min_payment()
        if not min_payment:
            aggregation_result.value = "Нет данных"
        else:
            result_lines = []
            for row in min_payment:
                result_lines.append(f"Клиент: {row['client_name']}\nСумма: {row['payment_amount']:.2f} руб.")
            aggregation_result.value = "\n\n".join(result_lines)
        page.update()

    


    # Кнопки
    total_button = ft.ElevatedButton(
        text = "Сумма",
        on_click=total_handler,
        width=150,
        style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    average_button = ft.ElevatedButton(
        text = "Среднее",
        on_click=average_handler,
        width=150,
        style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    max_button = ft.ElevatedButton(
        text = "Максимальное",
        on_click=max_handler,
        width=150,
        style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7))
    )

    min_button = ft.ElevatedButton(
        text = "Минимальное",
        on_click=min_handler,
        width=150,
        style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7))
    )



    # Содержимое первой вкладки
    app_content = ft.Column(
        [
            ft.Row(
                [
                    order_id_input,
                    order_date_input,
                    client_name_input,
                    payment_amount_input
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    work_status_dropdown,
                    payment_status_dropdown,
                    add_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Column([data_table], scroll=ft.ScrollMode.ALWAYS)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Содержимое второй вкладки
    def handler_export(e):
        try:
            file_path = export_to_csv()
            if file_path:
                page.set_clipboard(file_path)
                page.launch_url(f"file://{os.path.abspath(file_path)}")
                page.snack_bar = ft.SnackBar(
                    ft.Text("CSV файл успешно создан и доступен для скачивания", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN,
                    duration=2000,
                )
            else:
                page.snack_bar= ft.SnackBar(
                    ft.Text("Ошибка при экспорте в CSV", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED,
                    duration=2000,
                )
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Ошибка при экспорте в CSV: {ex}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
        page.snack_bar.open = True
        page.update()
   

    export_text = ft.Text(
        "Нажмите на кнопку, чтобы экспортировать в CSV файл",
        color=ft.Colors.YELLOW,
        size=20,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    export_button = ft.ElevatedButton(
        content=ft.Text("Экспортировать", size=20, color=ft.Colors.WHITE),
        on_click=handler_export,
        width=400,
        height=50,
        style = ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=7),
        ),
    )

    export_content = ft.Column(
        [
            export_text,
            export_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
        expand=True
    )

    # Содержмое третье вкладки
    search_input = ft.TextField(
        label="Поиск",
        hint_text="Введите имя клиента",
        width=400,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )

    search_results_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID заказа", color=ft.Colors.YELLOW,size=18.5)),
            ft.DataColumn(ft.Text("Дата заказа", color=ft.Colors.YELLOW,size=18.5)),
            ft.DataColumn(ft.Text("Имя клиента", color=ft.Colors.YELLOW,size=18.5)),
            ft.DataColumn(ft.Text("Статус работы", color=ft.Colors.YELLOW,size=18.5)),
            ft.DataColumn(ft.Text("Статус оплаты", color=ft.Colors.YELLOW,size=18.5)),
            ft.DataColumn(ft.Text("Сумма оплаты", color=ft.Colors.YELLOW,size=18.5)),
        ],
        rows=[]
    )

    # Функция поиска
    def handle_search(e):
        client_name = search_input.value.strip()
        if not client_name:
            page.snack_bar = ft.SnackBar(ft.Text("Поле поиска не может быть пустым", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED,duration=2000)
            page.snack_bar.open = True
            page.update()
            return
        
        results = search_orders_by_client_name(client_name)
        search_results_table.rows.clear()
        for row in results:
            search_results_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row["order_id"], color=ft.Colors.BLUE, size=20)),
                        ft.DataCell(ft.Text(row["order_date"], color=ft.Colors.BLUE, size=20)),
                        ft.DataCell(ft.Text(row["client_name"], color=ft.Colors.BLUE, size=20)),
                        ft.DataCell(ft.Text(row["work_status"], color=ft.Colors.BLUE, size=20)),
                        ft.DataCell(ft.Text(row["payment_status"], color=ft.Colors.BLUE, size=20)),
                        ft.DataCell(ft.Text(f"{row['payment_amount']:.2f}", color=ft.Colors.BLUE, size=20))
                    ]
                )
            )
        page.update()
    
    search_button = ft.ElevatedButton(
        content=ft.Text("Поиск", size=20, color=ft.Colors.WHITE),
        on_click=handle_search,
        width=200,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE, shape=ft.RoundedRectangleBorder(radius=7)),
    )

    search_content = ft.Column(
        [
            search_input,
            search_button,
            ft.Column([search_results_table], scroll=ft.ScrollMode.ALWAYS)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )

    # Содержимое вкладки "Агрегация данных"
    aggregation_content = ft.Column(
        [
            aggregation_result,
            ft.Row(
                [total_button, average_button],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [max_button, min_button],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )


    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Заказы", content=app_content),
            ft.Tab(text="Экспортировать", content=export_content),
            ft.Tab(text="Поиск", content=search_content),
            ft.Tab(text="Агрегация данных", content=aggregation_content),
            ft.Tab(text="Редактирование", content=create_edit_tab(page)),
        ],
        expand=True,
    )

    page.add(tabs)



if __name__ == "__main__":
    ft.app(target=main)