import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import random

# ========== ДАННЫЕ (вместо БД) ==========
films = [
    {
        "id": 1,
        "name": "Один дома",
        "country": "США",
        "year": 1990,
        "actors": "Маколей Калкин, Джо Пеши",
        "rating": 8.5,
        "poster": "🎬",
        "description": "Классическая рождественская комедия"
    },
    {
        "id": 2,
        "name": "Брат",
        "country": "Россия",
        "year": 1997,
        "actors": "Сергей Бодров, Виктор Сухоруков",
        "rating": 8.7,
        "poster": "🎬",
        "description": "Культовый российский фильм"
    },
    {
        "id": 3,
        "name": "Аватар",
        "country": "США",
        "year": 2009,
        "actors": "Сэм Уортингтон, Зои Салдана",
        "rating": 8.0,
        "poster": "🎬",
        "description": "Фантастический блокбастер"
    }
]

# Сеансы
sessions = [
    {"id": 1, "film_id": 1, "date": "2026-05-15", "time": "10:00", "hall": "Зал 1", "price": 300, "taken_seats": []},
    {"id": 2, "film_id": 1, "date": "2026-05-15", "time": "14:00", "hall": "Зал 1", "price": 400, "taken_seats": []},
    {"id": 3, "film_id": 2, "date": "2026-05-15", "time": "12:00", "hall": "Зал 2", "price": 350, "taken_seats": []},
    {"id": 4, "film_id": 2, "date": "2026-05-16", "time": "16:00", "hall": "Зал 2", "price": 400, "taken_seats": []},
    {"id": 5, "film_id": 3, "date": "2026-05-15", "time": "18:00", "hall": "Зал 3", "price": 500, "taken_seats": []},
    {"id": 6, "film_id": 3, "date": "2026-05-17", "time": "20:00", "hall": "Зал 3", "price": 550, "taken_seats": []}
]

# Конфигурация зала (ряды и места)
HALL_CONFIG = {
    "rows": 5,
    "seats_per_row": 8,
    "max_seats": 40
}

current_ticket = None


# ========== ГЛАВНОЕ ОКНО ==========
class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кинотеатр")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        self.show_main()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ========== МОДУЛЬ 4: ГЛАВНОЕ ОКНО ==========
    def show_main(self):
        self.clear()

        # Заголовок
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="🎬 КИНОТЕАТР", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=15)

        # Контейнер для фильмов (сетка 2 колонки)
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Показываем фильмы в 2 колонки
        for i, film in enumerate(films):
            row = i // 2
            col = i % 2

            frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
            frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            # Постер
            poster_frame = tk.Frame(frame, bg="#34495e", width=200, height=250)
            poster_frame.pack(side=tk.LEFT, padx=10, pady=10)
            poster_frame.pack_propagate(False)
            tk.Label(poster_frame, text=film["poster"], font=("Arial", 100), bg="#34495e", fg="white").pack(expand=True)

            # Информация о фильме
            info_frame = tk.Frame(frame, bg="white")
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)

            tk.Label(info_frame, text=film["name"], font=("Arial", 18, "bold"), bg="white", fg="#2c3e50").pack(
                anchor="w")
            tk.Label(info_frame, text=f"Страна: {film['country']} | Год: {film['year']}", font=("Arial", 10),
                     bg="white").pack(anchor="w", pady=5)
            tk.Label(info_frame, text=f"Актёры: {film['actors']}", font=("Arial", 10), bg="white", wraplength=300).pack(
                anchor="w", pady=2)
            tk.Label(info_frame, text=f"{film['description']}", font=("Arial", 10, "italic"), bg="white",
                     fg="gray").pack(anchor="w", pady=5)

            # Оценка
            rating_frame = tk.Frame(info_frame, bg="white")
            rating_frame.pack(anchor="w", pady=5)
            tk.Label(rating_frame, text="⭐" * int(film["rating"]) + "☆" * (5 - int(film["rating"])),
                     font=("Arial", 14), bg="white").pack(side=tk.LEFT)
            tk.Label(rating_frame, text=f" {film['rating']}/10", font=("Arial", 10), bg="white", fg="gold").pack(
                side=tk.LEFT)

            # Кнопка Купить билет
            tk.Button(info_frame, text="🎫 Купить билет", bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                      command=lambda f=film: self.show_sessions(f)).pack(anchor="w", pady=15)

        # Настройка сетки
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

    # ========== МОДУЛЬ 5: ВЫБОР СЕАНСА ==========
    def show_sessions(self, film):
        self.clear()

        tk.Label(self.root, text=f"🎬 Выберите сеанс: {film['name']}", font=("Arial", 18, "bold"),
                 bg="#f0f0f0", fg="#2c3e50").pack(pady=20)

        # Контейнер для сеансов
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)

        # Фильтруем сеансы для этого фильма
        film_sessions = [s for s in sessions if s["film_id"] == film["id"]]

        if not film_sessions:
            tk.Label(container, text="Нет доступных сеансов", font=("Arial", 14), fg="red").pack()
        else:
            for session in film_sessions:
                # Карточка сеанса
                frame = tk.Frame(container, bg="white", relief=tk.RAISED, bd=2)
                frame.pack(fill=tk.X, padx=20, pady=10)

                info_text = f"📅 {session['date']} | ⏰ {session['time']} | 🎭 {session['hall']} | 💰 {session['price']} руб"
                tk.Label(frame, text=info_text, font=("Arial", 12), bg="white", padx=20, pady=15).pack(side=tk.LEFT)

                seats_left = HALL_CONFIG["max_seats"] - len(session["taken_seats"])
                tk.Label(frame, text=f"Свободно мест: {seats_left}", font=("Arial", 10), bg="white", fg="green").pack(
                    side=tk.LEFT, padx=20)

                tk.Button(frame, text="Выбрать место", bg="#3498db", fg="white", font=("Arial", 10),
                          command=lambda s=session: self.choose_seats(s, film)).pack(side=tk.RIGHT, padx=20)

        tk.Button(self.root, text="← Назад", command=self.show_main, bg="#95a5a6", fg="white",
                  font=("Arial", 10)).pack(pady=20)

    # ========== ВЫБОР МЕСТА ==========
    def choose_seats(self, session, film):
        self.clear()

        tk.Label(self.root, text=f"🎬 {film['name']}", font=("Arial", 16, "bold"),
                 bg="#f0f0f0").pack(pady=10)
        tk.Label(self.root,
                 text=f"{session['date']} | {session['time']} | {session['hall']} | {session['price']} руб/место",
                 font=("Arial", 12), bg="#f0f0f0").pack(pady=5)

        # Сумма
        self.total_price = tk.Label(self.root, text="Сумма: 0 руб", font=("Arial", 14, "bold"),
                                    bg="#f0f0f0", fg="#e74c3c")
        self.total_price.pack(pady=10)

        # Экран
        screen_frame = tk.Frame(self.root, bg="#2c3e50", height=40)
        screen_frame.pack(fill=tk.X, padx=100, pady=10)
        tk.Label(screen_frame, text="ЭКРАН", font=("Arial", 12, "bold"), bg="#2c3e50", fg="white").pack(pady=8)

        # Зал с местами
        seats_frame = tk.Frame(self.root, bg="#f0f0f0")
        seats_frame.pack(pady=20)

        # Хранилище выбранных мест
        selected_seats = []
        seat_buttons = {}

        def update_total():
            self.total_price.config(text=f"Сумма: {len(selected_seats) * session['price']} руб")

        def toggle_seat(row, col, seat_num):
            seat_id = f"{row + 1}:{col + 1}"

            if seat_id in session["taken_seats"]:
                messagebox.showerror("Ошибка", "Это место уже занято")
                return

            if seat_num in selected_seats:
                selected_seats.remove(seat_num)
                seat_buttons[seat_num].config(bg="#ecf0f1", text=f"{row + 1}{chr(65 + col)}")
            else:
                if len(selected_seats) >= HALL_CONFIG["max_seats"] - len(session["taken_seats"]):
                    messagebox.showerror("Ошибка", "Нет свободных мест")
                    return
                selected_seats.append(seat_num)
                seat_buttons[seat_num].config(bg="#27ae60", text=f"{row + 1}{chr(65 + col)}")

            update_total()

        # Создаём сетку мест
        for row in range(HALL_CONFIG["rows"]):
            row_frame = tk.Frame(seats_frame, bg="#f0f0f0")
            row_frame.pack(pady=5)

            tk.Label(row_frame, text=f"{row + 1}", font=("Arial", 10, "bold"), width=3, bg="#f0f0f0").pack(side=tk.LEFT)

            for col in range(HALL_CONFIG["seats_per_row"]):
                seat_num = f"{row + 1}:{col + 1}"
                is_taken = seat_num in session["taken_seats"]

                btn = tk.Button(row_frame, text=f"{row + 1}{chr(65 + col)}", width=5, height=2,
                                bg="#95a5a6" if is_taken else "#ecf0f1",
                                state=tk.DISABLED if is_taken else tk.NORMAL,
                                command=lambda r=row, c=col, s=seat_num: toggle_seat(r, c, s))
                btn.pack(side=tk.LEFT, padx=2)
                seat_buttons[seat_num] = btn

        # Информация
        info_frame = tk.Frame(self.root, bg="#f0f0f0")
        info_frame.pack(pady=15)

        tk.Label(info_frame, text="⬜ Свободно  🟢 Выбрано  ⬛ Занято", font=("Arial", 10), bg="#f0f0f0").pack()

        # Кнопка оплаты
        def pay():
            if not selected_seats:
                messagebox.showerror("Ошибка", "Выберите места")
                return

            # Сохраняем билет
            global current_ticket
            current_ticket = {
                "film": film["name"],
                "date": session["date"],
                "time": session["time"],
                "hall": session["hall"],
                "seats": selected_seats,
                "price": len(selected_seats) * session["price"],
                "ticket_id": random.randint(10000, 99999)
            }

            # Бронируем места
            for seat in selected_seats:
                if seat not in session["taken_seats"]:
                    session["taken_seats"].append(seat)

            self.show_ticket()

        tk.Button(self.root, text="💳 Оплатить", bg="#27ae60", fg="white", font=("Arial", 14, "bold"),
                  command=pay).pack(pady=20)

        tk.Button(self.root, text="← Назад", command=lambda: self.show_sessions(film),
                  bg="#95a5a6", fg="white").pack()

    # ========== ЧЕК / БИЛЕТ ==========
    def show_ticket(self):
        self.clear()

        # Основной контейнер
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True)

        # Блок билета
        ticket_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=3)
        ticket_frame.pack(padx=40, pady=30)

        # Шапка билета
        tk.Label(ticket_frame, text="🎬 КИНОБИЛЕТ 🎬", font=("Arial", 22, "bold"),
                 bg="white", fg="#2c3e50").pack(pady=15)

        tk.Label(ticket_frame, text="=" * 40, bg="white").pack()

        # Информация о сеансе
        info = [
            ("Фильм:", current_ticket["film"]),
            ("Дата:", current_ticket["date"]),
            ("Время:", current_ticket["time"]),
            ("Зал:", current_ticket["hall"]),
            ("Места:", ", ".join(current_ticket["seats"])),
            ("Сумма:", f"{current_ticket['price']} руб"),
            ("Билет №:", current_ticket["ticket_id"])
        ]

        for label, value in info:
            row = tk.Frame(ticket_frame, bg="white")
            row.pack(fill=tk.X, padx=30, pady=5)
            tk.Label(row, text=label, font=("Arial", 12, "bold"), bg="white", width=10, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 12), bg="white", anchor="w").pack(side=tk.LEFT, padx=10)

        tk.Label(ticket_frame, text="=" * 40, bg="white").pack(pady=10)

        tk.Label(ticket_frame, text="Спасибо за покупку! Хорошего просмотра! 🍿",
                 font=("Arial", 10, "italic"), bg="white", fg="green").pack(pady=10)

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="🏠 На главную", command=self.show_main,
                  bg="#3498db", fg="white", font=("Arial", 12), padx=20).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="🎫 Новый билет", command=self.show_main,
                  bg="#27ae60", fg="white", font=("Arial", 12), padx=20).pack(side=tk.LEFT, padx=10)


# ========== МОДУЛЬ 3: ЗАПРОС (демонстрация) ==========
def show_query_result():
    """Запрос: все сеансы с российскими фильмами на 15.05.2026"""
    print("\n" + "=" * 50)
    print("МОДУЛЬ 3: Сеансы с российскими фильмами на 15.05.2026")
    print("=" * 50)

    russian_films = [f["id"] for f in films if f["country"] == "Россия"]
    result = [s for s in sessions if s["film_id"] in russian_films and s["date"] == "2026-05-15"]

    if result:
        for s in result:
            film = next(f for f in films if f["id"] == s["film_id"])
            print(f"Фильм: {film['name']} | Дата: {s['date']} | Время: {s['time']} | Зал: {s['hall']}")
    else:
        print("Нет сеансов российских фильмов на 15.05.2026")


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    # Вывод результата запроса в консоль (Модуль 3)
    show_query_result()

    # Запуск приложения
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()
