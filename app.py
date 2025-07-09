import flet as ft
import os
import sqlite3
from datetime import datetime
from edit_table import create_edit_tab
from database import (
    init_db,
    add_order_to_db,
    export_to_csv,
    get_total_payment,
    get_average_payment,
    get_max_payment,
    get_min_payment,
    search_orders_by_client_name,
    get_all_orders,
)

# Основное приложение
def main(page: ft.Page):
    page.title = "User table"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK

    # Инициализация базы данных
    init_db()

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

    # Функция для загрузки всех заказов в таблицу
    def load_all_orders():
        data_table.rows.clear()
        all_orders = get_all_orders()
        for order in all_orders:
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(order["order_id"]), color=ft.Colors.YELLOW)),
                        ft.DataCell(ft.Text(order["order_date"], color=ft.Colors.YELLOW)),
                        ft.DataCell(ft.Text(order["client_name"], color=ft.Colors.YELLOW)),
                        ft.DataCell(ft.Text(order["work_status"], color=ft.Colors.YELLOW)),
                        ft.DataCell(ft.Text(order["payment_status"], color=ft.Colors.YELLOW)),
                        ft.DataCell(ft.Text(f"{order['payment_amount']:.2f}", color=ft.Colors.YELLOW))
                    ]
                )
            )
        page.update()

    # Поля для ввода данных
    order_id_input = ft.TextField(
        label="ID заказа",
        width=200,
        height=50,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )

    def handle_date_change(e):
        order_date_input.value = date_picker.value.strftime("%d.%m.%Y")
        page.update()

    def open_date_picker(e):
        date_picker.open = True
        page.update()

    date_picker = ft.DatePicker(
        on_change=handle_date_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
        help_text="Выберите дату заказа"
    )
    page.overlay.append(date_picker)

    order_date_input = ft.TextField(
        label="Дата заказа",
        width=200,
        height=50,
        hint_text="ДД.ММ.ГГГГ",
        read_only=True, # Сделаем поле только для чтения, чтобы ввод был только через календарь
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10,
        # Добавим иконку календаря для вызова DatePicker
        suffix=ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=open_date_picker, icon_color=ft.Colors.BLUE),
    ) 


    client_name_input = ft.TextField(
        label="Имя клиента",
        width=200,
        height=50,
        text_style=ft.TextStyle(color=ft.Colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.YELLOW,
        border_width= 2,
        border_radius=10
    )
    
    # --- Рефакторинг: используем словари для цветов ---
    WORK_STATUS_COLORS = {
        "В работе": ft.Colors.ORANGE,
        "Выполнено": ft.Colors.GREEN,
        "Отменено": ft.Colors.RED,
    }
    
    #Установка цвета статуса работы для выпадающего списка
    def update_work_status_color(e):
        status = work_status_dropdown.value
        color = WORK_STATUS_COLORS.get(status, ft.Colors.WHITE)
        work_status_dropdown.text_style = ft.TextStyle(color=color)
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
    
    PAYMENT_STATUS_COLORS = {
        "Оплачено": ft.Colors.GREEN,
        "Не оплачено": ft.Colors.RED,
        "Долг": ft.Colors.ORANGE,
    }
    
    #Установка цвета статуса оплаты для выпадающего списка
    def update_payment_status_color(e):
        status = payment_status_dropdown.value
        color = PAYMENT_STATUS_COLORS.get(status, ft.Colors.WHITE)
        payment_status_dropdown.text_style = ft.TextStyle(color=color)
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
        height=50,
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
        
        # Добавление данных в базу данных с обработкой ошибки уникальности
        try:
            add_order_to_db(int(order_id), order_date, client_name, work_status, payment_status, payment_amount)
        except sqlite3.IntegrityError:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Заказ с ID {order_id} уже существует!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED,
                duration=2000,
            )
            page.snack_bar.open = True
            order_id_input.focus()
            page.update()
            return


        # Обновление таблицы и очистка полей
        load_all_orders()
        order_id_input.value = ""
        order_date_input.value = ""
        client_name_input.value = ""
        work_status_dropdown.value = "В работе"
        payment_status_dropdown.value = "Не оплачено"
        payment_amount_input.value = ""
        update_work_status_color(None)
        update_payment_status_color(None)
        order_id_input.focus()
        page.update()

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
            ft.Container(
                content=ft.Row(
                    [
                        work_status_dropdown,
                        payment_status_dropdown,
                        add_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                margin=ft.margin.only(top=10)
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
            ft.Tab(text="Редактирование", content=create_edit_tab(page, load_all_orders)),
        ],
        expand=True,
    )

    # Первоначальная загрузка данных
    load_all_orders()

    page.add(tabs)


if __name__ == "__main__":
    ft.app(target=main)