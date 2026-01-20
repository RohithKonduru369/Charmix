import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

# --- Image Resizer ---
def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        # Return a grey placeholder if image is missing
        return ImageTk.PhotoImage(Image.new('RGB', size, (200, 200, 200)))


def create_product_desc_ui(master, product_info, cart_data, previous_frame=None):
    # -------- MAIN FRAME --------
    pd_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    pd_frame.pack_propagate(False)
    pd_frame.place(x=0, y=0)

    # --- Load Icons ---
    try:
        back_icon = resize_image((30, 30), r"Images\arrow_back.png")
        routine_icon = resize_image((30, 30), r"Images\routine.png")
        cart_icon = resize_image((30, 30), r"Images\cart.png")
    except:
        back_icon = None
        routine_icon = None
        cart_icon = None

    # -------- TOP BAR --------
    top_bar = ctk.CTkFrame(pd_frame, fg_color="transparent")
    top_bar.pack(fill="x", pady=10, padx=10)

    def go_back():
        pd_frame.destroy()
        if previous_frame:
            # Re-show the previous frame (Home or Shop)
            previous_frame.place(x=0, y=0)
            # If it's the home screen, ensure it's visible
            try:
                previous_frame.pack_propagate(False)
            except:
                pass
        else:
            # Fallback
            from home_screen import create_home_ui
            create_home_ui(master)

    def go_to_checkout():
        from Checkout import create_checkout_ui
        pd_frame.place_forget()
        create_checkout_ui(master, cart_data=cart_data)

    def go_to_routine():
        # Import dynamically to check session
        import user_session
        from shop_screen import create_shop_ui
        from Routine import create_questionnaire_ui

        category, products = user_session.get_user_routine()

        pd_frame.place_forget()
        if products:
            create_shop_ui(master, custom_product_list=products, title_text=f"Your {category} Routine")
        else:
            create_questionnaire_ui(master)

    # Back Button
    back_btn = ctk.CTkButton(top_bar, text="", image=back_icon, width=40, height=40,
                             fg_color="transparent", hover_color="#D59CFF",
                             command=go_back)
    back_btn.pack(side="left", padx=10)

    # --- SEARCH BAR ---
    def perform_search(event=None):
        query = search_entry.get()
        from search import perform_global_search
        perform_global_search(master, query, current_frame=pd_frame)

    search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search...", width=400, height=38, corner_radius=20)
    search_entry.pack(side="left", padx=20)
    search_entry.bind("<Return>", perform_search)

    # Right Side Icons (Routine & Cart)
    # We place them absolutely to the right of the frame

    # Routine Button
    routine_btn = ctk.CTkButton(pd_frame, text="", image=routine_icon, width=30,
                                fg_color="transparent", hover_color="#D59CFF",
                                command=go_to_routine)
    routine_btn.place(x=570, y=16)

    # Cart Button
    cart_btn = ctk.CTkButton(pd_frame, text="", image=cart_icon, width=30,
                             fg_color="transparent", hover_color="#D59CFF",
                             command=go_to_checkout)
    cart_btn.place(x=630, y=16)

    # -------- MAIN WHITE CARD --------
    card = ctk.CTkFrame(pd_frame, fg_color="white", corner_radius=20, width=650, height=480)
    card.pack(pady=15, padx=20)
    card.pack_propagate(False)

    # -------- PHOTO (LEFT SIDE) --------
    # Load the actual product image
    img_path = product_info.get("image_path", "")
    product_img = resize_image((250, 250), img_path)

    img_label = ctk.CTkLabel(card, image=product_img, text="")
    img_label.image = product_img
    img_label.place(x=30, y=40)

    # -------- TEXT (RIGHT SIDE) --------
    # Use .get() to handle both 'name' and 'product_name' keys
    name_text = product_info.get("name", product_info.get("product_name", "Unknown Product"))

    title = ctk.CTkLabel(card, text=name_text,
                         font=("Arial", 20, "bold"), text_color="black", anchor="w", wraplength=300, justify="left")
    title.place(x=320, y=40)

    brand_text = product_info.get("brand", "Unknown Brand")
    brand_label = ctk.CTkLabel(card, text=brand_text, font=("Arial", 14, "bold"), text_color="gray")
    brand_label.place(x=320, y=80)  # Adjusted Y position

    # Rating (Static for now)
    rating = ctk.CTkLabel(card, text="⭐⭐⭐⭐⭐  (4.9 stars · 250 reviews)",
                          font=("Arial", 13), text_color="black")
    rating.place(x=320, y=110)


    # Price
    price_val = float(product_info.get("price", 0.0))
    price_label = ctk.CTkLabel(card, text=f"${price_val:.2f}", font=("Arial", 22, "bold"),
                               text_color="black", anchor="w")
    price_label.place(x=320, y=260)

    shipping_label = ctk.CTkLabel(card, text="+ Free Shipping", font=("Arial", 12),
                                  text_color="gray", anchor="w")
    shipping_label.place(x=320, y=295)

    # -------- BUTTONS --------
    def add_cart():

        if "db_id" in product_info:
            pass

        prod_key = product_info.get("db_id")  # This expects the key like 'prod_1' or 'routine_2'

        if prod_key:
            if prod_key in cart_data:
                cart_data[prod_key] += 1
            else:
                cart_data[prod_key] = 1
            go_to_checkout()
        else:
            messagebox.showerror("Error", "Could not identify product ID.")

    btn_cart = ctk.CTkButton(card, text="Add to Cart", command=add_cart,
                             fg_color="#8CD790", hover_color="#6CB070",
                             width=140, height=40, corner_radius=20)
    btn_cart.place(x=320, y=330)

    # -------- PERSONALIZED INSIGHTS --------
    ctk.CTkLabel(card, text="Personalized Insights",
                 font=("Arial", 14, "bold"), text_color="black").place(x=320, y=390)

    insights = (
        "• Matches your skin goals.\n"
        "• Contains recommended Ingredients"
    )
    ctk.CTkLabel(card, text=insights, font=("Arial", 12),
                 text_color="black", justify="left").place(x=320, y=420)

    return pd_frame