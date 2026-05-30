
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import random
import string


conn = None
cursor = None
current_user_id = None
current_user_name = None
current_user_role = None
cart = []
current_root = None
products_frame = None
cart_listbox = None
cart_total_label = None
search_entry = None
category_var = None
canvas = None
products_frame_inner = None



def init_db():
    global conn, cursor
    conn = sqlite3.connect('green_garden.db')
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name VARCHAR(20) NOT NULL UNIQUE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role_id INTEGER NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES roles(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS growing_conditions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        climate_zone VARCHAR(50) NOT NULL,
        soil_type VARCHAR(50) NOT NULL,
        sunlight VARCHAR(30) NOT NULL,
        watering VARCHAR(30) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article VARCHAR(30) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(20) NOT NULL,
        brand VARCHAR(50) NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        category VARCHAR(50) NOT NULL,
        description TEXT,
        image_path VARCHAR(255),
        planting_season VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS product_condition_link (
        product_id INTEGER NOT NULL,
        condition_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, condition_id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (condition_id) REFERENCES growing_conditions(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) NOT NULL DEFAULT 'new',
        total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
        delivery_address VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        count INTEGER NOT NULL,
        price_at_order DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id))''')

    conn.commit()
    insert_test_data()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def insert_test_data():
    global cursor, conn
    # Вставка ролей
    roles = ['guest', 'client', 'manager', 'admin']
    for role in roles:
        cursor.execute('INSERT OR IGNORE INTO roles (role_name) VALUES (?)', (role,))

    # Получение ID ролей
    cursor.execute('SELECT id, role_name FROM roles')
    roles_dict = {row[1]: row[0] for row in cursor.fetchall()}

    # Вставка пользователей
    users = [
        ('admin_garden', hash_password('GardenAdmin2026!'), roles_dict['admin'], 'Петрова А.В.', '+79991234567'),
        ('manager01', hash_password('Manager#789'), roles_dict['manager'], 'Сидоров Е.К.', '+79997654321'),
        ('client_ivanov', hash_password('Client@321'), roles_dict['client'], 'Иванов Д.М.', '+79991112233')
    ]
    for user in users:
        cursor.execute(
            'INSERT OR IGNORE INTO users (login, password_hash, role_id, full_name, phone) VALUES (?,?,?,?,?)', user)

    # Вставка условий выращивания
    conditions = [
        ('Умеренный', 'Суглинок', 'Солнце', 'Умеренно'),
        ('Тропический', 'Универсальная', 'Полутень', 'Ежедневно'),
        ('Средиземноморский', 'Песчаная', 'Солнце', 'Редко')
    ]
    for cond in conditions:
        cursor.execute(
            'INSERT OR IGNORE INTO growing_conditions (climate_zone, soil_type, sunlight, watering) VALUES (?,?,?,?)',
            cond)

    # Вставка товаров
    products = [
        ('ART001', 'Роза чайная', 'plant', 'Русский сад', 850, 25, 'Цветы', 'Красивая чайная роза', 'Весна'),
        ('ART002', 'Томаты Бычье сердце', 'seed', 'Аэлита', 120, 100, 'Овощи', 'Крупные сладкие томаты', 'Весна'),
        ('ART003', 'Спатифиллум', 'plant', 'Зеленый мир', 1500, 15, 'Комнатные', 'Очищает воздух', 'Круглый год')
    ]
    for prod in products:
        cursor.execute(
            'INSERT OR IGNORE INTO products (article, name, type, brand, price, quantity, category, description, planting_season) VALUES (?,?,?,?,?,?,?,?,?)',
            prod)

    conn.commit()


def get_user(login, password):
    global cursor
    pwd_hash = hash_password(password)
    cursor.execute('''SELECT u.id, u.full_name, r.role_name 
                      FROM users u 
                      JOIN roles r ON u.role_id = r.id 
                      WHERE u.login = ? AND u.password_hash = ?''', (login, pwd_hash))
    return cursor.fetchone()


def register_user(login, password, full_name, phone):
    global cursor, conn
    cursor.execute('SELECT id FROM roles WHERE role_name = "client"')
    role_id = cursor.fetchone()[0]

    try:
        cursor.execute('INSERT INTO users (login, password_hash, role_id, full_name, phone) VALUES (?, ?, ?, ?, ?)',
                       (login, hash_password(password), role_id, full_name, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_products(search=None, category=None):
    global cursor
    query = 'SELECT id, article, name, price, quantity, category FROM products WHERE 1=1'
    params = []

    if search:
        query += ' AND (name LIKE ? OR article LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    if category and category != 'Все':
        query += ' AND category = ?'
        params.append(category)

    cursor.execute(query, params)
    return cursor.fetchall()


def get_all_products():
    global cursor
    cursor.execute('SELECT id, article, name, price, quantity, category FROM products')
    return cursor.fetchall()


def get_categories():
    global cursor
    cursor.execute('SELECT DISTINCT category FROM products')
    return [row[0] for row in cursor.fetchall()]


def update_product(product_id, name, price, quantity):
    global cursor, conn
    cursor.execute('UPDATE products SET name=?, price=?, quantity=? WHERE id=?',
                   (name, price, quantity, product_id))
    conn.commit()


def delete_product(product_id):
    global cursor, conn
    cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()


def add_product(article, name, type_, brand, price, quantity, category, description):
    global cursor, conn
    cursor.execute('''INSERT INTO products (article, name, type, brand, price, quantity, category, description) 
                      VALUES (?,?,?,?,?,?,?,?)''',
                   (article, name, type_, brand, price, quantity, category, description))
    conn.commit()


def create_order(user_id, items, total, address, phone):
    global cursor, conn
    cursor.execute('''INSERT INTO orders (user_id, total_amount, delivery_address, phone) 
                      VALUES (?,?,?,?)''', (user_id, total, address, phone))
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute('''INSERT INTO order_items (order_id, product_id, count, price_at_order) 
                          VALUES (?,?,?,?)''', (order_id, item['product_id'], item['count'], item['price']))

    conn.commit()
    return order_id


def get_orders(user_id=None):
    global cursor
    if user_id:
        cursor.execute(
            'SELECT id, order_date, status, total_amount FROM orders WHERE user_id=? ORDER BY order_date DESC',
            (user_id,))
    else:
        cursor.execute(
            'SELECT o.id, o.order_date, o.status, o.total_amount, u.full_name FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.order_date DESC')
    return cursor.fetchall()


def update_order_status(order_id, status):
    global cursor, conn
    cursor.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()


def delete_order(order_id):
    global cursor, conn
    cursor.execute('DELETE FROM order_items WHERE order_id=?', (order_id,))
    cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
    conn.commit()


# ==================== ФУНКЦИИ ИНТЕРФЕЙСА ====================
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def add_to_cart(product_id, name, price, count):
    global cart
    cart.append({'id': product_id, 'name': name, 'price': price, 'count': count})
    update_cart_display()


def update_cart_display():
    global cart_listbox, cart_total_label, cart
    if cart_listbox:
        cart_listbox.delete(0, tk.END)
        total = 0
        for item in cart:
            cart_listbox.insert(tk.END, f"{item['name']} x{item['count']} = {item['price'] * item['count']} руб.")
            total += item['price'] * item['count']
        cart_total_label.config(text=f"Итого: {total} руб.")


def clear_cart():
    global cart
    cart = []
    update_cart_display()


def checkout():
    global cart, current_user_id, current_root
    if not cart:
        messagebox.showwarning("Корзина пуста", "Добавьте товары в корзину!")
        return

    dialog = tk.Toplevel(current_root)
    dialog.title("Оформление заказа")
    dialog.geometry("400x300")
    dialog.configure(bg='#F8FAF5')

    tk.Label(dialog, text="Адрес доставки:", font=('Arial', 12), bg='#F8FAF5').pack(pady=10)
    address_entry = tk.Entry(dialog, width=40)
    address_entry.pack(pady=5)

    tk.Label(dialog, text="Телефон:", font=('Arial', 12), bg='#F8FAF5').pack(pady=10)
    phone_entry = tk.Entry(dialog, width=40)
    phone_entry.pack(pady=5)

    def submit_order():
        global cart, current_user_id
        total = sum(item['price'] * item['count'] for item in cart)
        order_id = create_order(current_user_id, cart, total, address_entry.get(), phone_entry.get())
        messagebox.showinfo("Успех", f"Заказ №{order_id} оформлен!")
        cart = []
        update_cart_display()
        dialog.destroy()

    tk.Button(dialog, text="Подтвердить заказ", bg='#22C55E', fg='white', command=submit_order).pack(pady=20)


def edit_product(product_id, name, price, quantity):
    dialog = tk.Toplevel(current_root)
    dialog.title("Редактирование товара")
    dialog.geometry("300x250")
    dialog.configure(bg='#F8FAF5')

    tk.Label(dialog, text="Название:", font=('Arial', 12), bg='#F8FAF5').pack(pady=5)
    name_entry = tk.Entry(dialog, width=30)
    name_entry.insert(0, name)
    name_entry.pack(pady=5)

    tk.Label(dialog, text="Цена:", font=('Arial', 12), bg='#F8FAF5').pack(pady=5)
    price_entry = tk.Entry(dialog, width=30)
    price_entry.insert(0, price)
    price_entry.pack(pady=5)

    tk.Label(dialog, text="Количество:", font=('Arial', 12), bg='#F8FAF5').pack(pady=5)
    quantity_entry = tk.Entry(dialog, width=30)
    quantity_entry.insert(0, quantity)
    quantity_entry.pack(pady=5)

    def save():
        update_product(product_id, name_entry.get(), float(price_entry.get()), int(quantity_entry.get()))
        load_products()
        dialog.destroy()
        messagebox.showinfo("Успех", "Товар обновлен!")

    def delete():
        if messagebox.askyesno("Подтверждение", "Удалить товар?"):
            delete_product(product_id)
            load_products()
            dialog.destroy()

    tk.Button(dialog, text="Сохранить", bg='#22C55E', fg='white', command=save).pack(pady=10)
    tk.Button(dialog, text="Удалить", bg='#8B7355', fg='white', command=delete).pack()


def manage_products():
    dialog = tk.Toplevel(current_root)
    dialog.title("Управление товарами")
    dialog.geometry("500x500")
    dialog.configure(bg='#F8FAF5')

    tk.Label(dialog, text="Добавить новый товар", font=('Arial', 14, 'bold'), bg='#F8FAF5').pack(pady=10)

    frame = tk.Frame(dialog, bg='#F8FAF5')
    frame.pack(pady=10)

    fields = [('Артикул:', 'article'), ('Название:', 'name'), ('Тип:', 'type'),
              ('Бренд:', 'brand'), ('Цена:', 'price'), ('Количество:', 'quantity'),
              ('Категория:', 'category'), ('Описание:', 'description')]

    entries = {}
    for i, (label, key) in enumerate(fields):
        tk.Label(frame, text=label, font=('Arial', 10), bg='#F8FAF5').grid(row=i, column=0, pady=5, sticky='e')
        entry = tk.Entry(frame, width=25)
        entry.grid(row=i, column=1, pady=5, padx=10)
        entries[key] = entry

    def add():
        try:
            add_product(
                entries['article'].get(), entries['name'].get(), entries['type'].get(),
                entries['brand'].get(), float(entries['price'].get()), int(entries['quantity'].get()),
                entries['category'].get(), entries['description'].get()
            )
            messagebox.showinfo("Успех", "Товар добавлен!")
            dialog.destroy()
            load_products()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(dialog, text="Добавить товар", bg='#22C55E', fg='white', command=add).pack(pady=20)


def manage_orders():
    dialog = tk.Toplevel(current_root)
    dialog.title("Управление заказами")
    dialog.geometry("800x500")
    dialog.configure(bg='#F8FAF5')

    orders = get_orders()

    tree = ttk.Treeview(dialog, columns=('ID', 'Дата', 'Статус', 'Сумма', 'Клиент'), show='headings', height=20)
    tree.heading('ID', text='№ заказа')
    tree.heading('Дата', text='Дата')
    tree.heading('Статус', text='Статус')
    tree.heading('Сумма', text='Сумма')
    tree.heading('Клиент', text='Клиент')

    tree.column('ID', width=80)
    tree.column('Дата', width=150)
    tree.column('Статус', width=100)
    tree.column('Сумма', width=100)
    tree.column('Клиент', width=200)

    tree.pack(fill='both', expand=True, padx=20, pady=20)

    for order in orders:
        tree.insert('', 'end', values=order)

    def change_status():
        selected = tree.selection()
        if selected:
            order_id = tree.item(selected[0])['values'][0]
            status_dialog = tk.Toplevel(dialog)
            status_dialog.title("Сменить статус")
            status_dialog.geometry("300x150")
            status_dialog.configure(bg='#F8FAF5')

            tk.Label(status_dialog, text="Новый статус:", font=('Arial', 12), bg='#F8FAF5').pack(pady=10)
            status_var = tk.StringVar(value='new')
            status_combo = ttk.Combobox(status_dialog, textvariable=status_var,
                                        values=['new', 'processing', 'shipped', 'completed', 'cancelled'])
            status_combo.pack(pady=10)

            def update():
                update_order_status(order_id, status_var.get())
                messagebox.showinfo("Успех", "Статус обновлен!")
                status_dialog.destroy()
                dialog.destroy()
                manage_orders()

            tk.Button(status_dialog, text="Обновить", bg='#22C55E', fg='white', command=update).pack(pady=10)

    def delete_order_func():
        selected = tree.selection()
        if selected and messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            order_id = tree.item(selected[0])['values'][0]
            delete_order(order_id)
            dialog.destroy()
            manage_orders()

    btn_frame = tk.Frame(dialog, bg='#F8FAF5')
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Изменить статус", bg='#FCD34D', command=change_status).pack(side='left', padx=10)
    tk.Button(btn_frame, text="Удалить заказ", bg='#8B7355', fg='white', command=delete_order_func).pack(side='left',
                                                                                                         padx=10)


def on_canvas_configure(event):
    global canvas, products_frame_inner
    if canvas:
        canvas.configure(scrollregion=canvas.bbox('all'))


def load_products():
    global products_frame_inner, current_user_role, search_entry, category_var

    if not products_frame_inner:
        return

    for widget in products_frame_inner.winfo_children():
        widget.destroy()

    if current_user_role in ['manager', 'admin']:
        search = search_entry.get() if search_entry.get() else None
        category = category_var.get() if category_var.get() != 'Все' else None
        products = get_products(search, category)
    else:
        products = get_all_products()

    row = 0
    col = 0
    for product in products:
        product_id, article, name, price, quantity, category = product

        card = tk.Frame(products_frame_inner, bg='white', relief='ridge', bd=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        tk.Label(card, text=name, font=('Arial', 14, 'bold'), bg='white').pack(pady=(10, 5))
        tk.Label(card, text=f"Артикул: {article}", font=('Arial', 10), bg='white', fg='gray').pack()
        tk.Label(card, text=f"Цена: {price} руб.", font=('Arial', 12), bg='white', fg='#22C55E').pack()
        tk.Label(card, text=f"В наличии: {quantity} шт.", font=('Arial', 10), bg='white').pack()

        if current_user_role == 'client' and quantity > 0:
            frame = tk.Frame(card, bg='white')
            frame.pack(pady=10)

            spinner = ttk.Spinbox(frame, from_=1, to=min(10, quantity), width=5)
            spinner.pack(side='left', padx=5)

            tk.Button(frame, text="В корзину", bg='#22C55E', fg='white', font=('Arial', 10),
                      command=lambda p=product_id, n=name, pr=price, s=spinner: add_to_cart(p, n, pr,
                                                                                            int(s.get()))).pack(
                side='left')

        elif current_user_role in ['manager', 'admin']:
            tk.Button(card, text="✏️ Редактировать", bg='#FCD34D', fg='#333', font=('Arial', 10),
                      command=lambda p=product_id, n=name, pr=price, q=quantity: edit_product(p, n, pr, q)).pack(pady=5)

        col += 1
        if col >= 3:
            col = 0
            row += 1

    for i in range(3):
        products_frame_inner.grid_columnconfigure(i, weight=1)


def show_main_app():
    global current_root, products_frame, products_frame_inner, cart_listbox, cart_total_label, search_entry, category_var, canvas
    global current_user_name, current_user_role, current_user_id

    # Очищаем окно
    for widget in current_root.winfo_children():
        widget.destroy()

    current_root.title(f"Зелёный Сад - {current_user_name}")
    current_root.geometry("1200x700")
    current_root.configure(bg='#F8FAF5')

    # Header
    header = tk.Frame(current_root, bg='#22C55E', height=80)
    header.pack(fill='x')
    header.pack_propagate(False)

    tk.Label(header, text="🌱 Зелёный Сад", font=('Arial', 20, 'bold'), bg='#22C55E', fg='white').pack(side='left',
                                                                                                      padx=20, pady=20)
    tk.Label(header, text=f"Добро пожаловать, {current_user_name} ({current_user_role})",
             font=('Arial', 12), bg='#22C55E', fg='white').pack(side='right', padx=20, pady=20)

    # Main frame
    main_frame = tk.Frame(current_root, bg='#F8FAF5')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Left panel - filters
    left_panel = tk.Frame(main_frame, bg='#F8FAF5', width=250)
    left_panel.pack(side='left', fill='y', padx=(0, 20))

    tk.Label(left_panel, text="Фильтры", font=('Arial', 16, 'bold'), bg='#F8FAF5').pack(anchor='w', pady=10)

    # Category filter
    tk.Label(left_panel, text="Категория:", font=('Arial', 12), bg='#F8FAF5').pack(anchor='w', pady=(10, 0))
    category_var = tk.StringVar(value='Все')
    category_combo = ttk.Combobox(left_panel, textvariable=category_var, values=['Все'] + get_categories(), width=20)
    category_combo.pack(anchor='w', pady=5)

    # Search
    tk.Label(left_panel, text="Поиск:", font=('Arial', 12), bg='#F8FAF5').pack(anchor='w', pady=(10, 0))
    search_entry = tk.Entry(left_panel, font=('Arial', 12), width=25)
    search_entry.pack(anchor='w', pady=5)

    if current_user_role in ['manager', 'admin']:
        tk.Button(left_panel, text="Применить фильтры", bg='#22C55E', fg='white',
                  command=load_products).pack(pady=20)

        # Admin panel
        if current_user_role == 'admin':
            tk.Label(left_panel, text="Администрирование", font=('Arial', 16, 'bold'), bg='#F8FAF5').pack(anchor='w',
                                                                                                          pady=(20, 10))
            tk.Button(left_panel, text="Управление товарами", bg='#FCD34D', fg='#333',
                      command=manage_products).pack(pady=5, fill='x')
            tk.Button(left_panel, text="Управление заказами", bg='#8B7355', fg='white',
                      command=manage_orders).pack(pady=5, fill='x')

    # Right panel - products
    right_panel = tk.Frame(main_frame, bg='#F8FAF5')
    right_panel.pack(side='left', fill='both', expand=True)

    # Products frame with scroll
    canvas = tk.Canvas(right_panel, bg='#F8FAF5', highlightthickness=0)
    scrollbar = ttk.Scrollbar(right_panel, orient='vertical', command=canvas.yview)
    products_frame_inner = tk.Frame(canvas, bg='#F8FAF5')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', on_canvas_configure)

    canvas.create_window((0, 0), window=products_frame_inner, anchor='nw')

    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)

    # Cart panel for clients
    if current_user_role == 'client':
        cart_frame = tk.Frame(current_root, bg='#FCD34D', width=300)
        cart_frame.pack(side='right', fill='y', padx=(0, 20), pady=20)
        cart_frame.pack_propagate(False)

        tk.Label(cart_frame, text="🛒 Корзина", font=('Arial', 16, 'bold'), bg='#FCD34D').pack(pady=10)

        cart_listbox = tk.Listbox(cart_frame, height=15, width=35)
        cart_listbox.pack(pady=10, padx=10, fill='both', expand=True)

        cart_total_label = tk.Label(cart_frame, text="Итого: 0 руб.", font=('Arial', 14, 'bold'), bg='#FCD34D')
        cart_total_label.pack(pady=10)

        tk.Button(cart_frame, text="Оформить заказ", bg='#22C55E', fg='white',
                  command=checkout).pack(pady=5, padx=20, fill='x')
        tk.Button(cart_frame, text="Очистить корзину", bg='#8B7355', fg='white',
                  command=clear_cart).pack(pady=5, padx=20, fill='x')

    load_products()


def open_register(parent_window):
    reg_window = tk.Toplevel(parent_window)
    reg_window.title("Регистрация")
    reg_window.geometry("400x500")
    reg_window.configure(bg='#F8FAF5')

    captcha_text = generate_captcha()

    tk.Label(reg_window, text="Регистрация нового пользователя", font=('Arial', 18, 'bold'), bg='#F8FAF5').pack(pady=20)

    frame = tk.Frame(reg_window, bg='#F8FAF5')
    frame.pack(pady=20)

    fields = [
        ('Логин:', 'login'),
        ('Пароль:', 'password'),
        ('ФИО:', 'full_name'),
        ('Телефон:', 'phone')
    ]

    entries = {}
    row = 0
    for label, key in fields:
        tk.Label(frame, text=label, font=('Arial', 12), bg='#F8FAF5').grid(row=row, column=0, pady=10, sticky='e')
        entry = tk.Entry(frame, font=('Arial', 12), width=25, show='*' if key == 'password' else '')
        entry.grid(row=row, column=1, pady=10, padx=10)
        entries[key] = entry
        row += 1

    # CAPTCHA
    tk.Label(frame, text="CAPTCHA:", font=('Arial', 12), bg='#F8FAF5').grid(row=row, column=0, pady=10, sticky='e')
    captcha_label = tk.Label(frame, text=captcha_text, font=('Courier', 14, 'bold'), bg='#FCD34D', fg='#333')
    captcha_label.grid(row=row, column=1, pady=10, padx=10)
    row += 1

    tk.Label(frame, text="Введите CAPTCHA:", font=('Arial', 12), bg='#F8FAF5').grid(row=row, column=0, pady=10,
                                                                                    sticky='e')
    captcha_entry = tk.Entry(frame, font=('Arial', 12), width=25)
    captcha_entry.grid(row=row, column=1, pady=10, padx=10)

    def do_register():
        if captcha_entry.get().upper() != captcha_text:
            messagebox.showerror("Ошибка", "Неверная CAPTCHA!")
            return

        success = register_user(
            entries['login'].get(),
            entries['password'].get(),
            entries['full_name'].get(),
            entries['phone'].get()
        )

        if success:
            messagebox.showinfo("Успех", "Регистрация успешна! Теперь вы можете войти.")
            reg_window.destroy()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")

    tk.Button(reg_window, text="Зарегистрироваться", bg='#22C55E', fg='white', font=('Arial', 12),
              padx=40, pady=10, command=do_register).pack(pady=20)


def login():
    global current_user_id, current_user_name, current_user_role, current_root

    login_input = login_entry.get()
    password_input = password_entry.get()

    user = get_user(login_input, password_input)
    if user:
        current_user_id = user[0]
        current_user_name = user[1]
        current_user_role = user[2]
        show_main_app()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


def guest_login():
    global current_user_id, current_user_name, current_user_role, current_root

    current_user_id = 0
    current_user_name = "Гость"
    current_user_role = "guest"
    show_main_app()


def create_login_window():
    global login_entry, password_entry, current_root

    current_root = tk.Tk()
    current_root.title("Зелёный Сад - Вход")
    current_root.geometry("500x450")
    current_root.configure(bg='#F8FAF5')

    # Logo
    title = tk.Label(current_root, text="🌱 Зелёный Сад", font=('Arial', 24, 'bold'), bg='#F8FAF5', fg='#22C55E')
    title.pack(pady=20)

    subtitle = tk.Label(current_root, text="Природа в вашем доме", font=('Arial', 12), bg='#F8FAF5', fg='#8B7355')
    subtitle.pack()

    # Login frame
    frame = tk.Frame(current_root, bg='#F8FAF5')
    frame.pack(pady=30)

    tk.Label(frame, text="Логин:", font=('Arial', 12), bg='#F8FAF5').grid(row=0, column=0, pady=10, sticky='e')
    login_entry = tk.Entry(frame, font=('Arial', 12), width=25)
    login_entry.grid(row=0, column=1, pady=10, padx=10)

    tk.Label(frame, text="Пароль:", font=('Arial', 12), bg='#F8FAF5').grid(row=1, column=0, pady=10, sticky='e')
    password_entry = tk.Entry(frame, font=('Arial', 12), width=25, show='*')
    password_entry.grid(row=1, column=1, pady=10, padx=10)

    # Buttons
    btn_frame = tk.Frame(current_root, bg='#F8FAF5')
    btn_frame.pack(pady=20)

    login_btn = tk.Button(btn_frame, text="Войти", bg='#22C55E', fg='white', font=('Arial', 12),
                          padx=30, pady=10, command=login)
    login_btn.pack(side='left', padx=10)

    register_btn = tk.Button(btn_frame, text="Регистрация", bg='#FCD34D', fg='#333', font=('Arial', 12),
                             padx=30, pady=10, command=lambda: open_register(current_root))
    register_btn.pack(side='left', padx=10)

    guest_btn = tk.Button(btn_frame, text="Войти как Гость", bg='#8B7355', fg='white', font=('Arial', 12),
                          padx=30, pady=10, command=guest_login)
    guest_btn.pack(side='left', padx=10)

    current_root.mainloop()


# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    init_db()
    create_login_window()
