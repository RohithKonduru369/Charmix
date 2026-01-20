import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# --- Reuse Shop UI Logic to display results ---
from shop_screen import create_shop_ui


def perform_global_search(master, search_query, current_frame=None):
    """
    1. Searches 'products' and 'products1' tables for the query.
    2. Merges results.
    3. Navigates to the Shop Screen to display them.
    """
    if not search_query.strip():
        messagebox.showinfo("Search", "Please enter a search term.")
        return

    print(f"Searching for: {search_query}")

    found_products = {}

    try:
        conn = mysql.connector.connect(
            host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
        )
        cursor = conn.cursor(dictionary=True)

        # --- 1. Search Main Products Table ---
        # We use LOWER() for case-insensitive search and %LIKE% for partial matches
        sql_main = """
                   SELECT id, name, brand, price, image_path, category
                   FROM products
                   WHERE LOWER(name) LIKE %s \
                      OR LOWER(brand) LIKE %s \
                      OR LOWER(category) LIKE %s \
                   """
        wildcard_query = f"%{search_query.lower()}%"
        cursor.execute(sql_main, (wildcard_query, wildcard_query, wildcard_query))

        for row in cursor.fetchall():
            prod_id = f"prod_{row['id']}"
            found_products[prod_id] = row

        # --- 2. Search Routine Products Table (products1) ---
        sql_routine = """
                      SELECT id, product_name, brand, price, image_path, description
                      FROM products1
                      WHERE LOWER(product_name) LIKE %s \
                         OR LOWER(brand) LIKE %s \
                      """
        cursor.execute(sql_routine, (wildcard_query, wildcard_query))

        for row in cursor.fetchall():
            # Normalize keys for the UI
            row['name'] = row['product_name']
            # Use distinct prefix
            prod_id = f"routine_{row['id']}"
            found_products[prod_id] = row

    except Error as e:
        messagebox.showerror("Database Error", f"Search failed: {e}")
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    # --- 3. Navigate to Results ---
    if current_frame:
        current_frame.place_forget()

    if not found_products:
        messagebox.showinfo("Search Results", f"No products found for '{search_query}'.")
        # Optional: Stay on current page or go to empty shop
        create_shop_ui(master, custom_product_list={}, title_text=f"Results for '{search_query}'")
    else:
        # Re-use the Shop UI to display the list!
        create_shop_ui(master, custom_product_list=found_products, title_text=f"Results for '{search_query}'")