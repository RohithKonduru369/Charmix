import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import bcrypt
import user_session
from ad_test import create_admin_dashboard_ui
from home_screen import create_home_ui
from signup_screen import create_signup_ui

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")


def resize_image(size, image_url):
    # Load the original image
    original_image = Image.open(f'{image_url}')
    resized_image = original_image.resize((size[0], size[1]))
    tk_image = ImageTk.PhotoImage(resized_image)
    return tk_image

def create_login_ui(master):

    password_visible = ctk.BooleanVar(value=False)
    login_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    login_frame.pack_propagate(False)
    login_frame.place(x=0, y=0)
    eye_open_image = resize_image((20, 20), r"Images\eye_open.png")
    eye_closed_image = resize_image((20, 20), r"Images\eye_closed.png")

    def navigate_to_signup(event = None):
        login_frame.place_forget()
        create_signup_ui(master)

    def navigate_to_forgot(event = None):
        try:
            from change import change_password_ui
            login_frame.place_forget()
            change_password_ui(master)
        except ImportError:
            messagebox.showerror("Error", "Could not find 'change.py' file.")

    def toggle_password_visibility():
        if password_visible.get():
            # Hide password
            pwd_entry.configure(show="*")
            toggle_pass_btn.configure(image=eye_closed_image)
            password_visible.set(False)
        else:
            # Show password
            pwd_entry.configure(show="")
            toggle_pass_btn.configure(image=eye_open_image)
            password_visible.set(True)

    def login_user():
        email = email_entry.get()
        password = pwd_entry.get()

        # Simple validation
        if email == "Enter your email" or password == "Password" or not email or not password:
            messagebox.showerror("Login Error", "Please fill in all fields.")
            return

        try:

            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
                 
            )

            if conn.is_connected():
                cursor = conn.cursor()

                # --- SQL QUERY ---
                # This query checks for a matching email and password.
                # WARNING: Storing passwords in plain text is a major security risk.
                # For a real app, please use a hashing library like 'bcrypt'.
                query = "SELECT password FROM users WHERE email like %s"
                query_1 = "SELECT first_name from users where email like %s"

                # Execute the query securely
                cursor.execute(query, (email+"%",))

                result = cursor.fetchone()  # Get one matching row

                cursor.execute(query_1, (email+"%",))
                result_1 = cursor.fetchone()
            

                if result:
                    # 2. User was found, get the hashed password from DB
                    hashed_pwd_from_db = result[0].encode('utf-8')

                    # 3. Check if the entered password matches the hashed one
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_pwd_from_db):
                        user_session.set_current_user(email)
                        # Login successful
                        if email == "admin123@mail.com":
                            from ad_test import create_admin_dashboard_ui
                            messagebox.showinfo("Login Success", "Welcome, Admin!")
                            login_frame.place_forget()
                            create_admin_dashboard_ui(master)
                        else:
                            messagebox.showinfo("Login Success", f"Welcome back, {result_1[0]}!")
                            login_frame.place_forget()
                            create_home_ui(master)

                    else:
                        messagebox.showerror("Login Error", "Invalid email or password.")
                else:
                    # 4. No user was found with that email
                    messagebox.showerror("Login Error", "No user found with that email.")

        except Error as e:
                # Handle database connection errors
                messagebox.showerror("Database Error", f"Error connecting to database: {e}")

        finally:
            # Always close the connection
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()


    # icon_frame
    icon_frame = ctk.CTkFrame(login_frame, fg_color="transparent", width=180, height=180, corner_radius=120)
    icon_frame.place(relx=0.5, y=5, anchor=ctk.N)
    
    user_logo = resize_image((180, 180),"Images\icon.png")
    logo_label = ctk.CTkLabel(icon_frame, text="", image=user_logo, fg_color="transparent")
    logo_label.image = user_logo
    logo_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    # login text label (Centered)
    login_label = ctk.CTkLabel(login_frame, text="Welcome Back", text_color="#140101",
                               font=('inter', 24, 'bold'))
    login_label.place(relx=0.5, y=190, anchor=ctk.CENTER) 

    login_text = ctk.CTkLabel(login_frame, text="Login into your personalized beauty journey", text_color="#140101",
                               font=('inter', 13, 'normal'))
    login_text.place(x=230,y=205)

    # email_label and email_entry
    # email_label
    email_label = ctk.CTkLabel(login_frame, text="Email", text_color='#140101', font=('inter', 18, "bold"))
    email_label.place(x=200, y=240)

    # email_widget
    email_entry = ctk.CTkEntry(login_frame, text_color='black', font=('inter', 12, "normal"), width=300, height=45,
                                    corner_radius= 20, border_width=2,border_color="black",
                                      fg_color="#FFFFFF",placeholder_text='Enter your email')
    email_entry.place(x=200, y=270)

    # password_label
    pwd_label = ctk.CTkLabel(login_frame, text="Password", text_color='#140101', font=('inter', 18, "bold"))
    pwd_label.place(x=200, y=340)

    # pswd_widget
    pwd_entry = ctk.CTkEntry(login_frame, text_color='black',placeholder_text='Enter your password', font=('inter', 12, "normal"), width=300, height=45,
                                    corner_radius=20, border_width=2, fg_color="#FFFFFF",border_color='black', show="*")
    pwd_entry.place(x=200, y=370)

    toggle_pass_btn = ctk.CTkButton(pwd_entry, text="", image=eye_closed_image,
                                    width=20, height=20, fg_color="transparent",
                                    hover_color="#E0B0FF", command=toggle_password_visibility)
    toggle_pass_btn.place(x=260, y=12)

    # remember_me label
    remember_label = ctk.CTkLabel(login_frame, text="Remember me", text_color='#140101', font=('inter', 12, "normal"))
    remember_label.place(x=200, y=425)

    
    remember_var = ctk.StringVar(value="off")

    remember_me_checkbox = ctk.CTkCheckBox(
    login_frame, 
    text="", 
    text_color='#140101', 
    font=('inter', 14),
    variable=remember_var, 
    onvalue="on", 
    offvalue="off",
    checkbox_height=20, 
    checkbox_width=20,
    fg_color="#9370DB",)

    remember_me_checkbox.place(x=290, y=428)

    # forgot_password label
    forgot_label = ctk.CTkLabel(login_frame, text="Forgot Password", text_color='#140101', 
                                font=('inter', 12, "normal"),cursor = "hand2")
    forgot_label.place(x=390, y=425)
    forgot_label.bind("<Button-1>", navigate_to_forgot)


    # login_button
    register_button = ctk.CTkButton(login_frame, text="Login", text_color="#FFFFFF", width=150, height=40,
                                     fg_color="#9370DB",border_width=3, border_color="black", corner_radius=25,
                                     hover_color="#F6CA51", font=('inter', 18, "bold"),command = login_user)

    register_button.place(relx=0.5, y=490, anchor=ctk.CENTER)


    # sign_up label
    signup_label = ctk.CTkLabel(login_frame, text="Don't have your account?", 
                                text_color='#140101', font=('inter', 15, "normal"))
    signup_label.place(x=200, y=520)

    # sign_up label
    signup1_label = ctk.CTkLabel(
    login_frame,
    text="Sign up",
    text_color="#010414",
    font=('Inter', 15, "bold"),
    cursor="hand2") 
    signup1_label.place(x=380, y=520)
    # Bind left mouse click to the functio
    signup1_label.bind("<Button-1>", navigate_to_signup)

    return login_frame


if __name__ == "__main__":
    
    root = ctk.CTk()
    root.title("Group 4 User login Screen")
    root.geometry("700x600")
    root.resizable(False, False)
    create_login_ui(root)
    
    root.mainloop()