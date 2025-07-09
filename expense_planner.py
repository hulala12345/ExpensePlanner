import json
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

DATA_FILE = 'data.json'
CATEGORIES = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Other']


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'expenses': [], 'budgets': {c: 0 for c in CATEGORIES}}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


data = load_data()

root = tk.Tk()
root.title('ExpensePlanner')

amount_var = tk.StringVar()
date_var = tk.StringVar(value=date.today().isoformat())
category_var = tk.StringVar(value=CATEGORIES[0])
desc_var = tk.StringVar()

budget_vars = {c: tk.StringVar(value=str(data['budgets'].get(c, 0))) for c in CATEGORIES}


def add_expense():
    try:
        amount = float(amount_var.get())
    except ValueError:
        messagebox.showerror('Error', 'Invalid amount')
        return
    entry = {
        'amount': amount,
        'date': date_var.get(),
        'category': category_var.get(),
        'description': desc_var.get()
    }
    data['expenses'].append(entry)
    save_data(data)
    update_remaining()
    messagebox.showinfo('Expense added', 'Expense recorded.')


def update_remaining():
    totals = {c: 0 for c in CATEGORIES}
    month_prefix = date.today().isoformat()[:7]
    for e in data['expenses']:
        if e['date'].startswith(month_prefix):
            totals[e['category']] += e['amount']
    warnings = []
    for c in CATEGORIES:
        try:
            limit = float(budget_vars[c].get() or 0)
        except ValueError:
            limit = 0
        spent = totals.get(c, 0)
        if limit > 0 and spent >= 0.8 * limit:
            warnings.append(f'{c} spending at {spent}/{limit}')
    if warnings:
        messagebox.showwarning('Budget Alert', '\n'.join(warnings))


def save_budgets():
    for c in CATEGORIES:
        try:
            data['budgets'][c] = float(budget_vars[c].get())
        except ValueError:
            data['budgets'][c] = 0
    save_data(data)
    messagebox.showinfo('Budgets saved', 'Budgets updated')


def show_charts():
    totals = {c: 0 for c in CATEGORIES}
    month_prefix = date.today().isoformat()[:7]
    for e in data['expenses']:
        if e['date'].startswith(month_prefix):
            totals[e['category']] += e['amount']
    labels = list(totals.keys())
    amounts = list(totals.values())
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].pie(amounts, labels=labels, autopct='%1.1f%%')
    axs[0].set_title('Expense Distribution')
    limits = [data['budgets'].get(c, 0) for c in labels]
    x = range(len(labels))
    axs[1].bar(x, limits, label='Budget')
    axs[1].bar(x, amounts, label='Actual')
    axs[1].set_xticks(range(len(labels)))
    axs[1].set_xticklabels(labels)
    axs[1].legend()
    axs[1].set_title('Budget vs Actual')
    plt.show()


def generate_report():
    month_prefix = date.today().isoformat()[:7]
    totals = {c: 0 for c in CATEGORIES}
    for e in data['expenses']:
        if e['date'].startswith(month_prefix):
            totals[e['category']] += e['amount']
    total_spending = sum(totals.values())
    lines = ['Monthly Report', f'Total spending: {total_spending}']
    for c in CATEGORIES:
        limit = data['budgets'].get(c, 0)
        spent = totals.get(c, 0)
        lines.append(f'{c}: spent {spent} / budget {limit}')
    report = '\n'.join(lines)
    report_window = tk.Toplevel(root)
    report_window.title('Monthly Report')
    tk.Label(report_window, text=report, justify='left').pack(padx=10, pady=10)


frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text='Amount').grid(row=0, column=0)
tk.Entry(frame, textvariable=amount_var).grid(row=0, column=1)

tk.Label(frame, text='Date (YYYY-MM-DD)').grid(row=1, column=0)
tk.Entry(frame, textvariable=date_var).grid(row=1, column=1)

tk.Label(frame, text='Category').grid(row=2, column=0)
category_box = ttk.Combobox(frame, textvariable=category_var, values=CATEGORIES, state='readonly')
category_box.grid(row=2, column=1)

tk.Label(frame, text='Description').grid(row=3, column=0)
tk.Entry(frame, textvariable=desc_var).grid(row=3, column=1)

tk.Button(frame, text='Add Expense', command=add_expense).grid(row=4, column=0, columnspan=2, pady=5)

budget_frame = tk.LabelFrame(root, text='Budgets')
budget_frame.pack(padx=10, pady=10, fill='x')
for i, c in enumerate(CATEGORIES):
    tk.Label(budget_frame, text=c).grid(row=i, column=0, sticky='w')
    tk.Entry(budget_frame, textvariable=budget_vars[c]).grid(row=i, column=1)

tk.Button(budget_frame, text='Save Budgets', command=save_budgets).grid(row=len(CATEGORIES), column=0, columnspan=2, pady=5)


tk.Button(root, text='Show Charts', command=show_charts).pack(pady=5)

tk.Button(root, text='Generate Report', command=generate_report).pack(pady=5)

update_remaining()
root.mainloop()
