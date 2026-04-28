import flet as ft
import os
import sqlite3
from datetime import datetime
from edit_table import create_edit_tab
from analytics_tab import create_analytics_tab
from database import (
    init_db,
    add_order_to_db,
    export_to_csv,
    search_orders_by_client_name,
    get_all_orders,
    get_aggregation_summary,
)

# Основное приложение
def main(page: ft.Page):
    page.title = "User table"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK

    # Инициализация базы данных
    init_db()

    # --- Сортировка таблицы ---
    # Переменные для хранения состояния сортировки
    sort_column_name = "id"
    sort_ascending = True

    def handle_sort(e: ft.DataColumnSortEvent):
        nonlocal sort_column_name, sort_ascending

        # Карта для сопоставления индекса колонки с именем в БД
        column_map = {
            0: "order_id",
            1: "order_date",
            2: "client_name",
            3: "work_status",
            4: "payment_status",
            5: "payment_amount",
        }
        current_column_name = column_map.get(e.column_index)

        # Обновляем состояние сортировки
        if sort_column_name == current_column_name:
            sort_ascending = not sort_ascending
        else:
            sort_column_name = current_column_name
            sort_ascending = True

        # Обновляем визуальные индикаторы сортировки в заголовках
        for i, col in enumerate(data_table.columns):
            col.sort_ascending = sort_ascending if i == e.column_index else None

        load_all_orders()

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID заказа", color=ft.Colors.YELLOW), on_sort=handle_sort, numeric=True),
            ft.DataColumn(ft.Text("Дата заказа", color=ft.Colors.YELLOW), on_sort=handle_sort),
            ft.DataColumn(ft.Text("Имя клиента", color=ft.Colors.YELLOW), on_sort=handle_sort),
            ft.DataColumn(ft.Text("Статус работы", color=ft.Colors.YELLOW), on_sort=handle_sort),
            ft.DataColumn(ft.Text("Статус оплаты", color=ft.Colors.YELLOW), on_sort=handle_sort),
            ft.DataColumn(ft.Text("Сумма оплаты", color=ft.Colors.YELLOW), on_sort=handle_sort, numeric=True),
        ],
        rows=[]
    )

    # Функция для загрузки всех заказов в таблицу
    def load_all_orders():
        data_table.rows.clear()
        # Передаем параметры сортировки в функцию получения данных
        all_orders = get_all_orders(sort_column=sort_column_name, sort_ascending=sort_ascending)
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

    # Функция поиска
    def handle_search(e):
        """Динамический поиск, срабатывающий при изменении текста в поле ввода."""
        client_name = search_input.value.strip()
        search_results_table.rows.clear()

        if client_name:  # Выполняем поиск, только если поле не пустое
            results = search_orders_by_client_name(client_name)
            for row in results:
                search_results_table.rows.append(
                    ft.DataRow(
                        cells=[
                            # Исправлена ошибка: ID заказа нужно преобразовать в строку
                            ft.DataCell(ft.Text(str(row["order_id"]), color=ft.Colors.BLUE, size=20)),
                            ft.DataCell(ft.Text(row["order_date"], color=ft.Colors.BLUE, size=20)),
                            ft.DataCell(ft.Text(row["client_name"], color=ft.Colors.BLUE, size=20)),
                            ft.DataCell(ft.Text(row["work_status"], color=ft.Colors.BLUE, size=20)),
                            ft.DataCell(ft.Text(row["payment_status"], color=ft.Colors.BLUE, size=20)),
                            ft.DataCell(ft.Text(f"{row['payment_amount']:.2f}", color=ft.Colors.BLUE, size=20))
                        ]
                    )
                )
        page.update()

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
        border_radius=10,
        on_change=handle_search, # Добавляем обработчик on_change
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

    search_content = ft.Column(
        [
            search_input,
            # Кнопка "Поиск" больше не нужна, так как поиск стал динамическим
            ft.Column([search_results_table], scroll=ft.ScrollMode.ALWAYS)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )

    # --- Содержимое вкладки "Агрегация данных" ---

    # Вспомогательная функция для создания карточек со статистикой
    def create_stat_card(title: str, value: str, color: str, width: int = 200):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color, text_align=ft.TextAlign.CENTER),
                    ft.Text(title, size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=20,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_800),
            border_radius=10,
            width=width,
            alignment=ft.alignment.center,
        )

    # Создаем элементы управления для карточек, но пока без значений
    total_orders_card = create_stat_card("Всего заказов", "...", ft.Colors.WHITE)
    total_payment_card = create_stat_card("Общая выручка", "...", ft.Colors.GREEN_ACCENT_400)
    average_payment_card = create_stat_card("Средний чек", "...", ft.Colors.CYAN_ACCENT_400)
    in_progress_card = create_stat_card("В работе", "...", ft.Colors.ORANGE)
    completed_card = create_stat_card("Выполнено", "...", ft.Colors.GREEN)

    def update_aggregation_data(e=None):
        """Загружает и обновляет данные на карточках статистики."""
        summary = get_aggregation_summary()
        total_orders_card.content.controls[0].value = str(summary.get("total_orders", 0))
        total_payment_card.content.controls[0].value = f"{summary.get('total_payment', 0):.2f} ₽"
        average_payment_card.content.controls[0].value = f"{summary.get('average_payment', 0):.2f} ₽"
        in_progress_card.content.controls[0].value = str(summary.get("in_progress_orders", 0))
        completed_card.content.controls[0].value = str(summary.get("completed_orders", 0))
        page.update()

    refresh_button = ft.IconButton(
        icon=ft.Icons.REFRESH,
        on_click=update_aggregation_data,
        tooltip="Обновить данные",
        icon_color=ft.Colors.BLUE,
    )

    aggregation_content = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Ключевые показатели", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW),
                    refresh_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=640 # Ширина равна сумме карточек и отступов
            ),
            ft.Row(
                [total_orders_card, total_payment_card, average_payment_card],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Row(
                [in_progress_card, completed_card],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )

    # --- Вкладка "Аналитика" ---
    analytics_tab_content, update_analytics_chart = create_analytics_tab(page)

    def on_tab_change(e):
        # Обновляем данные на вкладке "Агрегация", когда она становится активной
        if e.control.selected_index == 3:
            update_aggregation_data()
        # Обновляем данные на вкладке "Аналитика"
        elif e.control.selected_index == 4:
            update_analytics_chart()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Заказы", content=app_content),
            ft.Tab(text="Экспортировать", content=export_content),
            ft.Tab(text="Поиск", content=search_content),
            ft.Tab(text="Агрегация данных", content=aggregation_content),
            ft.Tab(text="Аналитика", content=analytics_tab_content),
            ft.Tab(text="Редактирование", content=create_edit_tab(page, load_all_orders))
        ],
        on_change=on_tab_change,
        expand=True,
    )

    # Первоначальная загрузка данных
    load_all_orders()

    page.add(tabs)


if __name__ == "__main__":
    ft.app(target=main)