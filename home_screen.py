import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import random
import mysql.connector
from mysql.connector import Error

from Product_description_screen import create_product_desc_ui

from menu import create_menu_ui
from Routine import create_questionnaire_ui
import user_session

GLOBAL_CART = {}

# --- Image Resizer ---
def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print(f"Error loading image r'{image_url}': {e}")
        placeholder = Image.new('RGB', size, (200, 200, 200))
        return ImageTk.PhotoImage(placeholder)

def create_product_card(parent, product_id, product_info, master_window, home_frame):
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, width=150, height=200)
    card.pack(side="left", padx=10, pady=10)  # Pack horizontally
    card.pack_propagate(False)

    def open_description(event):
        product_info["db_id"] = product_id
        home_frame.place_forget()
        create_product_desc_ui(master_window, product_info, GLOBAL_CART, previous_frame=home_frame)

        # Bind click to card background
        card.bind("<Button-1>", open_description)

    # Load product image
    product_image = resize_image((120, 100), product_info["image_path"])  # Use PhotoImage
    img_label = ctk.CTkLabel(card, text="", image=product_image)
    img_label.image = product_image  # Keep a reference
    img_label.pack(pady=(10, 5))
    img_label.bind("<Button-1>", open_description)

    name_lbl = ctk.CTkLabel(card, text=product_info["name"], font=("Arial", 14, "bold"), text_color="black")
    name_lbl.pack(pady=0, padx=15, anchor="w")
    name_lbl.bind("<Button-1>", open_description) # Bind click to name

    ctk.CTkLabel(card, text=product_info["brand"], font=("Arial", 12), text_color="gray").pack(pady=0, padx=15,
                                                                                               anchor="w")

    bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
    bottom_frame.pack(fill="x", padx=15, pady=(5, 0), anchor="s")

    ctk.CTkLabel(bottom_frame, text=f"${product_info['price']:.2f}", font=("Arial", 14, "bold"),
                 text_color="black").pack(side="left")

    def add_to_cart():
        if product_id in GLOBAL_CART:
            GLOBAL_CART[product_id] += 1
        else:
            GLOBAL_CART[product_id] = 1

        if go_to_checkout:
            from Checkout import create_checkout_ui
            home_frame.place_forget()
            create_checkout_ui(master_window, cart_data=GLOBAL_CART)

    cart_icon = resize_image((25, 25), r"Images\addcart.png")  # Use PhotoImage
    cart_button = ctk.CTkButton(bottom_frame, text="", image=cart_icon, width=25, height=25,
                                fg_color="transparent", hover_color="#F0F0F0",
                                command=add_to_cart)
    cart_button.image = cart_icon  # Keep reference
    cart_button.pack(side="right")

    return card

def create_carousel(parent, title, product_list, master_window, home_frame):

    ctk.CTkLabel(parent, text=title, font=("Arial", 20, "bold"), text_color="black").pack(anchor="w", padx=20,
                                          pady=(20, 5))
    carousel_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=240,
                                            orientation="horizontal")
    carousel_frame.pack(fill="x")

    for prod_id, prod_info in product_list.items():
        create_product_card(carousel_frame, prod_id, prod_info, master_window, home_frame)


def load_products_from_db():
    products_dict = {}
    try:
        conn = mysql.connector.connect(
            host="141.209.241.57",
            user="kondu2r",
            password="mypass",
            database="BIS698Fall25_GRP4"
        )
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, name, brand, price, image_path, category FROM products"
        cursor.execute(query)

        for row in cursor.fetchall():
            product_id = f"prod_{row['id']}"  # Create a "prod_001" style ID
            products_dict[product_id] = {
                "name": row["name"],
                "brand": row["brand"],
                "price": float(row["price"]),  # Convert from Decimal
                "image_path": row["image_path"],
                "category": row["category"],
                "product_desc": row.get("product_desc", " No Description available")
            }

    except Error as e:
        print(f"Database Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return products_dict


def create_home_ui(master, first_name="first_name"):

    if first_name == "first_name":
        email = user_session.get_current_user()
        if email:
            try:
                conn = mysql.connector.connect(
                    host="141.209.241.57",
                    user="kondu2r",
                    password="mypass",
                    database="BIS698Fall25_GRP4"
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT first_name FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    first_name = result["first_name"]
                if 'conn' in locals() and conn.is_connected(): conn.close()
            except: pass

    home_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    home_frame.pack_propagate(False)
    home_frame.place(x=0, y=0)

    menu_icon = resize_image((40, 40), r"Images\menu.png")
    routine_icon = resize_image((30, 30), r"Images\routine.png")
    cart_icon = resize_image((30, 30), r"Images\cart.png")
    search_icon_img = resize_image((20, 20), r"Images\search.png")

    def go_to_menu():
        create_menu_ui(master, overlay_on_frame=home_frame)

    def go_to_routine():
        category, products = user_session.get_user_routine()

        if products:
            # If yes, go straight to Shop Screen with those products
            from shop_screen import create_shop_ui
            home_frame.place_forget()
            create_shop_ui(master, custom_product_list=products, title_text=f"Your {category} Routine")
        else:
            # If no, go to Questionnaire
            home_frame.place_forget()
            create_questionnaire_ui(master)

    def go_to_cart():
        # Import inside function prevents circular import crash
        from Checkout import create_checkout_ui
        home_frame.place_forget()
        # Pass the GLOBAL_CART to the checkout screen
        create_checkout_ui(master, cart_data=GLOBAL_CART)

    def perform_search():
        query = search_entry.get()
        # Import dynamically to avoid circular import
        from search import perform_global_search
        perform_global_search(master, query, current_frame=home_frame)

    menu_btn = ctk.CTkButton(home_frame, text="", image=menu_icon, width=40, height=40,
                             fg_color="transparent", hover_color="#D59CFF", command=go_to_menu)
    menu_btn.image = menu_icon
    menu_btn.place(x=20, y=30)

    search_frame = ctk.CTkFrame(home_frame, fg_color="white", corner_radius=15, width=350, height=40)
    search_frame.place(relx=0.5, y=40, anchor="center")
    search_frame.pack_propagate(False)
    search_icon_label = ctk.CTkLabel(search_frame, text="", image=search_icon_img, fg_color="transparent",
                                     bg_color="white", corner_radius=20)
    search_icon_label.image = search_icon_img
    search_icon_label.place(x=25, y=20, anchor="center")
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search for products...", fg_color="transparent",
                                text_color="black", border_width=0)
    search_entry.pack(side="left", fill="x", expand=True, padx=(35, 10))
    search_entry.bind("<Return>", lambda e: perform_search())

    routine_btn = ctk.CTkButton(home_frame, text="", image=routine_icon, width=30, command=go_to_routine,
                                fg_color="transparent", hover_color="#D59CFF")
    routine_btn.image = routine_icon
    routine_btn.place(x=570, y=35)

    cart_btn = ctk.CTkButton(home_frame, text="", image=cart_icon, width=30, command=go_to_cart,
                             fg_color="transparent", hover_color="#D59CFF")  # <-- EDITED: Fixed hover color
    cart_btn.image = cart_icon
    cart_btn.place(x=630, y=35)

    page_content_frame = ctk.CTkScrollableFrame(home_frame, fg_color="transparent")
    page_content_frame.place(x=0, y=100, relwidth=1.0, relheight=0.83)  # <-- EDITED: Changed placement

    ctk.CTkLabel(page_content_frame, text=f"Welcome back, {first_name}!",
                 font=("Arial", 24, "bold"), text_color="black").pack(anchor="w", padx=20, pady=(10, 0))


    all_products = load_products_from_db()
    skincare_products = {k: v for k, v in all_products.items() if v["category"] == "skincare"}
    haircare_products = {k: v for k, v in all_products.items() if v["category"] == "haircare"}
    makeup_products = {k: v for k, v in all_products.items() if v["category"] == "makeup"}

    # Get 5 random products for "Top Picks"
    if all_products:  # Only sample if products were loaded
        random_ids = random.sample(list(all_products.keys()), min(len(all_products), 5))
        top_picks = {k: all_products[k] for k in random_ids}
    else:
        top_picks = {}

    create_carousel(page_content_frame, "Top Picks For You", top_picks, master, home_frame)
    create_carousel(page_content_frame, "Skincare", skincare_products, master, home_frame)
    create_carousel(page_content_frame, "Hair Care", haircare_products, master, home_frame)
    create_carousel(page_content_frame, "Makeup", makeup_products, master, home_frame)

    ctk.CTkFrame(page_content_frame, height=20, fg_color="transparent").pack()  # Add spacing at the bottom

    return home_frame


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Home Screen (Test Mode)")
    root.geometry("700x600")
    create_home_ui(root, first_name="Sarah")  # Pass a test name
    root.mainloop()