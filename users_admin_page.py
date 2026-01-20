import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error


def create_users_admin_page(parent_frame):
    """Creates the 'Manage Users' page for the admin."""

    ctk.CTkLabel(parent_frame, text="Manage Users",
                 font=("Arial", 24, "bold"), text_color="black").place(x=20, y=20)

    # --- Total Users Card ---
    stats_card = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=10, width=200, height=80)
    stats_card.place(x=20, y=70)
    stats_card.pack_propagate(False)  # Stop shrinking

    ctk.CTkLabel(stats_card, text="Total Users", font=("Arial", 14), text_color="gray").pack(anchor="w", padx=20,
                                                                                             pady=(10, 0))

    count_label = ctk.CTkLabel(stats_card, text="Loading...", font=("Arial", 24, "bold"), text_color="black")
    count_label.pack(anchor="w", padx=20, pady=(0, 10))

    # --- Users Table Frame ---
    table_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="white", width=460, height=400)
    table_frame.place(x=20, y=170)

    # --- Table Headers ---
    header = ctk.CTkFrame(table_frame, fg_color="#F0F0F0", height=40)
    header.pack(fill="x", pady=5)

    ctk.CTkLabel(header, text="ID", width=40, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="First Name", width=100, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Last Name", width=100, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Email", width=200, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)

    # --- Fetch Data ---
    try:
        conn = mysql.connector.connect(
            host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
        )
        cursor = conn.cursor(dictionary=True)

        # 1. Get Count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        count_label.configure(text=str(total_users))

        # 2. Get Users List
        query = "SELECT id, first_name, last_name, email FROM users ORDER BY id"
        cursor.execute(query)
        users = cursor.fetchall()

        for user in users:
            row = ctk.CTkFrame(table_frame, fg_color="transparent", height=30)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=str(user['id']), width=40, text_color="black", anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=user['first_name'], width=100, text_color="black", anchor="w").pack(side="left",
                                                                                                       padx=5)
            ctk.CTkLabel(row, text=user['last_name'], width=100, text_color="black", anchor="w").pack(side="left",
                                                                                                      padx=5)
            ctk.CTkLabel(row, text=user['email'], width=200, text_color="black", anchor="w").pack(side="left", padx=5)

            ctk.CTkFrame(table_frame, height=1, fg_color="#E0E0E0").pack(fill="x")

    except Error as e:
        messagebox.showerror("Database Error", f"{e}")
        count_label.configure(text="Error")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close();
            conn.close()

    return parent_frame