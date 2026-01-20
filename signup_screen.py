import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox
import re
import mysql.connector
from mysql.connector import Error
import bcrypt

def create_signup_ui(master):
    password_visible = ctk.BooleanVar(value=False)

    def resize_image(size, image_url):
    # Load the original image
        original_image = Image.open(f'{image_url}')
        resized_image = original_image.resize((size[0], size[1]))
        tk_image = ImageTk.PhotoImage(resized_image)
        return tk_image

    eye_open_image = resize_image((20, 20), r"Images\eye_open.png")
    eye_closed_image = resize_image((20, 20), r"Images\eye_closed.png")

    back_image = resize_image((20, 20), r"Images\arrow_back.png")

    def navigate_to_login():
       from login_screen import create_login_ui
       signup_frame.place_forget() 
       create_login_ui(master)

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


    def on_register_click():
        fname= fname_entry.get()
        lname= lname_entry.get()
        email=email_entry.get()
        pwd=pwd_entry.get()
        cnpwd=cnpwd_entry.get()

        errors = []
        #First Name
        if not (len(fname) >= 3 and fname[0].isupper()):
            errors.append("First Name: Must be 3+ chars and start with a capital.")

            # Last Name
        if not (len(lname) >= 2 and lname[0].isupper()):
            errors.append("Last Name: Must be 2+ chars and start with a capital.")

            # Email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Email: Invalid format (must be user@domain.com).")

            # Password Match
        if pwd != cnpwd:
            errors.append("Passwords: Passwords do not match.")

            # Password Complexity
        if len(pwd) < 8:
            errors.append("Password: Must be at least 8 characters long.")
        if not re.search(r"[A-Z]", pwd):
            errors.append("Password: Must contain at least one capital letter.")
        if not re.search(r"[a-z]", pwd):
            errors.append("Password: Must contain at least one small letter.")
        if not re.search(r"[!@#$%^&*(),.?:{}|<>_]", pwd):
            errors.append("Password: Must contain at least one special character.")

            # 3. Show errors or proceed
        if errors:
            messagebox.showerror("Registration Error", "\n".join(errors))
            return
            # 4. No errors, procceding to database
        try:
            salt=bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), salt)

        #connect to DB
            conn = mysql.connector.connect(
                host="141.209.241.57",
                user="kondu2r",
                password="mypass",
                database="BIS698Fall25_GRP4"
                )
            cursor = conn.cursor()

            cursor.execute("SELECT email FROM users WhERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "The Email is already registered.")

            query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (fname, lname, email, hashed_pwd))
            new_user_id = cursor.lastrowid

            update_sql = """
                          UPDATE users
                          SET customer_code = CONCAT(
                                  UPPER(LEFT (last_name,2)),
                                  UPPER(LEFT(first_name,2)),
                              LPAD(id, 4, '0')
                          )
                              WHERE id = %s
                         """
            cursor.execute(update_sql, (new_user_id,))

            conn.commit()

            messagebox.showinfo("Success", "You are registered, Login back again.")
            navigate_to_login()
        except Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def on_clear_click():
            # Clear all entry fields
            fname_entry.delete(0, 'end')
            lname_entry.delete(0, 'end')
            email_entry.delete(0, 'end')
            pwd_entry.delete(0, 'end')
            cnpwd_entry.delete(0, 'end')

            # Re-insert placeholders
            fname_entry.insert(0, "Full Name")
            lname_entry.insert(0, "Last Name")
            email_entry.insert(0, "Email")
            pwd_entry.insert(0, "Password")
            cnpwd_entry.insert(0, "Confirm Password")



    signup_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=700, height=600)
    signup_frame.pack_propagate(False)
    signup_frame.place(x=0, y=0)

    user_logo = resize_image((180, 180), r"Images\icon.png")
    signup_frame.user_logo_ref = user_logo
    logo_label = ctk.CTkLabel(signup_frame,text = "",image = user_logo,fg_color = "#F6CA51")
    logo_label.place(relx=0.5,y = 85, anchor=ctk.CENTER)


    # login text label
    signup_label = ctk.CTkLabel(signup_frame, text="Create your Charmix account!!", text_color="#140101",
                           font=('inter', 20, 'bold'))
    signup_label.place(x=215, y=165)


   # fname_widget
    fname_entry = ctk.CTkEntry(signup_frame, text_color="black",placeholder_text="First Name", font=('inter', 12, "normal"), width=300, height=40,
                                border_width=2,border_color='black', fg_color="#FFFFFF")
    fname_entry.place(x=200, y=205)


    # lname_widget
    lname_entry = ctk.CTkEntry(signup_frame, text_color='black',placeholder_text="Last name", font=('inter', 12, "normal"), width=300, height=40,
                                    border_width=2,border_color='black', fg_color="#FFFFFF")
    lname_entry.place(x=200, y=255)


    # email_widget
    email_entry = ctk.CTkEntry(signup_frame, text_color='black',placeholder_text="Enter your email", font=('inter', 12, "normal"), width=300, height=40,
                                    border_width=2,border_color='black', fg_color="#FFFFFF")
    email_entry.place(x=200, y=305)


    # email_widget
    pwd_entry = ctk.CTkEntry(signup_frame, text_color='black',placeholder_text="Password", font=('inter', 12, "normal"), width=300, height=40,
                                    border_width=2,border_color='black', fg_color="#FFFFFF", show="*")
    pwd_entry.place(x=200, y=355)


    cnpwd_entry = ctk.CTkEntry(signup_frame, text_color='black', font=('inter', 12, "normal"), width=300, height=40,
                                    border_width=2,border_color='black' ,fg_color="#FFFFFF",placeholder_text="Confirm password", show="*")
    cnpwd_entry.place(x=200, y=405)


    toggle_pass_btn = ctk.CTkButton(pwd_entry, text="", image=eye_closed_image,
                                width=20, height=20, fg_color="transparent",
                                hover_color="#E0B0FF",
                                command=toggle_password_visibility)
    toggle_pass_btn.place(x=265, y=8)


    # login_button
    register_button = ctk.CTkButton(signup_frame, text="Register", text_color="#FFFFFF", width=125, height=40,
                             fg_color="#9370DB",border_width=3, border_color="black", corner_radius=20,
                                hover_color="#F6CA51", font=('inter', 18, "bold"), command=on_register_click)
    register_button.place(x=200, y=480)

    #Clear_button
    clear_button = ctk.CTkButton(signup_frame, text="Clear", text_color="#FFFFFF", width=125, height=40,
                             fg_color="#9370DB", border_width=3, border_color="black", corner_radius=20,
                             hover_color="#F6CA51", font=('inter', 18, "bold"), command=on_clear_click)
    clear_button.place(x=375, y=480)

    master.back_image_ref = back_image

    back_button = ctk.CTkButton(signup_frame, text="Back", text_color="#000000", image=back_image, width =25, height = 25, fg_color="transparent",
                            hover_color = "#F6CA51", compound="left",command = navigate_to_login)
    back_button.place(x=25, y=25)

    return signup_frame

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Group 4 User Signup Screen")
    root.geometry("700x600")
    root.resizable(False, False)
    create_signup_ui(root)

    root.mainloop()
