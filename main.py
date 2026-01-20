import customtkinter as ctk
from landing import create_login_ui

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Skincare App")
    root.geometry("700x600")
    root.resizable(False, False)

    # Start by showing the login screen
    create_login_ui(root)

    root.mainloop()