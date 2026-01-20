import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error


def create_orders_admin_page(parent_frame):
    """Creates the 'Manage Orders' page for the admin."""

    ctk.CTkLabel(parent_frame, text="Manage Orders",
                 font=("Arial", 24, "bold"), text_color="black").place(x=20, y=20)

    # --- 1. Vertical Scroll Frame (Main Container) ---
    vertical_scroll_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="white", width=480, height=500)
    vertical_scroll_frame.place(x=20, y=70)

    # --- 2. Horizontal Scroll Frame (Inner Container) ---
    table_frame = ctk.CTkScrollableFrame(vertical_scroll_frame, fg_color="transparent",
                                         orientation="horizontal", height=500)
    table_frame.pack(fill="both", expand=True)

    # --- Table Headers ---
    header = ctk.CTkFrame(table_frame, fg_color="#F0F0F0", height=40)
    header.pack(fill="x", pady=5, anchor="nw")

    # EDITED: Reduced widths to decrease spacing
    ctk.CTkLabel(header, text="Order ID", width=120, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Email", width=180, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Date", width=90, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Status", width=90, font=("Arial", 12, "bold"), text_color="black", anchor="w").pack(
        side="left", padx=5)
    ctk.CTkLabel(header, text="Total", width=70, font=("Arial", 12, "bold"), text_color="black", anchor="e").pack(
        side="left", padx=5)

    # --- Fetch Data ---
    try:
        conn = mysql.connector.connect(
            host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
        )
        cursor = conn.cursor(dictionary=True)

        query = "SELECT order_id, customer_email, order_date, order_status, total_amount FROM Orders ORDER BY order_date DESC"
        cursor.execute(query)
        orders = cursor.fetchall()

        if not orders:
            ctk.CTkLabel(table_frame, text="No orders found.", text_color="gray").pack(pady=20, anchor="w")

        for order in orders:
            row = ctk.CTkFrame(table_frame, fg_color="transparent", height=30)
            row.pack(fill="x", pady=2, anchor="nw")

            status_color = "green" if order['order_status'] == 'Delivered' else "#D97706"

            # EDITED: Matched widths to headers
            ctk.CTkLabel(row, text=order['order_id'], width=120, text_color="black", anchor="w").pack(side="left",
                                                                                                      padx=5)
            ctk.CTkLabel(row, text=order['customer_email'], width=180, text_color="black", anchor="w").pack(side="left",
                                                                                                            padx=5)
            ctk.CTkLabel(row, text=str(order['order_date']), width=90, text_color="black", anchor="w").pack(side="left",
                                                                                                            padx=5)
            ctk.CTkLabel(row, text=order['order_status'], width=90, text_color=status_color, font=("Arial", 12, "bold"),
                         anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${order['total_amount']:.2f}", width=70, text_color="black", anchor="e").pack(
                side="left", padx=5)

            ctk.CTkFrame(table_frame, height=1, fg_color="#E0E0E0", width=600).pack(fill="x", anchor="nw")

    except Error as e:
        ctk.CTkLabel(table_frame, text=f"Error fetching orders: {e}", text_color="red").pack(pady=20, anchor="w")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close();
            conn.close()

    return parent_frame