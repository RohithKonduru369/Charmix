import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

root = ctk.CTk()
root.title("Group 4 User Registration Screen")
root.geometry("700x600")
root.resizable(False, False)


def resize_image(size, image_url):
    # Load the original image
    original_image = Image.open(f'{image_url}')
    resized_image = original_image.resize((size[0], size[1]))
    tk_image = ImageTk.PhotoImage(resized_image)
    return tk_image
def navigate_to_login():
    from login_screen import create_login_ui
    login_frame.place_forget() 
    create_login_ui(root)

login_frame = ctk.CTkFrame(root, fg_color="#E0B0FF", width=700, height=600)
login_frame.pack_propagate(False)
login_frame.place(x=0, y=0)

user_logo = resize_image((180,180),"Images\icon.png")
logo_label = ctk.CTkLabel(login_frame,text = "",image = user_logo,fg_color = "#F6CA51")
logo_label.place(x = 350, y = 90, anchor="center")


# login text label
main_label = ctk.CTkLabel(login_frame, text="Your personalized beauty \n journey begins here", text_color="#140101",
                           font=('inter', 22, 'bold'))
main_label.place(x=220, y=180)

#main Title
main_label= ctk.CTkLabel(login_frame, text="Discover your glow", text_color='#140101',
                                    font=('inter', 21))
main_label.place(x=260, y=260)

# started_button
start_button = ctk.CTkButton(login_frame, text="Get Started", text_color="#000000", width=250, height=40,
                             fg_color="#9370DB",border_width=3, border_color="black", corner_radius=25,command = navigate_to_login,
                                hover_color="#F6CA51", font=('inter', 19, "bold"))
start_button.place(x=230, y=350)

# Custom Box
custom1_frame = ctk.CTkFrame(login_frame, fg_color="#9370DB", border_width=2.5, border_color="white",
                             width=150, height=100)
custom1_frame.pack_propagate(False)
custom1_frame.place(x=60, y=440)

# Custom Box
custom2_frame = ctk.CTkFrame(login_frame, fg_color="#9370DB", border_width=2.5, border_color="white",
                             width=150, height=100)
custom2_frame.pack_propagate(False)
custom2_frame.place(x=285, y=440)

# Custom Box
custom3_frame = ctk.CTkFrame(login_frame, fg_color="#9370DB", border_width=2.5, border_color="white",
                             width=150, height=100)
custom3_frame.pack_propagate(False)
custom3_frame.place(x=500, y=440)

#Box1
text1_label= ctk.CTkLabel(custom1_frame, text="Custom Routines", text_color='#140101',
                                    font=('inter', 12, "bold"))
text1_label.place(x=25, y=55)

logo1 = resize_image((35,35),"Images\\routine.png")
logo_label = ctk.CTkLabel(custom1_frame,text = "",image = logo1,fg_color = "#9370DB")
logo_label.place(x=60, y=15)

#Box2
text2_label= ctk.CTkLabel(custom2_frame, text="Curated Products", text_color='#140101',
                                    font=('inter', 12, "bold"))
text2_label.place(x=25, y=55)

logo_label = ctk.CTkLabel(custom2_frame,text = "",image = logo1,fg_color = "#9370DB")
logo_label.place(x=60, y=15)

#Box3
text3_label= ctk.CTkLabel(custom3_frame, text="Trending Products", text_color='#140101',
                                    font=('inter', 12, "bold"))
text3_label.place(x=25, y=55)

logo_label = ctk.CTkLabel(custom3_frame,text = "",image = logo1,fg_color = "#9370DB")
logo_label.place(x=60, y=15)


root.mainloop()
