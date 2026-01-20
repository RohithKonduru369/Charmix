import uuid
from tkinter.constants import INSERT
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import datetime
import mysql.connector
from mysql.connector import Error
import user_session
from Routine import create_questionnaire_ui
from menu import create_menu_ui
from Product_description_screen import create_product_desc_ui
def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print(f"Error loading image r'{image_url}': {e}")
        placeholder = Image.new('RGB', size, (200, 200, 200))
        return ImageTk.PhotoImage(placeholder)

def create_checkout_ui(master, cart_data=None, previous_frame=None):
    if cart_data is None:
        cart_data = {}

    # --- 1. Main Frame Setup ---
    cart_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    cart_frame.pack_propagate(False)
    cart_frame.place(x=0, y=0)

    SHIPPING_COST = 5.00

    back_icon = resize_image((30, 30), r"Images\arrow_back.png")
    menu_icon = resize_image((40, 40), r"Images\menu.png")
    routine_icon = resize_image((30, 30), r"Images\routine.png")
    cart_icon = resize_image((30, 30), r"Images\cart.png")
    trash_icon = resize_image((20, 20), r"Images\delete.png")
    # Use CTkImage for the search icon label
    search_icon = resize_image((20, 20), r"Images\search.png")

    # --- Navigation ---
    def go_to_home():
        # Import inside function to avoid circular import
        from home_screen import create_home_ui
        cart_frame.place_forget()
        # We default name to "User" here, or you could fetch it if needed
        create_home_ui(master, first_name="User")

    def go_to_routine():
        cart_frame.place_forget()
        create_questionnaire_ui(master)

    def go_to_cart():
        print("Already on cart page.")

    def perform_search():
        query = search_entry.get()
        from search import perform_global_search
        # Pass cart_frame so it can be hidden
        perform_global_search(master, query, current_frame=cart_frame)

    def go_to_menu():
        # Pass cart_frame so menu can manage it
        create_menu_ui(master, overlay_on_frame=cart_frame)

    # --- 4. Header Content ---
    back_btn = ctk.CTkButton(cart_frame, text="", image=back_icon, width=40, height=40,
                             fg_color="transparent", hover_color="#D59CFF",
                             bg_color="#E0B0FF", command=go_to_home)
    back_btn.place(x=20, y=30)

    menu_btn = ctk.CTkButton(cart_frame, text="", image=menu_icon, width=40, height=40,
                             fg_color="transparent", hover_color="#D59CFF",
                             bg_color="#E0B0FF", command=go_to_menu)
    menu_btn.image = menu_icon
    menu_btn.place(x=70, y=30)

    search_frame = ctk.CTkFrame(cart_frame, fg_color="white", corner_radius=15,
                                width=350, height=40, bg_color="#E0B0FF")
    search_frame.place(relx=0.5, y=40, anchor="center")
    search_frame.pack_propagate(False)

    search_icon_label = ctk.CTkLabel(search_frame, text="", image=search_icon, fg_color="transparent", bg_color="white")
    search_icon_label.place(x=20, y=20, anchor="center")

    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search for products, routines...",
                                fg_color="transparent", text_color="black", border_width=0)
    search_entry.pack(side="left", fill="x", expand=True, padx=(35, 10))  # Added padding for icon
    search_entry.bind("<Return>", lambda event: perform_search())

    routine_btn = ctk.CTkButton(cart_frame, text="", image=routine_icon, width=30, command=go_to_routine,
                                fg_color="transparent", bg_color="#E0B0FF", hover_color="#D59CFF")
    routine_btn.image = routine_icon
    routine_btn.place(x=570, y=35)

    cart_btn = ctk.CTkButton(cart_frame, text="", image=cart_icon, width=30, command=go_to_cart,
                             fg_color="transparent", bg_color="#E0B0FF", hover_color="#D59CFF")
    cart_btn.image = cart_icon
    cart_btn.place(x=630, y=35)

    # --- Body ---
    cart_title_label = ctk.CTkLabel(cart_frame, text="Your Cart (0 Items)",
                                    font=("Arial", 24, "bold"), text_color="black", bg_color="#E0B0FF")
    cart_title_label.place(x=30, y=120)

    cart_scroll_frame = ctk.CTkScrollableFrame(cart_frame, fg_color="transparent", width=380, height=450)
    cart_scroll_frame.place(x=20, y=160)

    summary_frame = ctk.CTkFrame(cart_frame, fg_color="white", width=250, height=250, corner_radius=20,
                                 bg_color="#E0B0FF")
    summary_frame.place(x=430, y=180)
    summary_frame.pack_propagate(False)
    ctk.CTkLabel(summary_frame, text="Order Summary", font=("Arial", 18, "bold"), text_color="black").pack(anchor="w",
                                                                                                           padx=20,
                                                                                                           pady=(15, 5))
    subtotal_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
    subtotal_frame.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(subtotal_frame, text="Subtotal:", text_color="gray").pack(side="left")
    subtotal_label = ctk.CTkLabel(subtotal_frame, text="$0.00", text_color="black")
    subtotal_label.pack(side="right")
    shipping_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
    shipping_frame.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(shipping_frame, text="Shipping:", text_color="gray").pack(side="left")
    shipping_label = ctk.CTkLabel(shipping_frame, text=f"${SHIPPING_COST:.2f}", text_color="black")
    shipping_label.pack(side="right")
    ctk.CTkFrame(summary_frame, height=1, fg_color="#E0E0E0").pack(fill="x", padx=20, pady=10)
    total_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
    total_frame.pack(fill="x", padx=20, pady=5)
    ctk.CTkLabel(total_frame, text="Total:", font=("Arial", 14, "bold"), text_color="black").pack(side="left")
    total_label = ctk.CTkLabel(summary_frame, text="$0.00", font=("Arial", 14, "bold"), text_color="black")
    total_label.place(x=180, y=155)

    def proceed_to_checkout():
        if not cart_data:
            messagebox.showerror("Empty Cart", "Your cart is empty.")
            return
        messagebox.showinfo("Checkout", "Proceeding to checkout with a total of " + total_label.cget("text"))

        #1 USer Session:
        user_email = user_session.get_current_user()
        if not user_email:
            messagebox.showerror("Error", "You must be logged in to checkout.")
            return

        # 2. Calculate Total
        total_str = total_label.cget("text").replace("$", "")
        total_val = float(total_str)

        try:
            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor(dictionary=True)


            # 3. Get Customer ID from Email
            cursor.execute("SELECT id, customer_code FROM users WHERE email = %s", (user_email,))
            user_row = cursor.fetchone()
            if not user_row:
                messagebox.showerror("Error", "User ID not found for this email.")
                return
            customer_id = user_row['id']
            customer_code = user_row['customer_code']

            if not customer_code:
                customer_code = str(customer_id)

            # 4. Determine Sequence Number (How many orders today?)
            today_date = datetime.date.today()  # YYYY-MM-DD
            cursor.execute("SELECT COUNT(*) as count FROM Orders WHERE customer_id = %s AND order_date = %s",
                           (customer_id, today_date))
            count_row = cursor.fetchone()
            sequence = count_row['count'] + 1  # 1st order is 1, 2nd is 2, etc.

            # 5. Format Order ID: YYYYMMDD-custID-Seq
            date_str = today_date.strftime("%Y%m%d")
            # Zfill(2) ensures '1' becomes '01'
            order_id = f"{date_str}-{customer_id}-{str(sequence).zfill(2)}"

            # 6. Insert Order
            insert_sql = """
                         INSERT INTO Orders (order_id, customer_id, customer_email, order_date, order_status, \
                                             order_sequence, total_amount)
                         VALUES (%s, %s, %s, %s, %s, %s, %s) \
                         """
            cursor.execute(insert_sql,
                           (order_id, customer_id, user_email, today_date, 'Processing', sequence, total_val))
            for prod_key, quantity in cart_data.items():
                db_id = prod_key.split('_')[1]
                update_stock_sql = "UPDATE products SET stock_quantity = stock_quantity - %s WHERE id = %s"
                cursor.execute(update_stock_sql, (quantity, db_id))

            conn.commit()

            messagebox.showinfo("Success", f"Order placed successfully!\nOrder ID: {order_id}")

            # 7. Clear Cart & Go Home
            cart_data.clear()
            rebuild_cart_items()  # Refresh UI to show empty
            go_to_home()

        except Error as e:
            messagebox.showerror("Database Error", f"Could not place order: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close();
                conn.close()

    checkout_btn = ctk.CTkButton(cart_frame, text="Proceed to Checkout",
                                 width=250, height=45, corner_radius=25,
                                 fg_color="#4DB6AC", hover_color="#00897B",
                                 bg_color="#E0B0FF", text_color="white",
                                 font=("Arial", 16, "bold"),
                                 command=proceed_to_checkout)
    checkout_btn.place(x=430, y=450)

    # --- DB Fetch Function ---
    def load_all_product_data():
        all_products = {}
        try:
            conn = mysql.connector.connect(
                host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor(dictionary=True)

            # 1. Fetch from Main Products Table
            cursor.execute("SELECT id, name, brand, price, image_path FROM products")
            for row in cursor.fetchall():
                all_products[f"prod_{row['id']}"] = row

            # 2. Fetch from Routine Products Table (products1)
            cursor.execute("SELECT id, product_name, brand, price, image_path FROM products1")
            for row in cursor.fetchall():
                # Normalize key names to match the first table
                row['name'] = row['product_name']
                # Use a different prefix 'routine_' to avoid ID collision
                all_products[f"routine_{row['id']}"] = row

        except Error as e:
            print(f"Database Error: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
        return all_products

    ALL_PRODUCTS_DB = load_all_product_data()

    def rebuild_cart_items():
        for widget in cart_scroll_frame.winfo_children():
            widget.destroy()
        subtotal = 0.0
        total_items = 0

        for prod_id, quantity in cart_data.items():
            if prod_id not in ALL_PRODUCTS_DB: continue
            product = ALL_PRODUCTS_DB[prod_id]
            item_total = float(product["price"]) * quantity
            subtotal += item_total
            total_items += quantity

            item_card = ctk.CTkFrame(cart_scroll_frame, fg_color="white", corner_radius=15, height=100)
            item_card.pack(fill="x", pady=5)
            item_card.pack_propagate(False)

            def open_description(event, p=product, pid=prod_id):
                p["db_id"] = prod_id
                cart_frame.place_forget()
                create_product_desc_ui(master, p, cart_data, previous_frame=cart_frame)

            item_card.bind("<Button-1>", open_description)

            img_placeholder = ctk.CTkFrame(item_card, width=60, height=60, fg_color="#F0F0F0", corner_radius=10)
            img_placeholder.place(x=20, y=20)
            prod_img_small = resize_image((50,50), product["image_path"])
            img_lbl = ctk.CTkLabel(img_placeholder, text="", image=prod_img_small)
            img_lbl.image = prod_img_small
            img_lbl.place(relx=0.5, rely=0.5, anchor="center")
            img_lbl.bind("<Button-1>", open_description)
            name_lbl = ctk.CTkLabel(item_card, text=product["name"], font=("Arial", 16, "bold"), text_color="black")
            name_lbl.place(x=100, y=20)
            name_lbl.bind("<Button-1>", open_description)

            ctk.CTkLabel(item_card, text=product["brand"], font=("Arial", 12), text_color="gray").place(x=100, y=45)
            ctk.CTkLabel(item_card, text=f"${item_total:.2f}", font=("Arial", 14, "bold"), text_color="black").place(
                x=250, y=45)

            def update_quantity(pid, amount):
                cart_data[pid] += amount
                if cart_data[pid] <= 0: cart_data[pid] = 1
                rebuild_cart_items()

            def remove_item(pid):
                if pid in cart_data: cart_data.pop(pid)
                rebuild_cart_items()

            minus_btn = ctk.CTkButton(item_card, text="-", width=25, height=25,
                                      command=lambda pid=prod_id: update_quantity(pid, -1))
            minus_btn.place(x=100, y=70)
            qty_label = ctk.CTkLabel(item_card, text=str(quantity), font=("Arial", 14), width=30)
            qty_label.place(x=130, y=70)
            plus_btn = ctk.CTkButton(item_card, text="+", width=25, height=25,
                                     command=lambda pid=prod_id: update_quantity(pid, 1))
            plus_btn.place(x=165, y=70)

            remove_btn = ctk.CTkButton(item_card, text="", image=trash_icon, width=25, height=25,
                                       fg_color="transparent", hover_color="#FEF0F0",
                                       command=lambda pid=prod_id: remove_item(pid))
            remove_btn.image = trash_icon
            remove_btn.place(x=340, y=70)

        subtotal_label.configure(text=f"${subtotal:.2f}")
        if total_items > 0:
            total_label.configure(text=f"${subtotal + SHIPPING_COST:.2f}")
            shipping_label.configure(text=f"${SHIPPING_COST:.2f}")
        else:
            total_label.configure(text="$0.00")
            shipping_label.configure(text="$0.00")
        cart_title_label.configure(text=f"Your Cart ({total_items} Items)")

    rebuild_cart_items()
    return cart_frame


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Checkout Screen (Test Mode)")
    root.geometry("700x600")
    create_checkout_ui(root, cart_data={"prod_001":2})
    root.mainloop()