#!/usr/bin/env python3
"""
Программа для извлечения таблиц из PDF документа
с возможностью выбора конкретной таблицы для сохранения в CSV или Excel.
"""

import pdfplumber
import pandas as pd
import sys
import os


def extract_tables_from_pdf(pdf_path):
    """
    Извлекает все таблицы из PDF файла.
    
    Args:
        pdf_path: Путь к PDF файлу
        
    Returns:
        Список таблиц (каждая таблица - список строк, где каждая строка - список ячеек)
    """
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table in tables:
                if table:  # Проверяем, что таблица не пустая
                    all_tables.append({
                        'page': page_num,
                        'table_data': table
                    })
    
    return all_tables


def display_table_preview(table_data, max_rows=5, max_cols=5):
    """
    Отображает превью таблицы.
    
    Args:
        table_data: Данные таблицы (список строк)
        max_rows: Максимальное количество строк для отображения
        max_cols: Максимальное количество колонок для отображения
    """
    print("\n" + "="*60)
    
    for i, row in enumerate(table_data[:max_rows]):
        if row:
            cells = [str(cell).strip() if cell else '' for cell in row[:max_cols]]
            print(f"  {' | '.join(cells)}")
            if len(row) > max_cols:
                print(f"  ... и ещё {len(row) - max_cols} колонок")
    
    if len(table_data) > max_rows:
        print(f"  ... и ещё {len(table_data) - max_rows} строк")
    
    print("="*60)


def save_table_to_csv(table_data, output_path):
    """
    Сохраняет таблицу в CSV формат.
    
    Args:
        table_data: Данные таблицы
        output_path: Путь для сохранения файла
    """
    df = pd.DataFrame(table_data)
    df.to_csv(output_path, index=False, header=False, encoding='utf-8-sig')
    print(f"✓ Таблица сохранена в CSV: {output_path}")


def save_table_to_excel(table_data, output_path):
    """
    Сохраняет таблицу в Excel формат.
    
    Args:
        table_data: Данные таблицы
        output_path: Путь для сохранения файла
    """
    df = pd.DataFrame(table_data)
    df.to_excel(output_path, index=False, header=False)
    print(f"✓ Таблица сохранена в Excel: {output_path}")


def main():
    print("="*60)
    print("Программа для извлечения таблиц из PDF")
    print("="*60)
    
    # Запрос пути к PDF файлу
    while True:
        pdf_path = input("\nВведите путь к PDF файлу: ").strip()
        if pdf_path.startswith('"') and pdf_path.endswith('"'):
            pdf_path = pdf_path[1:-1]
        
        if os.path.exists(pdf_path):
            break
        else:
            print(f"❌ Файл не найден: {pdf_path}")
            print("   Попробуйте снова или нажмите Ctrl+C для выхода.")
    
    print(f"\n📄 Обработка файла: {pdf_path}")
    print("⏳ Извлечение таблиц...")
    
    try:
        all_tables = extract_tables_from_pdf(pdf_path)
    except Exception as e:
        print(f"❌ Ошибка при обработке PDF: {e}")
        sys.exit(1)
    
    if not all_tables:
        print("\n❌ Таблицы не найдены в данном PDF файле.")
        sys.exit(0)
    
    print(f"\n✅ Найдено таблиц: {len(all_tables)}")
    
    # Отображение списка таблиц
    print("\n" + "-"*60)
    print("СПИСОК ТАБЛИЦ:")
    print("-"*60)
    
    for idx, table_info in enumerate(all_tables, 1):
        table_data = table_info['table_data']
        num_rows = len(table_data)
        num_cols = max(len(row) for row in table_data) if table_data else 0
        
        print(f"\n[Таблица #{idx}]")
        print(f"  Страница: {table_info['page']}")
        print(f"  Размер: {num_rows} строк × {num_cols} колонок")
        print(f"  Превью:")
        display_table_preview(table_data)
    
    # Выбор таблицы для сохранения
    while True:
        try:
            choice = input(f"\nВведите номер таблицы для сохранения (1-{len(all_tables)}) или 0 для выхода: ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                print("Выход из программы.")
                sys.exit(0)
            elif 1 <= choice_num <= len(all_tables):
                selected_table = all_tables[choice_num - 1]
                break
            else:
                print(f"❌ Введите число от 0 до {len(all_tables)}")
        except ValueError:
            print("❌ Пожалуйста, введите корректное число.")
    
    # Выбор формата сохранения
    print("\nВыберите формат сохранения:")
    print("  1. CSV")
    print("  2. Excel (.xlsx)")
    
    while True:
        format_choice = input("\nВведите номер формата (1 или 2): ").strip()
        if format_choice == '1':
            output_format = 'csv'
            break
        elif format_choice == '2':
            output_format = 'xlsx'
            break
        else:
            print("❌ Введите 1 или 2")
    
    # Генерация имени выходного файла
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    if output_format == 'csv':
        output_path = f"{base_name}_table_{choice_num}.csv"
    else:
        output_path = f"{base_name}_table_{choice_num}.xlsx"
    
    output_path = input(f"\nВведите имя выходного файла [{output_path}]: ").strip() or output_path
    
    # Сохранение таблицы
    selected_data = selected_table['table_data']
    
    if output_format == 'csv':
        if not output_path.endswith('.csv'):
            output_path += '.csv'
        save_table_to_csv(selected_data, output_path)
    else:
        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'
        save_table_to_excel(selected_data, output_path)
    
    print("\n" + "="*60)
    print("Готово!")
    print("="*60)


if __name__ == "__main__":
    main()
