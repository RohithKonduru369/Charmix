import customtkinter as ctk
from tkinter import messagebox
# --- FIXED: Ensure this import is present ---
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


def create_account_ui(master, previous_frame=None):
    """Creates the My Account screen."""

    account_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    account_frame.pack_propagate(False)
    account_frame.place(x=0, y=0)

    # --- Load Icons ---
    # Ensure you have 'back_icon.png' in your Images folder
    back_icon = resize_image((30, 30), r"Images\arrow_back.png")
    app_logo = resize_image((50, 50), r"Images\icon.png")

    # --- Navigation ---
    def go_back():
        # Destroy current frame
        account_frame.destroy()

        # 1. Restore the background frame (Home or Checkout)
        if previous_frame:
            previous_frame.place(x=0, y=0)

            # 2. Re-open the Menu on top of it
            from menu import create_menu_ui
            create_menu_ui(master, overlay_on_frame=previous_frame)
        else:
            # Fallback if opened directly
            from home_screen import create_home_ui
            create_home_ui(master)

    # Back Button (Icon + Text)
    back_btn = ctk.CTkButton(account_frame, text=" Back", image=back_icon, width=100, height=40,
                             fg_color="transparent", text_color="black", hover_color="#D59CFF",
                             font=("Arial", 16, "bold"), anchor="w", command=go_back)
    back_btn.place(x=20, y=20)

    # Logo (Top Right)
    logo_label = ctk.CTkLabel(account_frame, text="", image=app_logo, fg_color="transparent")
    logo_label.place(x=620, y=20)

    ctk.CTkLabel(account_frame, text="My Account", font=("Arial", 28, "bold"), text_color="black").place(relx=0.5, y=80,
                                                                                                         anchor="center")

    # --- Display Data ---
    info_frame = ctk.CTkFrame(account_frame, fg_color="white", width=500, height=300, corner_radius=15)
    info_frame.place(relx=0.5, y=300, anchor="center")

    # Labels
    ctk.CTkLabel(info_frame, text="First Name:", font=("Arial", 14, "bold"), text_color="gray").place(x=50, y=50)
    fname_label = ctk.CTkLabel(info_frame, text="Loading...", font=("Arial", 16), text_color="black")
    fname_label.place(x=50, y=80)

    ctk.CTkLabel(info_frame, text="Last Name:", font=("Arial", 14, "bold"), text_color="gray").place(x=50, y=130)
    lname_label = ctk.CTkLabel(info_frame, text="Loading...", font=("Arial", 16), text_color="black")
    lname_label.place(x=50, y=160)

    ctk.CTkLabel(info_frame, text="Email ID:", font=("Arial", 14, "bold"), text_color="gray").place(x=50, y=210)
    email_label = ctk.CTkLabel(info_frame, text="Loading...", font=("Arial", 16), text_color="black")
    email_label.place(x=50, y=240)

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
            query = "SELECT first_name, last_name, email FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()

            if user_data:
                fname_label.configure(text=user_data["first_name"])
                lname_label.configure(text=user_data["last_name"])
                email_label.configure(text=user_data["email"])
            else:
                messagebox.showerror("Error", "User data not found.")

        except Error as e:
            messagebox.showerror("Database Error", f"{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close();
                conn.close()
    else:
        # For testing purposes, don't show an error if just running the file directly
        # messagebox.showwarning("Session Error", "No user logged in.")
        pass

    return account_frame


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Account Page")
    root.geometry("700x600")
    create_account_ui(root)
    root.mainloop()