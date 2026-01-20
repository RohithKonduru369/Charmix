import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import re
import bcrypt


def resize_image(size, image_url):
    # Load the original image
    original_image = Image.open(f'{image_url}')
    resized_image = original_image.resize((size[0], size[1]))
    tk_image = ImageTk.PhotoImage(resized_image)
    return tk_image


def change_password_ui(root):

    password_visible = ctk.BooleanVar(value=False)

    login_frame = ctk.CTkFrame(root, fg_color="#E0B0FF", width=700, height=600)
    login_frame.pack_propagate(False)
    login_frame.place(x=0, y=0)

    def on_save_changes_click(master, email_entry, pwd_entry, cnpwd_entry, login_frame):
        # 1. Get all values
        email = email_entry.get()
        new_password = pwd_entry.get()
        confirm_password = cnpwd_entry.get()

        # 2. Validation
        errors = []

        # Email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Email: Invalid format (must be user@domain.com).")

        # Password Match
        if new_password != confirm_password:
            errors.append("Passwords: Passwords do not match.")

        # Password Complexity
        if len(new_password) < 8:
            errors.append("Password: Must be at least 8 characters long.")
        if not re.search(r"[A-Z]", new_password):
            errors.append("Password: Must contain at least one capital letter.")
        if not re.search(r"[a-z]", new_password):
            errors.append("Password: Must contain at least one small letter.")
        if not re.search(r"[!@#$%^&*(),.?:{}|<>_]", new_password):
            errors.append("Password: Must contain at least one special character.")

        # 3. Show errors or proceed
        if errors:
            messagebox.showerror("Update Error", "\n".join(errors))
            return  # Stop the function

        # 4. No errors, proceed to database
        try:
            # Hash the new password
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(new_password.encode('utf-8'), salt)

            # Connect to DB
            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
            )
            cursor = conn.cursor()

            # Check if email *exists*
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "No user found with this email.")
                return

            # Email exists, so update the password
            query = "UPDATE users SET password = %s WHERE email = %s"
            cursor.execute(query, (hashed_pwd, email))
            conn.commit()

            messagebox.showinfo("Success", "Password updated! Please log in with your new password.")

            # Navigate back to login
            from login_screen import create_login_ui
            login_frame.place_forget()
            create_login_ui(master)

        except Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()


    user_logo = resize_image((180,180),"Images/icon.png")
    logo_label = ctk.CTkLabel(login_frame,text = "",image = user_logo,fg_color = "#F6CA51")
    logo_label.place(x = 350, y = 90, anchor="center")

    eye_open_image = resize_image((20, 20), r"Images\eye_open.png")
    eye_closed_image = resize_image((20, 20), r"Images\eye_closed.png")


    def navigate_to_login():
        from login_screen import create_login_ui
        login_frame.place_forget() 
        create_login_ui(root)

    def toggle_password_visibility():
        if password_visible.get():
            # Hide password
            pwd_entry.configure(show="*")
            cnpwd_entry.configure(show="*")
            toggle_pass_btn.configure(image=eye_closed_image)
            password_visible.set(False)
        else:
            # Show password
            pwd_entry.configure(show="")
            cnpwd_entry.configure(show="")
            toggle_pass_btn.configure(image=eye_open_image)
            password_visible.set(True)

    # login text label
    change_label = ctk.CTkLabel(login_frame, text="Change Password", text_color="#140101",
                           font=('inter', 28, 'bold'))
    change_label.place(x=240, y=180)


    # email_label
    email_label = ctk.CTkLabel(login_frame, text="Email", text_color='#140101', font=('inter', 18, "bold"))
    email_label.place(x=200, y=220)

    # email_widget
    email_entry = ctk.CTkEntry(login_frame, text_color='black', font=('inter', 12, "normal"), width=300, height=45,
                                    corner_radius= 20, border_width=2,border_color='black', fg_color="#FFFFFF",placeholder_text="Enter your email")
    email_entry.place(x=200, y=250)
    

    # password_label
    pwd_label = ctk.CTkLabel(login_frame, text="Password", text_color='#140101', font=('inter', 18, "bold"))
    pwd_label.place(x=200, y=300)

    # pswd_widget
    pwd_entry = ctk.CTkEntry(login_frame, text_color='black', font=('inter', 12, "normal"), width=300, height=45,
                                    corner_radius=20, border_width=2,border_color='black', fg_color="#FFFFFF",
                             placeholder_text="Enter your password", show="*")
    pwd_entry.place(x=200, y=330)
    


    #  label
    cnpwd_label = ctk.CTkLabel(login_frame, text="Confirm Password", text_color='#140101',font=('inter', 18, "bold"),
                               )
    cnpwd_label.place(x=200, y=380)

    cnpwd_entry = ctk.CTkEntry(login_frame, text_color='black', font=('inter', 12, "normal"), width=300, height=45,
                                    corner_radius=20, border_width=2,border_color='black', fg_color="#FFFFFF",
                                    placeholder_text='Confirm password', show="*")
    cnpwd_entry.place(x=200, y=410)
    

    toggle_pass_btn = ctk.CTkButton(pwd_entry, text="", image=eye_closed_image,
                                    width=20, height=20, fg_color="transparent",
                                    hover_color="#E0B0FF",
                                    command=toggle_password_visibility)
    toggle_pass_btn.place(x=260, y=10)  # Place next to password


    # Save Changes_button
    save_button = ctk.CTkButton(login_frame, text="Save Changes", text_color="#FFFFFF", width=125, height=40,
                                fg_color="#9370DB", border_width=3, border_color="black", corner_radius=25,
                                hover_color="#F6CA51", font=('inter', 15, "bold"),
                                command=lambda: on_save_changes_click(root, email_entry, pwd_entry, cnpwd_entry,
                                                                      login_frame))
    save_button.place(x=200, y=490)
    #back_button
    back_button = ctk.CTkButton(login_frame, text="Back", text_color="#FFFFFF", width=125, height=40,
                             fg_color="#9370DB", border_width=3, border_color="black", corner_radius=20,
                             hover_color="#F6CA51", font=('inter', 15, "bold"),command = navigate_to_login)
    back_button.place(x=375, y=490)

    return login_frame

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Group 4 change password Screen")
    root.geometry("700x600")
    root.resizable(False, False)

    change_password_ui(root)
    
    root.mainloop()
