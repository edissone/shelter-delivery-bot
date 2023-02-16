import os

from xlsxwriter import Workbook

from src.models.const import OrderStatuses


class ReportBuilder:
    fields = {
        'headers': 'Общее состояние',
        'values': [('Номер заказа', 'number'), ('Оператор', 'supplier'), ('Доставщик', 'deliver'),
                   ('Сумма', 'amount'), ('Тип оплаты', 'payment_type'), ('Код оплаты', 'payment_code'),
                   ('Сдача с', 'payback_from'), ('Сдача', 'payback'), ('Тип доставки', 'delivery_type'),
                   ('Адрес', 'delivery_address'), ('Состояние', 'status'), ('Время', 'date'), ('Имя позиции', ''),
                   ('Кол-во', '')]
    }
    report_states = [('Завершено', 'completed'), ('Отменено', 'declined'), ('Открыто', 'other')]

    @classmethod
    def build_report(cls, data: dict):
        data_dict = {}
        for element in data['data']:
            data_dict[element['date']] = element

        sorted_dates = sorted(data_dict.keys())
        filename = f'resources/report-buffer/{sorted_dates[0]} - {sorted_dates[-1]}.xlsx' if len(
            sorted_dates) > 1 else f'resources/report-buffer/{sorted_dates[0]}.xlsx'

        workbook = Workbook(filename)
        for date in sorted_dates:
            cls.fill_data(data_dict, date, workbook)
        workbook.close()
        result = open(filename, 'rb')
        os.remove(filename)
        return result

    @classmethod
    def fill_data(cls, data_dict, date, workbook):
        entries = data_dict[date]
        row = 0
        column = 0
        sheet = workbook.add_worksheet(name=date)
        header_format = workbook.add_format({'bold': 1})
        header_format.set_top()
        header_format.set_bottom()
        header_format.set_left()
        header_format.set_right()
        cell_format = workbook.add_format()
        cell_format.set_top()
        cell_format.set_bottom()
        cell_format.set_left()
        cell_format.set_right()
        for rs in cls.report_states:
            sheet.write_string(row, 0, cls.fields['headers'], header_format)
            sheet.write_string(row, 1, rs[0], header_format)
            sheet.write_number(row, 2, len(entries[rs[1]]), header_format)

            row += 1
            if len(entries[rs[1]]) >= 1:
                for field in cls.fields['values']:
                    sheet.write(row, column, field[0], header_format)
                    column += 1

                row += 1
                column = 0
                for entry in entries[rs[1]]:
                    for field in cls.fields['values'][:-2]:
                        sheet.write(row, column, cls.translate_value(entry[field[1]]), cell_format)
                        column += 1

                    for position, count in entry['positions'].items():
                        sheet.write(row, column, position, cell_format)
                        sheet.write(row, column + 1, count, cell_format)
                        row += 1
                    column = 0
            sheet.autofit()
            column = 0
            row += 1
        sheet.write(row, column, 'Итого', header_format)
        sheet.write(row, column + 1, entries['total_amount'], header_format)

    @staticmethod
    def translate_value(data):
        if data == 'SELF':
            return 'Самовывоз'
        elif data == 'DELIVERY':
            return 'Доставка'
        else:
            val = OrderStatuses.get_by_name(data)
            return val.label if val is not None else data
