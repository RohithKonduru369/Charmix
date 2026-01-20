import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from CTkCalendar import CTkCalendar
import mysql.connector
from mysql.connector import Error
from products_page import create_products_page
from reports_page import create_reports_page
from orders_admin_page import create_orders_admin_page
from users_admin_page import create_users_admin_page

def create_admin_dashboard_ui(master):
    # --- Main Container Frame ---
    dashboard_frame = ctk.CTkFrame(master, fg_color="#F0F2F5", width=700, height=600)
    dashboard_frame.pack_propagate(False)
    dashboard_frame.place(x=0, y=0)

    # --- 1. Sidebar Frame (Dark) ---
    sidebar_frame = ctk.CTkFrame(dashboard_frame, fg_color="#2A3042", width=180, height=600,
                                 corner_radius=0)
    sidebar_frame.pack(side="left", fill="y")
    sidebar_frame.pack_propagate(False)

    # --- 2. Main Content Frame (Light) ---
    # This frame will now be the parent for all sub-pages
    main_content_frame = ctk.CTkFrame(dashboard_frame, fg_color="#F0F2F5", width=520, height=600)
    main_content_frame.pack(side="right", fill="both", expand=True)
    main_content_frame.pack_propagate(False)

    # --- Navigation & Page Functions ---
    def clear_main_content():
        """Helper function to clear the main content area."""
        for widget in main_content_frame.winfo_children():
            widget.destroy()

    def show_products_page():
        clear_main_content()
        create_products_page(main_content_frame)

    def show_reports_page():
        clear_main_content()
        create_reports_page(main_content_frame)

    def show_users_page():
        clear_main_content()
        create_users_admin_page(main_content_frame)

    def show_orders_page():
        clear_main_content()
        create_orders_admin_page(main_content_frame)


    def show_dashboard_page():
        """Shows the main dashboard with stats."""
        clear_main_content()  # Clear the frame first

        ctk.CTkLabel(main_content_frame, text="Welcome, Admin!",
                     font=("Arial", 24, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(20, 10))

        # --- Stats Cards Frame ---
        stats_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=10)

        # --- Database Logic for Stats ---
        total_sales = 0.0
        new_users = 0
        recent_orders = 0
        products_in_stock = 0

        try:
            conn = mysql.connector.connect(
                host="141.209.241.57", user="kondu2r",
                password="mypass", database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor()


            cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM Orders")
            total_sales = float(cursor.fetchone()[0])

            # Fetch New Users
            cursor.execute("SELECT COUNT(id) FROM users")
            new_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM Orders WHERE order_date >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
            recent_orders = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(stock_quantity),0) FROM products")
            products_in_stock = int(cursor.fetchone()[0])

        except Error as e:
            print(f"Error connecting to DB: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

        # --- Create Stat Cards ---
        card1 = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10,
                             cursor="hand2")
        card1.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
        card1.bind("<Button-1>", lambda e: show_reports_page())

        lbl1_1 = ctk.CTkLabel(card1, text="Total Sales", font=("Arial", 12), text_color="black", fg_color="white")
        lbl1_1.pack(pady=(0, 0))
        lbl1_1.bind("<Button-1>", lambda e: show_reports_page())

        lbl1_2 = ctk.CTkLabel(card1, text=f"${total_sales:,.2f}", font=("Arial", 20, "bold"), text_color="black",
                              fg_color="white")
        lbl1_2.pack(pady=(0, 0))
        lbl1_2.bind("<Button-1>", lambda e: show_reports_page())

        card2 = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
        card2.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
        ctk.CTkLabel(card2, text="Total Users", font=("Arial", 12), text_color="black").pack(pady=(0, 0))
        ctk.CTkLabel(card2, text=f"{new_users}", font=("Arial", 20, "bold"), text_color="black").pack(pady=(0, 0))

        # --- Second Row of Stats Cards ---
        stats_frame_2 = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        stats_frame_2.pack(fill="x", padx=15, pady=(0, 10))

        card3 = ctk.CTkFrame(stats_frame_2, fg_color="white", corner_radius=10)
        card3.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
        ctk.CTkLabel(card3, text="Recent Orders", font=("Arial", 12), text_color="black").pack(pady=(0, 0))
        ctk.CTkLabel(card3, text=f"{recent_orders}", font=("Arial", 20, "bold"), text_color="black").pack(pady=(0, 0))

        card4 = ctk.CTkFrame(stats_frame_2, fg_color="white", corner_radius=10,
                             cursor="hand2")
        card4.pack(side="left", fill="x", expand=True, padx=8, ipady=5)
        card4.bind("<Button-1>", lambda e: show_products_page())

        lbl4_1 = ctk.CTkLabel(card4, text="Products in Stock", font=("Arial", 12), text_color="black", fg_color="white")
        lbl4_1.pack(pady=(0, 0))
        lbl4_1.bind("<Button-1>", lambda e: show_products_page())

        lbl4_2 = ctk.CTkLabel(card4, text=f"{products_in_stock}", font=("Arial", 20, "bold"), text_color="black",
                              fg_color="white",anchor = "w")
        lbl4_2.pack(pady=(0, 0))
        lbl4_2.bind("<Button-1>", lambda e: show_products_page())

    def logout():
        from login_screen import create_login_ui
        dashboard_frame.place_forget()
        create_login_ui(master)

    # --- Sidebar Content ---
    ctk.CTkLabel(sidebar_frame, text="Admin Dashboard",
                 font=("Arial", 18, "bold"), text_color="white").pack(padx=20, pady=30)

    ctk.CTkButton(sidebar_frame, text="Dashboard", fg_color="#4A5264", text_color="white",
                  anchor="w", font=("Arial", 14, "bold"), height=40,
                  command=show_dashboard_page).pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(sidebar_frame, text="Products", fg_color="transparent", text_color="white",
                  anchor="w", font=("Arial", 14), height=40, hover_color="#4A5264",
                  command=show_products_page).pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(sidebar_frame, text="Users", fg_color="transparent", text_color="white",
                  anchor="w", font=("Arial", 14), height=40, hover_color="#4A5264",
                  command=show_users_page).pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(sidebar_frame, text="Orders", fg_color="transparent", text_color="white",
                  anchor="w", font=("Arial", 14), height=40, hover_color="#4A5264",
                  command=show_orders_page).pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(sidebar_frame, text="Reports", fg_color="transparent", text_color="white",
                  anchor="w", font=("Arial", 14), height=40, hover_color="#4A5264",
                  command=show_reports_page).pack(fill="x", padx=10, pady=5)

    # Logout Button at the bottom
    ctk.CTkButton(sidebar_frame, text="Log Out", fg_color="transparent", text_color="#FF6B6B",
                  anchor="w", font=("Arial", 14), height=40, hover_color="#4A5264",
                  command=logout).pack(side="bottom", fill="x", padx=10, pady=20)

    # --- Initial Page Load ---
    show_dashboard_page()  # Show the dashboard by default

    return dashboard_frame


# --- This block lets you run this file directly for testing ---
if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Admin Dashboard (Test Mode)")
    root.geometry("700x600")
    root.resizable(False, False)

    create_admin_dashboard_ui(root)

    root.mainloop()