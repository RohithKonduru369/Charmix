import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

from account_page import create_account_ui
from orders_page import create_orders_page

# --- Image Resizer (Simpler Version) ---
def resize_image(size, image_url):
    original_image = Image.open(f'{image_url}')
    resized_image = original_image.resize(size)
    return ImageTk.PhotoImage(resized_image)

def create_menu_ui(master, overlay_on_frame=None):
    menu_frame = ctk.CTkFrame(master, fg_color="#E0B0FF", width=350, height=600)
    menu_frame.pack_propagate(False)
    menu_frame.place(x=0, y=0)

    menu_icon = resize_image((40, 40), r"Images\menu.png")

    def close_menu():
        menu_frame.destroy()

    def go_to_my_account():
        menu_frame.destroy()
        if overlay_on_frame:
            overlay_on_frame.place_forget()
            # Pass the background frame so we can return to it later
        create_account_ui(master, previous_frame=overlay_on_frame)

    def go_to_orders():
        menu_frame.destroy()
        if overlay_on_frame:
            overlay_on_frame.place_forget()
        create_orders_page(master, previous_frame=overlay_on_frame)

    def perform_logout():
        from login_screen import create_login_ui
        menu_frame.destroy()
        if overlay_on_frame:
            overlay_on_frame.place_forget()
        create_login_ui(master)

    close_btn = ctk.CTkButton(menu_frame, text="", image=menu_icon, width=40, height=40,
                              fg_color="transparent", hover_color="#D59CFF",
                              bg_color="#E0B0FF", command=close_menu)
    close_btn.place(x=20, y=30)

    title_label = ctk.CTkLabel(menu_frame, text="Menu",
                               font=('inter', 28, 'bold'), text_color="#140101")
    title_label.place(relx=0.5, y=100, anchor=ctk.CENTER)

    # Buttons
    account_button = ctk.CTkButton(menu_frame, text="My Account",
                                   font=('inter', 18, "bold"),
                                   width=250, height=50,
                                   fg_color="#9370DB", border_width=3, border_color="black",
                                   hover_color="#F6CA51", corner_radius=25,
                                   command=go_to_my_account)
    account_button.place(relx=0.5, y=200, anchor=ctk.CENTER)

    orders_button = ctk.CTkButton(menu_frame, text="My Orders",
                                  font=('inter', 18, "bold"),
                                  width=250, height=50,
                                  fg_color="#9370DB", border_width=3, border_color="black",
                                  hover_color="#F6CA51", corner_radius=25,
                                  command=go_to_orders)
    orders_button.place(relx=0.5, y=270, anchor=ctk.CENTER)

    logout_button = ctk.CTkButton(menu_frame, text="Log Out",
                                  font=('inter', 18, "bold"),
                                  width=250, height=50,
                                  fg_color="transparent", border_width=3, border_color="#9370DB",
                                  text_color="#9370DB", hover_color="#F0F0F0", corner_radius=25,
                                  command=perform_logout)
    logout_button.place(relx=0.5, y=530, anchor=ctk.CENTER)

    return menu_frame


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Menu Page")
    root.geometry("700x600")
    create_menu_ui(root)
    root.mainloop()