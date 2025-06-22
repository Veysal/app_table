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