import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error


# --- Image Resizer ---
def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        # Return a grey placeholder if image is missing
        return ImageTk.PhotoImage(Image.new('RGB', size, (200, 200, 200)))


def create_product_card(parent, product_info, prod_id):
    """Helper function to create a small product card with Add to Cart logic"""
    # Card Container - Kept white for contrast against the purple background
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, width=160, height=260)
    card.pack_propagate(False)

    # 1. Product Image
    image_path = product_info.get("image_path", "")
    product_image = resize_image((120, 120), image_path)

    img_label = ctk.CTkLabel(card, text="", image=product_image)
    img_label.image = product_image  # Keep reference
    img_label.pack(pady=(15, 5))

    # 2. Product Name & Brand
    name_text = product_info.get("name", product_info.get("product_name", "Unknown Product"))
    ctk.CTkLabel(card, text=name_text, font=("Arial", 14, "bold"),
                 text_color="black", wraplength=140).pack(pady=0, padx=5)

    ctk.CTkLabel(card, text=product_info.get("brand", ""), font=("Arial", 12),
                 text_color="gray").pack(pady=0, padx=5)

    # 3. Price & Button Container
    bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
    bottom_frame.pack(side="bottom", fill="x", padx=10, pady=15)

    price_val = float(product_info.get('price', 0.0))
    ctk.CTkLabel(bottom_frame, text=f"${price_val:.2f}", font=("Arial", 14, "bold"),
                 text_color="black").pack(side="left")

    def add_to_cart():
        try:
            from home_screen import GLOBAL_CART
            if prod_id in GLOBAL_CART:
                GLOBAL_CART[prod_id] += 1
            else:
                GLOBAL_CART[prod_id] = 1
            messagebox.showinfo("Cart", f"Added {name_text} to cart!")
        except ImportError:
            print("Could not import GLOBAL_CART from home_screen")

    ctk.CTkButton(bottom_frame, text="Add", width=50, height=25,
                  fg_color="#9370DB", hover_color="#F6CA51",
                  command=add_to_cart).pack(side="right")

    return card


def load_all_products_from_db():
    """Fetches ALL products from the main 'products' table (Default View)"""
    products_dict = {}
    try:
        conn = mysql.connector.connect(
            host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
        )
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, brand, price, image_path, category FROM products1"
        cursor.execute(query)
        for row in cursor.fetchall():
            product_id = f"prod_{row['id']}"
            products_dict[product_id] = row
    except Error as e:
        print(f"DB Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close();
            conn.close()
    return products_dict


def create_shop_ui(master, custom_product_list=None, title_text="Shop All Products"):
    """
    Creates the UI to display products with a unified purple background.
    """

    # --- 1. Main Frame Setup (UNIFIED COLOR) ---
    shop_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    shop_frame.pack_propagate(False)
    shop_frame.place(x=0, y=0)

    # --- 2. Header Content ---
    # Removed the 'bg_color' argument so it blends with the main frame
    ctk.CTkLabel(shop_frame, text=title_text, font=("Arial", 28, "bold"),
                 text_color="black").place(x=20, y=20)

    # Navigation Logic
    def go_home():
        from home_screen import create_home_ui
        shop_frame.place_forget()
        create_home_ui(master)

    # Updated button to blend better (removed bg_color="#D0EFFF")
    back_btn = ctk.CTkButton(shop_frame, text="< Back to Home", command=go_home,
                             fg_color="#9370DB", hover_color="#F6CA51",
                             text_color="white", width=120)
    back_btn.place(x=550, y=25)

    # --- 3. Scrollable Product Area ---
    # Set fg_color to "transparent" so the purple shows through
    scroll_area = ctk.CTkScrollableFrame(shop_frame, fg_color="transparent", width=660, height=480)
    scroll_area.place(x=20, y=80)

    # --- 4. Determine Data Source ---
    if custom_product_list:
        products_to_show = custom_product_list
    else:
        products_to_show = load_all_products_from_db()

    # --- 5. Grid Layout Logic ---
    if not products_to_show:
        ctk.CTkLabel(scroll_area, text="No products found.",
                     text_color="black", font=("Arial", 16)).pack(pady=50)
    else:
        row_frame = None
        col_count = 0
        max_cols = 3

        for prod_id, product in products_to_show.items():
            if col_count == 0:
                row_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
                row_frame.pack(fill="x", pady=10)

            card = create_product_card(row_frame, product, prod_id)
            card.pack(side="left", padx=15, expand=True)

            col_count += 1
            if col_count >= max_cols:
                col_count = 0

    return shop_frame