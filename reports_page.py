from multiprocessing.pool import worker
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import pandas as pd
import mysql.connector
from mysql.connector import Error
from tkcalendar import Calendar
import datetime
import os

def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        # Placeholder
        return ImageTk.PhotoImage(Image.new('RGB', size, (200, 200, 200)))


def create_reports_page(parent_frame):
    

    ctk.CTkLabel(parent_frame, text="Generate Reports",
                 font=("Arial", 24, "bold"), text_color="black").place(x=20, y=20)

    # -------- SCROLLABLE FRAME --------
    scroll = ctk.CTkScrollableFrame(parent_frame, width=480, height=510, fg_color="transparent")
    scroll.place(x=20, y=70)

    # ---------------- FILTERS CARD ----------------
    filters_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    filters_card.pack(fill="x", pady=5)

    ctk.CTkLabel(filters_card, text="Filters", text_color="black", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

    time_var = ctk.StringVar(value="Daily")

    ctk.CTkLabel(filters_card, text="Time Frame", font=("Arial", 14, "bold"),
                 text_color="black").pack(anchor="w", padx=20)

    # ---------------- SIDE-BY-SIDE CALENDAR FRAME ----------------
    custom_range_frame = ctk.CTkFrame(filters_card, fg_color="white")
    # We don't pack it yet; only when "Custom" is selected

    calendar_icon = resize_image((20, 20), r"Images\calendar.png")  # Ensure you have this icon

    def open_calendar(target_entry):
        # Create a Toplevel window for the calendar popup
        top = ctk.CTkToplevel(parent_frame)
        top.title("Select Date")
        top.geometry("300x250")
        top.attributes("-topmost", True)  # Keep on top

        cal = Calendar(top, selectmode="day", date_pattern="y-mm-dd",
                       background="#9370DB", foreground="white", headersbackground="#E0B0FF", headersforeground="black")
        cal.pack(pady=10)

        def set_date():
            target_entry.delete(0, 'end')
            target_entry.insert(0, cal.get_date())
            top.destroy()

        ctk.CTkButton(top, text="Select", command=set_date, fg_color="green").pack(pady=10)

    # Start Date Row
    start_row = ctk.CTkFrame(custom_range_frame, fg_color="transparent")
    start_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(start_row, text="Start Date:", width=80, anchor="w", text_color="black").pack(side="left")
    start_date_entry = ctk.CTkEntry(start_row, fg_color="white", width=150, text_color="black")
    start_date_entry.pack(side="left", padx=5)
    ctk.CTkButton(start_row, text="", image=calendar_icon, width=30, height=30,
                  fg_color="transparent", hover_color="#E0B0FF",
                  command=lambda: open_calendar(start_date_entry)).pack(side="left")

    # End Date Row
    end_row = ctk.CTkFrame(custom_range_frame, fg_color="transparent")
    end_row.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(end_row, text="End Date:", width=80, anchor="w", text_color="black").pack(side="left")
    end_date_entry = ctk.CTkEntry(end_row, fg_color="white" ,width=150, text_color="black")
    end_date_entry.pack(side="left", padx=5)
    ctk.CTkButton(end_row, text="", image=calendar_icon, width=30, height=30,
                  fg_color="transparent", hover_color="#E0B0FF",
                  command=lambda: open_calendar(end_date_entry)).pack(side="left")

  # ---------------- Radio button logic ----------------
    def on_timeframe_change():

        if time_var.get() == "Custom":
            custom_range_frame.pack(fill="x", pady=10)
        else:
            custom_range_frame.pack_forget()

    # Radio buttons list
    ctk.CTkRadioButton(filters_card, text="Daily", text_color="black", variable=time_var, value="Daily",
                       command=on_timeframe_change).pack(anchor="w", padx=30)
    ctk.CTkRadioButton(filters_card, text="Weekly", text_color="black", variable=time_var, value="Weekly",
                       command=on_timeframe_change).pack(anchor="w", padx=30)
    ctk.CTkRadioButton(filters_card, text="Monthly", text_color="black", variable=time_var, value="Monthly",
                       command=on_timeframe_change).pack(anchor="w", padx=30)
    ctk.CTkRadioButton(filters_card, text="Custom Range", text_color="black", variable=time_var, value="Custom",
                       command=on_timeframe_change).pack(anchor="w", padx=30)
    
    # ---------------- DATA TO INCLUDE ----------------
    data_include_frame = ctk.CTkFrame(filters_card, fg_color="white")
    data_include_frame.pack(fill="x", pady=(10, 0))

    ctk.CTkLabel(data_include_frame, text="Data to Include", text_color="black", font=("Arial", 14, "bold")).pack(anchor="w", padx=20)

    orders_var = ctk.BooleanVar()
    sales_var = ctk.BooleanVar()
    demand_var = ctk.BooleanVar()
    stock_var = ctk.BooleanVar()

    ctk.CTkCheckBox(data_include_frame, text="Orders", text_color="black", variable=orders_var).pack(anchor="w", padx=30)
    ctk.CTkCheckBox(data_include_frame, text="Total Sales", text_color="black", variable=sales_var).pack(anchor="w", padx=30)
    ctk.CTkCheckBox(data_include_frame, text="Current Stock Levels", text_color="black", variable=stock_var).pack(anchor="w", padx=30)

    # ------------------ GENERATE ------------------
    def generate_excel_report():
        # 1. Check selection
        if not any([orders_var.get(), sales_var.get(), demand_var.get(), stock_var.get()]):
            messagebox.showwarning("Warning", "Please select at least one data type to include.")
            return

        # 2. Determine Date Range
        start_date = None
        end_date = None
        today = datetime.date.today()

        if time_var.get() == "Daily":
            start_date = today
            end_date = today
        elif time_var.get() == "Weekly":
            start_date = today - datetime.timedelta(days=7)
            end_date = today
        elif time_var.get() == "Monthly":
            start_date = today - datetime.timedelta(days=30)
            end_date = today
        elif time_var.get() == "Custom":
            try:
                # Retrieve date directly from calendar widget
                # tkcalendar returns strings in 'y-mm-dd' format (e.g. '2025-11-25')
                s_val = start_cal.get_date()
                e_val = end_cal.get_date()

                start_date = datetime.datetime.strptime(s_val, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(e_val, "%Y-%m-%d").date()

                if start_date > end_date:
                    messagebox.showerror("Error", "Start Date cannot be after End Date.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid Date Format from calendar.")
                return

        base_name_parts = []
        if orders_var.get(): base_name_parts.append("Orders")
        if sales_var.get(): base_name_parts.append("Sales")
        if stock_var.get(): base_name_parts.append("Stock")

        # Join parts (e.g., "Orders_Sales") or default to "Report" if too long
        if len(base_name_parts) > 2:
            base_name = "Full_Report"
        else:
            base_name = "_".join(base_name_parts) + "_Report"

        # Current Date string
        date_str = today.strftime("%Y-%m-%d")

        # Get default downloads folder (Works on Windows/Mac)
        if os.name == 'nt':
            download_folder = os.path.expanduser('~') + "\\Downloads\\"
        else:
            download_folder = os.path.expanduser('~') + "/Downloads/"

        # Versioning Logic (001, 002, etc.)
        counter = 1
        while True:
            # Format: Name_Date_001.xlsx
            filename = f"{base_name}_{date_str}_{str(counter).zfill(3)}.xlsx"
            file_path = os.path.join(download_folder, filename)

            if not os.path.exists(file_path):
                break  # Found a free filename!
            counter += 1


        # 4. Fetch Data and Write
        try:
            conn = mysql.connector.connect(
                host="141.209.241.57", user="kondu2r",
                password="mypass", database="BIS698Fall25_GRP4"
            )

            # Try to use xlsxwriter for charts, fallback to openpyxl
            writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
            workbook = writer.book
            data_written = False

            # --- ORDERS ---
            if orders_var.get():
                query = f"SELECT * FROM Orders WHERE order_date BETWEEN '{start_date}' AND '{end_date}'"
                df_orders = pd.read_sql(query, conn)
                if not df_orders.empty:
                    df_orders.to_excel(writer, sheet_name='Orders', index=False)
                    data_written = True

                # --- SALES ---
            if sales_var.get():
                query = f"""
                        SELECT order_date, SUM(total_amount) as daily_sales 
                        FROM Orders 
                        WHERE order_date BETWEEN '{start_date}' AND '{end_date}' 
                        GROUP BY order_date
                        """

                df_sales = pd.read_sql(query, conn)
                if not df_sales.empty:
                    sheet_name = 'Sales'
                    df_sales.to_excel(writer, sheet_name=sheet_name, index=False)
                    data_written = True

                    worksheet = writer.sheets[sheet_name]

                    chart = workbook.add_chart({'type': 'line'})

                    # Configure series
                    # Assuming date is in col A (0), sales in col B (1)
                    max_row = len(df_sales) + 1
                    chart.add_series({
                        'name': 'Daily Sales',
                        'categories': [sheet_name, 1, 0, max_row, 0],  # Column A (Dates)
                        'values': [sheet_name, 1, 1, max_row, 1],  # Column B (Sales)
                        'line': {'color': 'blue', 'width': 2.25},
                        'marker': {'type': 'circle', 'size': 7}
                    })

                    chart.set_title({'name': 'Sales Trend'})
                    chart.set_x_axis({'name': 'Date', 'date_axis': True})
                    chart.set_y_axis({'name': 'Total Amount ($)'})

                    # Insert chart into sheet
                    worksheet.insert_chart('D2', chart)

            # --- STOCK ---
            if stock_var.get():
                query = "SELECT name, stock_quantity FROM products"
                df_stock = pd.read_sql(query, conn)
                if not df_stock.empty:
                    sheet_name = 'Stock'
                    df_stock.to_excel(writer, sheet_name=sheet_name, index=False)
                    data_written = True

                    worksheet = writer.sheets[sheet_name]
                    chart = workbook.add_chart({'type': 'column'})

                    max_row = len(df_stock) + 1
                    chart.add_series({
                        'name': 'Stock Level',
                        'categories': [sheet_name, 1, 0, max_row, 0],  # Col A: Name
                        'values': [sheet_name, 1, 1, max_row, 1],  # Col B: Qty
                        'fill': {'color': '#8CD790'}
                    })

                    chart.set_title({'name': 'Current Inventory'})
                    chart.set_x_axis({'name': 'Product'})
                    chart.set_y_axis({'name': 'Quantity'})

                    worksheet.insert_chart('D2', chart)

            writer.close()

            if data_written:
                messagebox.showinfo("Success", f"Report saved to:\n{file_path}")
            else:
                messagebox.showinfo("Info", "No data found for selected period.")

        except Error as e:
            messagebox.showerror("Database Error", f"{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    ctk.CTkButton(filters_card, text="Generate Report",
                  fg_color="green", hover_color="darkgreen",
                  command=generate_excel_report).pack(fill="x", padx=20, pady=20)


    # ---------------- OUTPUT CARD ----------------
    output_card = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    output_card.pack(fill="both", expand=True, pady=5)

    ctk.CTkLabel(output_card, text="Report Output", font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", padx=20, pady=10)
    ctk.CTkLabel(output_card, text="Select filters above to generate an Excel file.",
                 text_color="gray").pack(pady=50)
    return parent_frame
