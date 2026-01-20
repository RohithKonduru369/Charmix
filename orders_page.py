import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import user_session

# --- Image Resizer ---
def resize_image(size, image_url):
    try:
        # This requires 'Image' from PIL
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize(size)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print(f"Error loading image r'{image_url}': {e}")
        # This also requires 'Image' from PIL
        placeholder = Image.new('RGB', size, (200, 200, 200))
        return ImageTk.PhotoImage(placeholder)


def create_orders_page(master, previous_frame=None):
    """Creates the My Orders screen."""

    orders_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    orders_frame.pack_propagate(False)
    orders_frame.place(x=0, y=0)

    # --- Load Icons ---
    back_icon = resize_image((30, 30), r"Images\arrow_back.png")
    app_logo = resize_image((50, 50), r"Images\icon.png")

    # --- Navigation ---
    def go_back():
        # Destroy current frame
        orders_frame.destroy()

        # 1. Restore the background frame
        if previous_frame:
            previous_frame.place(x=0, y=0)

            # 2. Re-open the Menu
            from menu_page import create_menu_ui
            create_menu_ui(master, overlay_on_frame=previous_frame)
        else:
            # Fallback if opened directly
            from home_screen import create_home_ui
            create_home_ui(master)

            # Back Button

    back_btn = ctk.CTkButton(orders_frame, text=" Back", image=back_icon, width=100, height=30,
                             fg_color="transparent", text_color="black", hover_color="#D59CFF",
                             font=("Arial", 16, "bold"), anchor="w", command=go_back)
    back_btn.place(x=20, y=20)

    # Logo
    logo_label = ctk.CTkLabel(orders_frame, text="", image=app_logo, fg_color="transparent")
    logo_label.place(x=620, y=20)

    ctk.CTkLabel(orders_frame, text="My Orders", font=("Arial", 28, "bold"), text_color="black").place(relx=0.5, y=80,
                                                                                                       anchor="center")

    # --- Orders List ---
    scroll_frame = ctk.CTkScrollableFrame(orders_frame, fg_color="white", width=600, height=400)
    scroll_frame.place(relx=0.5, y=350, anchor="center")

    # --- Fetch Data ---
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

            query = """
                    SELECT 
                           o.order_id, 
                           u.first_name, 
                           o.order_date, 
                           o.order_status,
                           o.total_amount
                    FROM Orders o 
                    JOIN users u ON o.customer_id = u.id
                    WHERE o.customer_email = %s
                    ORDER BY o.order_date DESC
                    """
            cursor.execute(query, (email,))
            orders = cursor.fetchall()

            if not orders:
                ctk.CTkLabel(scroll_frame, text="No orders placed yet.",
                             font=("Arial", 16), text_color="gray").pack(pady=50)
            else:
                # Headers
                header = ctk.CTkFrame(scroll_frame, fg_color="#F0F0F0")
                header.pack(fill="x", pady=5)
                ctk.CTkLabel(header, text="Order ID", width=130, font=("Arial", 12, "bold"), text_color="black",
                             anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Name", width=80, font=("Arial", 12, "bold"), text_color="black",
                             anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Date", width=130, font=("Arial", 12, "bold"), text_color="black",
                             anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Status", width=80, font=("Arial", 12, "bold"), text_color="black",
                             anchor="w").pack(side="left", padx=5)
                ctk.CTkLabel(header, text="Total", width=80, font=("Arial", 12, "bold"), text_color="black",
                             anchor="e").pack(side="left", padx=5)

                for order in orders:
                    row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                    row.pack(fill="x", pady=5)

                    # Order ID
                    ctk.CTkLabel(row, text=f"{order['order_id']}", width=130, text_color="black", anchor="w").pack(
                        side="left", padx=5)

                    # First Name (New)
                    ctk.CTkLabel(row, text=f"{order['first_name']}", width=80, text_color="black", anchor="w").pack(
                        side="left", padx=5)

                    # Date
                    ctk.CTkLabel(row, text=str(order['order_date']), width=130, text_color="black", anchor="w").pack(
                        side="left", padx=5)

                    # Status (Color Coded)
                    status_color = "green" if order['order_status'] == 'Delivered' else "#D97706"  # Orange for Processing
                    ctk.CTkLabel(row, text=order['order_status'], width=80, text_color=status_color,
                                 font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=5)

                    # Total
                    ctk.CTkLabel(row, text=f"${order['total_amount']:.2f}", width=80, text_color="black",
                                 font=("Arial", 12, "bold"), anchor="e").pack(side="left", padx=5)

                    # Separator line
                    ctk.CTkFrame(scroll_frame, height=1, fg_color="#E0E0E0").pack(fill="x")

        except Error as e:
            ctk.CTkLabel(scroll_frame, text=f"Could not fetch orders: {e}", text_color="red").pack(pady=20)
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close();
                conn.close()
    else:
        # messagebox.showwarning("Session Error", "No user logged in.")
        pass

    return orders_frame