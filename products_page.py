import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error


def create_products_page(parent_frame):
    """Creates the 'Manage Products' page with a full vertical scrollbar."""

    # --- 1. MAIN SCROLLABLE CONTAINER ---
    # This frame wraps everything so the whole page scrolls
    main_scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
    main_scroll.pack(fill="both", expand=True)

    # --- Header ---
    ctk.CTkLabel(main_scroll, text="Manage Products",
                 font=("Arial", 24, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(20, 10))

    # --- 2. ADD PRODUCT FRAME ---
    add_product_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, width=400)
    add_product_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(add_product_frame, text="Add New Product",
                 font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(15, 5))

    # --- Form Container ---
    details_frame = ctk.CTkFrame(add_product_frame, fg_color="transparent")
    details_frame.pack(fill="x", padx=20, pady=5)

    # 1. Product Name
    ctk.CTkLabel(details_frame, text="Product Name:", anchor="w", text_color="black").pack(fill="x")
    name_entry = ctk.CTkEntry(details_frame, placeholder_text="Enter Product Name")
    name_entry.pack(fill="x", pady=(0, 5))

    # 2. Brand
    ctk.CTkLabel(details_frame, text="Brand:", anchor="w", text_color="black").pack(fill="x")
    brand_entry = ctk.CTkEntry(details_frame, placeholder_text="Enter Brand")
    brand_entry.pack(fill="x", pady=(0, 5))

    # 3. Product Description
    ctk.CTkLabel(details_frame, text="Product Description:", anchor="w", text_color="black").pack(fill="x")
    desc_entry = ctk.CTkEntry(details_frame, placeholder_text="Enter short description")
    desc_entry.pack(fill="x", pady=(0, 5))

    # 4. Price & Quantity Container
    price_qty_container = ctk.CTkFrame(add_product_frame, fg_color="transparent")
    price_qty_container.pack(fill="x", padx=20, pady=(0, 10))

    # Price (Left)
    price_frame = ctk.CTkFrame(price_qty_container, fg_color="transparent")
    price_frame.pack(side="left", padx=(0, 5), expand=True, fill="x")
    ctk.CTkLabel(price_frame, text="Price:", anchor="w", text_color="black").pack(fill="x")
    price_entry = ctk.CTkEntry(price_frame, placeholder_text="e.g. 12.99")
    price_entry.pack(fill="x")

    # Quantity (Right)
    quantity_frame = ctk.CTkFrame(price_qty_container, fg_color="transparent")
    quantity_frame.pack(side="left", padx=(5, 0), expand=True, fill="x")
    ctk.CTkLabel(quantity_frame, text="Stock Quantity:", anchor="w", text_color="black").pack(fill="x")
    quantity_entry = ctk.CTkEntry(quantity_frame, placeholder_text="e.g. 50")
    quantity_entry.pack(fill="x")

    # 5. Image Selection
    image_path = ctk.StringVar(value="No image selected")

    def select_image():
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            image_path.set(path)
            filename = path.split('/')[-1]
            image_label.configure(text=filename)

    # Button Container for Image & Add
    btn_container = ctk.CTkFrame(add_product_frame, fg_color="transparent")
    btn_container.pack(fill="x", padx=20, pady=(10, 20))

    image_button = ctk.CTkButton(btn_container, text="Select Image", command=select_image)
    image_button.pack(side="left")

    image_label = ctk.CTkLabel(btn_container, text="No image selected", text_color="gray")
    image_label.pack(side="left", padx=10)

    # --- ADD LOGIC ---
    def on_add_product():
        name = name_entry.get()
        brand = brand_entry.get()
        desc = desc_entry.get()
        price = price_entry.get()
        quantity = quantity_entry.get()
        img_path = image_path.get()

        if not all([name, brand, price, quantity]) or img_path == "No image selected":
            messagebox.showerror("Error", "Please fill all fields and select an image.")
            return

        try:
            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor()

            query = """
                    INSERT INTO products (name, brand, price, stock_quantity, image_path, product_desc)
                    VALUES (%s, %s, %s, %s, %s, %s) \
                    """
            cursor.execute(query, (name, brand, float(price), int(quantity), img_path, desc))
            conn.commit()

            messagebox.showinfo("Success", "Product added successfully!")

            # Clear fields
            name_entry.delete(0, 'end')
            brand_entry.delete(0, 'end')
            desc_entry.delete(0, 'end')
            price_entry.delete(0, 'end')
            quantity_entry.delete(0, 'end')
            image_path.set("No image selected")
            image_label.configure(text="No image selected")

            # Refresh the table below
            load_stock_table()

        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    add_button = ctk.CTkButton(btn_container, text="Add Product", fg_color="green", hover_color="darkgreen",
                               command=on_add_product)
    add_button.pack(side="right")

    # --- 3. CURRENT STOCK FRAME ---
    stock_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=10, height=300)
    stock_frame.pack(fill="x", padx=20, pady=20)
    stock_frame.pack_propagate(False)

    ctk.CTkLabel(stock_frame, text="Current Stock",
                 font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", padx=20, pady=10)

    # Stock List Scrollable Area
    stock_list_frame = ctk.CTkScrollableFrame(stock_frame, fg_color="#F5F5F5")
    stock_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # --- Headers ---
    header = ctk.CTkFrame(stock_list_frame, fg_color="transparent")
    header.pack(fill="x")
    ctk.CTkLabel(header, text="Product Name", font=("Arial", 12, "bold"), text_color="black", width=200,
                 anchor="w").pack(side="left", padx=10)
    ctk.CTkLabel(header, text="Brand", font=("Arial", 12, "bold"), text_color="black", width=100, anchor="w").pack(
        side="left", padx=10)
    ctk.CTkLabel(header, text="Stock", font=("Arial", 12, "bold"), text_color="black", width=50, anchor="w").pack(
        side="left", padx=10)

    def load_stock_table():
        # Clear existing
        for widget in stock_list_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != header:
                widget.destroy()

        try:
            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT name, brand, stock_quantity FROM products ORDER BY name")
            all_products = cursor.fetchall()

            for product in all_products:
                row = ctk.CTkFrame(stock_list_frame, fg_color="white", height=30)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=product['name'], font=("Arial", 12), text_color="black", width=200,
                             anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(row, text=product['brand'], font=("Arial", 12), text_color="black", width=100,
                             anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(row, text=str(product['stock_quantity']), text_color="black", font=("Arial", 12), width=50,
                             anchor="w").pack(side="left", padx=10)

        except Error as e:
            ctk.CTkLabel(stock_list_frame, text=f"Error loading stock: {e}", text_color="red").pack()
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    load_stock_table()

    return parent_frame