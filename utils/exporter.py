import io
import xlsxwriter
from collections import defaultdict


def export_expenses_to_excel(expenses, period_name):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})

    # Лист "Расходы"
    sheet_expenses = workbook.add_worksheet("Расходы")
    headers = ["Дата", "Сумма", "Категория", "Комментарий"]
    sheet_expenses.write_row("A1", headers)

    for i, item in enumerate(expenses, start=1):
        sheet_expenses.write(i, 0, item["date"])
        sheet_expenses.write(i, 1, item["amount"])
        sheet_expenses.write(i, 2, item["category_name"])
        sheet_expenses.write(i, 3, item.get("comment", "") or "")

    row_total = len(expenses) + 1
    sheet_expenses.write(row_total, 0, "Итого:")
    sheet_expenses.write_formula(row_total, 1, f"=SUM(B2:B{row_total})")

    # Лист "Статистика"
    category_totals = defaultdict(float)
    total_sum = 0
    for item in expenses:
        category_totals[item["category_name"]] += item["amount"]
        total_sum += item["amount"]

    stats = [(cat, amount, round(amount / total_sum * 100, 1)) for cat, amount in category_totals.items()]
    sheet_stats = workbook.add_worksheet("Статистика")
    sheet_stats.write_row("A1", ["Категория", "Сумма", "%"])
    for i, (cat, amount, percent) in enumerate(stats, start=1):
        sheet_stats.write(i, 0, cat)
        sheet_stats.write(i, 1, amount)
        sheet_stats.write(i, 2, percent)

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': 'Распределение расходов',
        'categories': f'=Статистика!$A$2:$A${1 + len(stats)}',
        'values': f'=Статистика!$B$2:$B${1 + len(stats)}'
    })
    chart.set_title({'name': 'Распределение расходов'})
    chart.set_style(10)
    sheet_stats.insert_chart("E2", chart)

    workbook.close()
    output.seek(0)
    return output
