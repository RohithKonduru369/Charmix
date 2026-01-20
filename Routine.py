import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error

# --- Imports ---
from shop_screen import create_shop_ui
import user_session  # <--- IMPORT ADDED


# --- Image Resizer ---
def resize_image(size, image_url):
    try:
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        placeholder = Image.new('RGB', size, (200, 200, 200))
        return ImageTk.PhotoImage(placeholder)


def create_questionnaire_ui(root):
    # --- 1. Main Frame Setup ---
    scroll_frame = ctk.CTkScrollableFrame(root, fg_color="#E0B0FF", width=700, height=600)
    scroll_frame.pack(fill="both", expand=True)

    # --- 2. Load Icons ---
    try:
        back_icon = resize_image((30, 30), r"Images\arrow_back.png")
    except:
        back_icon = None

    # --- 3. Navigation Functions ---
    def go_back():
        from home_screen import create_home_ui
        scroll_frame.pack_forget()
        create_home_ui(root)

    back_btn = ctk.CTkButton(scroll_frame, text=" Back", image=back_icon, width=100, height=40,
                             fg_color="transparent", hover_color="#D59CFF", text_color="black",
                             font=("Arial", 14, "bold"), anchor="w",
                             command=go_back)
    back_btn.pack(anchor="w", padx=20, pady=(20, 0))

    title = ctk.CTkLabel(scroll_frame, text="Let's Personalize Your Routine",
                         font=("Arial", 25, "bold"), text_color="black")
    title.pack(pady=(10, 5), padx=50, anchor="w")

    # --- Data Storage Variables ---
    q1_cleansing_feel = ctk.StringVar()
    q2_dry_patches = ctk.StringVar()
    q3_tzone_midday = ctk.StringVar()
    q4_pores_visibility = ctk.StringVar()
    q5_breakouts = ctk.StringVar()
    q6_new_products = ctk.StringVar()
    q7_sun_reaction = ctk.StringVar()
    q8_concerns = {
        "Acne": ctk.BooleanVar(), "Pigmentation": ctk.BooleanVar(),
        "Sensitivity": ctk.BooleanVar(), "Dryness": ctk.BooleanVar(),
        "Aging": ctk.BooleanVar(), "None": ctk.BooleanVar(),
    }

    # --- LOGIC TO DETERMINE CATEGORY ---
    def get_recommendations_from_db(user_profile):

        # 1. Initialize Scores
        scores = {
            "Acne": 0, "Sensitive": 0, "Dry": 0,
            "Oily": 0, "Texture": 0, "Sun": 0
        }

        # 2. SCORING LOGIC
        ans1 = user_profile.get('q1_cleansing_feel')
        if ans1 == "Tight & Dry":
            scores['Dry'] += 2
        elif ans1 == "Very Oily":
            scores['Oily'] += 2
        elif ans1 == "Slightly Oily":
            scores['Texture'] += 1

        ans3 = user_profile.get('q3_tzone_midday')
        if ans3 == "Very Shiny":
            scores['Oily'] += 2
        elif ans3 == "Slightly Shiny":
            scores['Texture'] += 1
        elif ans3 == "Still Matte":
            scores['Dry'] += 1

        if user_profile.get('q5_breakouts') in ["Frequently", "Almost Always"]:
            scores['Acne'] += 3

        if user_profile.get('q7_sun_reaction') in ["Yes, Easily", "Very Easily"]:
            scores['Sensitive'] += 2
            scores['Sun'] += 1

        concerns = user_profile.get('q8_concerns', [])
        if "Acne" in concerns: scores['Acne'] += 3
        if "Dryness" in concerns: scores['Dry'] += 3
        if "Sensitivity" in concerns: scores['Sensitive'] += 3
        if "Pigmentation" in concerns: scores['Texture'] += 3
        if "Aging" in concerns: scores['Texture'] += 2

        winner_concern = max(scores, key=scores.get)
        print(f"DEBUG: Winner Concern: {winner_concern}")

        # 3. Map Concern to Routine ID
        routine_map = {
            "Acne": "Routine_2", "Sensitive": "Routine_3",
            "Dry": "Routine_4", "Oily": "Routine_5",
            "Texture": "Routine_6", "Sun": "Routine_1"
        }

        target_routine_id = routine_map.get(winner_concern, "Routine_1")

        # 4. Fetch products
        recommended_products = {}
        conn = None
        try:
            conn = mysql.connector.connect(
                host="141.209.241.57", user="kondu2r", password="mypass", database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor(dictionary=True)
            query = """
                    SELECT id, product_name, brand, price, image_path, description, routine_id
                    FROM products1
                    WHERE routine_id = %s \
                    """
            cursor.execute(query, (target_routine_id,))
            results = cursor.fetchall()

            for row in results:
                normalized_row = {
                    "name": row['product_name'],
                    "brand": row['brand'],
                    "price": row['price'],
                    "image_path": row['image_path'],
                    "product_desc": row['description'],
                    "db_id": row['id']
                }
                prod_key = f"routine_{row['id']}"
                recommended_products[prod_key] = normalized_row

        except Error as e:
            messagebox.showerror("Database Error", f"Could not fetch recommendations: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close();
                conn.close()

        return winner_concern, recommended_products

    def on_submit_routine(questionnaire_frame):
        selected_concerns = [k for k, v in q8_concerns.items() if v.get()]

        if not selected_concerns and not q1_cleansing_feel.get():
            messagebox.showwarning("Incomplete", "Please answer the basic questions so we can help you!")
            return

        user_profile = {
            "q1_cleansing_feel": q1_cleansing_feel.get(),
            "q3_tzone_midday": q3_tzone_midday.get(),
            "q5_breakouts": q5_breakouts.get(),
            "q7_sun_reaction": q7_sun_reaction.get(),
            "q8_concerns": selected_concerns,
        }

        category_name, product_list = get_recommendations_from_db(user_profile)

        if not product_list:
            messagebox.showinfo("Info", f"We identified your skin as {category_name}, but found no products.")
            scroll_frame.pack_forget()
            create_shop_ui(root)
        else:
            # --- SAVE TO SESSION HERE ---
            user_session.set_user_routine(category_name, product_list)

            messagebox.showinfo("Success",
                                f"Your Skin Type: {category_name}\n\nWe have curated a routine just for you!")
            scroll_frame.pack_forget()
            create_shop_ui(root, custom_product_list=product_list, title_text=f"Your {category_name} Routine")

    def create_question_card(parent, question_text, options, variable, width=300, height=200):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=20, width=width, height=height)
        card.pack(side="left", padx=10, pady=5, expand=True)
        card.pack_propagate(False)

        title = ctk.CTkLabel(card, text=question_text, font=("Arial", 16, "bold"),
                             text_color="black", wraplength=260, justify="left")
        title.place(x=20, y=20)

        seg_button = ctk.CTkSegmentedButton(card, values=options, variable=variable,
                                            width=260, height=35,
                                            selected_color="#9370DB",
                                            selected_hover_color="#7B5DB8",
                                            unselected_color="#F0F0F0",
                                            unselected_hover_color="#E0E0E0",
                                            text_color="black")
        seg_button.place(x=20, y=100)
        return card

    # --- UI LAYOUT ---
    section1_title = ctk.CTkLabel(scroll_frame, text="Basic Profile", font=("Arial", 20, "bold"), text_color="#333333")
    section1_title.pack(pady=(20, 5), padx=50, anchor="w")

    row1 = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    row1.pack(pady=10, padx=20, fill="x")
    create_question_card(row1, "1. How does skin feel after cleansing?",
                         ["Tight & Dry", "Comfortable", "Slightly Oily", "Very Oily"], q1_cleansing_feel)
    create_question_card(row1, "2. Do you experience dry patches?", ["Never", "Sometimes", "Often"], q2_dry_patches)

    row2 = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    row2.pack(pady=10, padx=20, fill="x")
    create_question_card(row2, "3. Midday T-zone status?", ["Still Matte", "Slightly Shiny", "Very Shiny"],
                         q3_tzone_midday)
    create_question_card(row2, "4. Pore visibility?", ["Hardly", "Slightly", "Clearly", "Large"], q4_pores_visibility)

    row3 = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    row3.pack(pady=10, padx=20, fill="x")
    create_question_card(row3, "5. How often do you breakout?",
                         ["Rarely", "Occasionally", "Frequently", "Almost Always"], q5_breakouts)
    create_question_card(row3, "6. Reaction to new products?", ["No Reaction", "Mild Tingling", "Redness", "Breakouts"],
                         q6_new_products)

    row4 = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    row4.pack(pady=10, padx=20, fill="x")
    create_question_card(row4, "7. Sun reaction?", ["Not Really", "Slightly", "Yes, Easily", "Very Easily"],
                         q7_sun_reaction)

    card8 = ctk.CTkFrame(row4, fg_color="white", corner_radius=20, width=300, height=200)
    card8.pack(side="left", padx=10, pady=5, expand=True)
    card8.pack_propagate(False)
    ctk.CTkLabel(card8, text="8. Select your main concerns", font=("Arial", 16, "bold"),
                 text_color="black", wraplength=260).place(x=20, y=20)
    ctk.CTkCheckBox(card8, text="Acne", variable=q8_concerns["Acne"], text_color="black").place(x=30, y=60)
    ctk.CTkCheckBox(card8, text="Pigmentation", variable=q8_concerns["Pigmentation"], text_color="black").place(x=150,
                                                                                                                y=60)
    ctk.CTkCheckBox(card8, text="Sensitivity", variable=q8_concerns["Sensitivity"], text_color="black").place(x=30,
                                                                                                              y=100)
    ctk.CTkCheckBox(card8, text="Dryness", variable=q8_concerns["Dryness"], text_color="black").place(x=150, y=100)
    ctk.CTkCheckBox(card8, text="Aging", variable=q8_concerns["Aging"], text_color="black").place(x=30, y=140)

    submit_button = ctk.CTkButton(scroll_frame, text="Get My Routine", font=("Arial", 18, "bold"),
                                  height=50, width=300, fg_color="#9370DB", hover_color="#F6CA51",
                                  corner_radius=25, border_width=2, border_color="black",
                                  command=lambda: on_submit_routine(scroll_frame))
    submit_button.pack(pady=40)

    return scroll_frame