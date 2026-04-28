import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import matplotlib
import matplotlib.pyplot as plt
from database import get_revenue_by_month, get_status_distribution

# Используем бэкенд, который не требует GUI (например, TkAgg, WXAgg)
matplotlib.use("agg")

# Цвета для статусов, чтобы они совпадали с остальным интерфейсом
STATUS_COLORS = {
    "В работе": "#FF8F00",  # ft.Colors.ORANGE
    "Выполнено": "#388E3C", # ft.Colors.GREEN
    "Отменено": "#D32F2F",   # ft.Colors.RED
}

def create_analytics_tab(page: ft.Page):
    """Создает вкладку "Аналитика" с графиками."""

    # Элементы для отображения графиков
    revenue_chart = MatplotlibChart(expand=True)
    status_chart = MatplotlibChart(expand=True)

    def update_analytics(e=None):
        """Получает данные и обновляет оба графика."""
        
        # --- 1. Обновление графика выручки (Bar chart) ---
        revenue_data = get_revenue_by_month()
        revenue_chart.figure.clear()
        ax_rev = revenue_chart.figure.add_subplot(111)
        ax_rev.set_facecolor("#202020")
        revenue_chart.figure.set_facecolor("#202020")

        if not revenue_data:
            ax_rev.text(0.5, 0.5, "Нет данных по выручке",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax_rev.transAxes, fontsize=14, color='grey')
        else:
            months = [row['month'] for row in revenue_data]
            revenues = [row['total_revenue'] for row in revenue_data]
            ax_rev.bar(months, revenues, color='#0078D7')
            ax_rev.tick_params(axis='x', labelrotation=45, colors='white')
            ax_rev.tick_params(axis='y', colors='white')
            ax_rev.spines['top'].set_visible(False)
            ax_rev.spines['right'].set_visible(False)
            ax_rev.spines['bottom'].set_color('grey')
            ax_rev.spines['left'].set_color('grey')
            ax_rev.set_title("Выручка по месяцам", color="yellow")
            ax_rev.set_ylabel("Сумма, ₽", color="white")
            revenue_chart.figure.tight_layout()

        # --- 2. Обновление диаграммы статусов (Pie chart) ---
        status_data = get_status_distribution()
        status_chart.figure.clear()
        ax_stat = status_chart.figure.add_subplot(111)
        ax_stat.set_facecolor("#202020")
        status_chart.figure.set_facecolor("#202020")

        if not status_data:
            ax_stat.text(0.5, 0.5, "Нет данных по статусам",
                         horizontalalignment='center', verticalalignment='center',
                         transform=ax_stat.transAxes, fontsize=14, color='grey')
        else:
            labels = [row['work_status'] for row in status_data]
            sizes = [row['count'] for row in status_data]
            colors = [STATUS_COLORS.get(label, "#FFFFFF") for label in labels]
            
            wedges, texts, autotexts = ax_stat.pie(
                sizes, autopct='%1.1f%%', startangle=140, colors=colors,
                pctdistance=0.85
            )
            # Стилизация текста на диаграмме
            plt.setp(texts, color='white', weight="bold")
            plt.setp(autotexts, color='black', weight="bold")

            ax_stat.axis('equal')  # Круговая диаграмма
            ax_stat.legend(wedges, labels,
                          title="Статусы",
                          loc="center left",
                          bbox_to_anchor=(0.9, 0, 0.5, 1),
                          labelcolor='white'
                          )
            ax_stat.set_title("Распределение статусов", color="yellow", pad=20)

        page.update()

    # Кнопка для обновления
    refresh_button = ft.IconButton(
        icon=ft.Icons.REFRESH,
        on_click=update_analytics,
        tooltip="Обновить графики",
        icon_color=ft.Colors.BLUE,
    )

    # Инициализируем пустую фигуру при создании
    revenue_chart.figure = plt.figure()
    status_chart.figure = plt.figure()

    # Содержимое вкладки
    analytics_content = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Аналитика", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.YELLOW),
                    refresh_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(
                controls=[
                    revenue_chart,
                    status_chart,
                ],
                expand=True,
            ),
        ],
        expand=True,
    )

    # Возвращаем содержимое и функцию обновления, чтобы ее можно было вызвать извне
    return analytics_content, update_analytics