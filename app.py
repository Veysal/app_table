import flet as ft

# Основное приложение
def main(page: ft.Page):
    page.title = "User table"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLACK

    #Создание таблицы для отображения данных
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID заказа", color=ft.colors.YELLOW)),
            ft.DataColumn(ft.Text("Дата заказа", color=ft.colors.YELLOW)),
            ft.DataColumn(ft.Text("Имя клиента", color=ft.colors.YELLOW)),
            ft.DataColumn(ft.Text("Статус работы", color=ft.colors.YELLOW)),
            ft.DataColumn(ft.Text("Статус оплаты", color=ft.colors.YELLOW)),
            ft.DataColumn(ft.Text("Сумма оплаты", color=ft.colors.YELLOW)),
        ],
        rows=[]
    )

    # Поля для ввода данных
    order_id_input = ft.TextField(
        label="ID заказа",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.YELLOW,
        border_width= 2,
        border_radius=10
    )
    
    order_date_input = ft.TextField(
        label="Дата заказа",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.YELLOW,
        border_width= 2,
        border_radius=10
    ) 


    client_name_input = ft.TextField(
        label="Имя клиента",
        width=200,
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.YELLOW,
        border_width= 2,
        border_radius=10
    )


    #Установка цвета статуса работы для выпадающего списка
    def update_work_status_color(e):
        if work_status_dropdown.value == "В работе":
            work_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.ORANGE)
        elif work_status_dropdown.value == "Выполнено":
            work_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.GREEN)
        elif work_status_dropdown.value == "Отменено":
            work_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.RED)            
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
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
    )

    #Установка цвета статуса оплаты для выпадающего списка
    def update_payment_status_color(e):
        if payment_status_dropdown.value == "Оплачено":
            payment_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.GREEN)
        elif payment_status_dropdown.value == "Не оплачено":
            payment_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.RED)
        elif payment_status_dropdown.value == "Долг":
            payment_status_dropdown.text_style.color = ft.TextStyle(color=ft.colors.ORANGE)            
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
        text_style=ft.TextStyle(color=ft.colors.RED),
        on_change=update_payment_status_color
    )

    payment_amount_input = ft.TextField(
        label="Сумма оплаты",
        width=200,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.colors.YELLOW),
        border = ft.InputBorder.OUTLINE,
        border_color=ft.colors.BLUE,
        focused_border_color=ft.colors.YELLOW,
        border_width= 2,
        border_radius=10
    )



    # Содержимое первой вкладки
    app_content = ft.Column(
        [
            ft.Row(
                [
                    order_id_input,
                    order_date_input,
                    client_name_input,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Заказы", content=app_content)
        ],
        expand=True,
    )

    page.add(tabs)



if __name__ == "__main__":
    ft.app(target=main)