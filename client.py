from tkinter import messagebox
from datetime import datetime
from tkinter import ttk
import tkinter as tk
import socket
import random
import time
import ast
import sys

# Constants
HOST = 'localhost'
PORT = 5050
MAX_FRIENDS = 6
weather_bot = "Weather Bot"
hundreds_game = "Numbers Game"
bots = [weather_bot, hundreds_game]
FONT = "Helvetica"
game_result = ""
screen_on = 0

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

class AppClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.username = ''
        self.title("Tom's Texts")
        self.geometry("450x550")
        #self.iconbitmap('app.ico')
        #self.configure(bg='#2A2524')
        self.resizable(False, False)
        self.weather_report = ''
        self.friend_name = ''
        self.last_message = ''
        self.sock = None
        self.initialize_login_frame()
        self.messages_text = None
        self.same_message = 'nothing'

    def send_command(self, command):
        try:
            self.sock.send(command.encode())
            return self.sock.recv(1024).decode()
        except:
            messagebox.showerror("Connection Error", "Lost connection with the server")
            self.on_closing()
        
    def send_long_command(self, command):
        try:
            self.sock.send(command.encode())
            return self.sock.recv(10240).decode()
        except:
            messagebox.showerror("Connection Error", "Lost connection with the server")
            self.on_closing()

    def validate_entry(self, entry):
        if '|' in entry:
            messagebox.showerror("Fail", "Contains forbidden character '|'")
            return False
        if '~' in entry:
            messagebox.showerror("Fail", "Contains forbidden character '~'")
            return False
        if len(entry) > 10000:
            messagebox.showerror("Fail", "Exceeds max length of 10000 characters")
            return False
        if entry == ":Unread Messages":
            messagebox.showerror("Fail", "Invalid command")
            return False
        return True

    def initialize_login_frame(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(padx=20, pady=200)
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Label(self.login_frame, text="").grid(row=2, column=0)
        tk.Button(self.login_frame, text="Login", padx=20, command=self.login).grid(row=3, column=1, sticky='w', ipadx=10)

        tk.Button(self.login_frame, text="Sign up", padx=15, command=self.show_signup_frame).grid(row=4, column=1, sticky='w', ipadx=10)

        self.username_entry.bind('<Return>', lambda event=None: self.login())
        self.password_entry.bind('<Return>', lambda event=None: self.login())

    def initialize_signup_frame(self):
        self.signup_frame = tk.Frame(self)
        self.signup_frame.pack(padx=20, pady=190)
        tk.Label(self.signup_frame, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.signup_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.signup_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.signup_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Label(self.signup_frame, text="Confirm:").grid(row=2, column=0)
        self.confirm_password_entry = tk.Entry(self.signup_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1)

        tk.Label(self.signup_frame, text="").grid(row=3, column=0)
        tk.Button(self.signup_frame, text="Sign up", padx=15, command=self.signup).grid(row=4, column=1, sticky='w', ipadx=10)
        tk.Label(self.signup_frame, text="").grid(row=4, column=0)
        tk.Button(self.signup_frame, text="Log in", padx=20, command=self.show_login_frame).grid(row=5, column=1, sticky='w', ipadx=10)

        self.username_entry.bind('<Return>', lambda event=None: self.signup())
        self.password_entry.bind('<Return>', lambda event=None: self.signup())
        self.confirm_password_entry.bind('<Return>', lambda event=None: self.signup())

    def create_friend_button(self, master, text, command, notification=False, user_online=False):
        frame_bg = "#f0f0f0"

        frame = tk.Frame(master, bg=frame_bg)
        frame.pack(pady=2, fill='x', expand=False)

        button_font = (FONT, 15)

        button = tk.Button(frame, text=text, command=command, width=20, anchor="w", relief="flat", height=2, font=button_font)
        button.pack(side="left", fill="both", expand=True)

        # Calculate placement for dots
        green_dot_x = 0.85
        red_dot_x = green_dot_x - 0.1

        if notification:
            canvas_red = tk.Canvas(frame, width=20, height=20, bg=frame_bg, highlightthickness=0)
            canvas_red.place(relx=red_dot_x, rely=0.5, anchor="center")
            canvas_red.create_oval(5, 5, 18, 18, fill="red")

        if user_online:
            canvas_green = tk.Canvas(frame, width=20, height=20, bg=frame_bg, highlightthickness=0)
            canvas_green.place(relx=green_dot_x, rely=0.5, anchor="center")
            canvas_green.create_oval(5, 5, 18, 18, fill="green")

        return frame

    def display_friends_buttons(self, friends_list):
        # Clear current friend buttons
        for widget in self.friends_buttons_frame.winfo_children():
            widget.destroy()

        # Add a composite widget for each friend
        for friend in friends_list:
            if friend == "" or friend in bots:
                self.create_friend_button(self.friends_buttons_frame, friend, lambda f=friend: self.open_chat(f))
            else:
                response = self.send_command(f"CHECK_FOR_NOTIFICATION|{self.username}|{friend}")
                is_user_online = self.send_command(f"IS_USER_ONLINE|{friend}") == 'Yes'
                if response == "NEW_MESSAGE":
                    self.create_friend_button(self.friends_buttons_frame, friend, lambda f=friend: self.open_chat(f), notification=True, user_online=is_user_online)
                else:
                    self.create_friend_button(self.friends_buttons_frame, friend, lambda f=friend: self.open_chat(f), user_online=is_user_online)

    def initialize_friends_frame(self):
        # Clear previous frame contents
        for widget in self.winfo_children():
            widget.destroy()

        self.friends_frame = tk.Frame(self)
        self.friends_frame.pack(padx=10, pady=20)

        # Entry to add a new friend
        self.friendname_entry = tk.Entry(self.friends_frame)
        self.friendname_entry.grid(row=0, column=0, pady=(15, 5), ipady=0)

        #addfriend_button = tk.Button(self.friends_frame, text="Add Friend", command=self.add_friend, font=(FONT,14))
        addfriend_button = tk.Button(self.friends_frame, text="Add Friend", command=self.add_friend, font=(FONT,14), bg="#F0F0F0", fg="black")
        addfriend_button.grid(row=0, column=1, pady=(12, 5), sticky="w", ipady=0)

        deletefriend_button = tk.Button(self.friends_frame, text="Delete", command=self.delete_friend, font=(FONT,14))
        deletefriend_button.grid(row=0, column=2, pady=(12, 5), sticky="w", ipady=0)

        # Label for "Chats"
        chats_label = tk.Label(self.friends_frame, text="Friends List", font=(FONT, 15))
        chats_label.grid(row=1, column=0, columnspan=3, pady=(30,0))  # Span across all columns

        # A separate container for friend buttons
        self.friends_buttons_frame = tk.Frame(self.friends_frame)
        self.friends_buttons_frame.grid(row=2, column=0, columnspan=3, pady=(5, 0))

        update_button = tk.Button(self.friends_frame, text="Update", command=self.update_friends_list, font=(FONT,14))
        update_button.grid(row=20, column=1, pady=(37, 40), sticky='e', ipady=0)

        logout_button = tk.Button(self.friends_frame, text="Logout", command=self.logout, font=(FONT,14))
        logout_button.grid(row=20, column=2, pady=(0, 3), sticky='w', ipady=0)

        block_button = "Block Friend Requests" if self.send_command(f"FRIEND_REQUESTS|{self.username}") == "on" else "Unblock Friend Requests"
        block_friend_request_button = tk.Button(self.friends_frame, text=block_button, command=self.change_friend_requests, width=20, font=(FONT,14))
        block_friend_request_button.grid(row=20, column=0, pady=(0, 3), sticky='w', ipady=0)

        self.friendname_entry.bind('<Return>', lambda event=None: self.add_friend())

        self.friendname_entry.delete(0, tk.END)
        self.update_friends_list()

    def change_friend_requests(self):
        response = self.send_command(f"CHANGE_FRIEND_REQUESTS|{self.username}")
        if response != "Friend requests blocked" and response != "Friend requests unblocked":
            messagebox.showerror("Fail", response)
        self.initialize_friends_frame()

    def update_chat(self):
        """Fetches the latest messages and schedules the next update."""
        if hasattr(self, 'current_friend'):
            self.populate_messages(self.current_friend)  # Refresh messages
            self.after(100, self.update_chat)  # Schedule the next update after 0.1 second

    def update_friends_list(self):
        response = self.send_command(f"SHOWFRIENDS|{self.username}")
        if response == "No friends":
            response = ""
        response = response.split('\n')
        for i in range(len(response), MAX_FRIENDS):
            response.append("")
        self.display_friends_buttons(response)

    def open_chat(self, friend_name):
        self.friend_name = friend_name
        if friend_name == "":
            return
        self.friends_frame.pack_forget()

        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        tk.Label(self.chat_frame, text=f"Chatting with {friend_name}", font=(FONT, 15)).pack()

        # Message display area
        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, wrap=tk.WORD, font=(FONT, 15))
        self.messages_text.pack(padx=5, pady=(5, 20), fill=tk.BOTH, expand=True)

        # Message entry field
        self.message_entry = tk.Entry(self.chat_frame)
        self.message_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Bind the Enter key to the send_message function
        self.message_entry.bind('<Return>', lambda event=None: self.send_message(friend_name))

        # Buttons frame to hold Send and Back buttons
        buttons_frame = tk.Frame(self.chat_frame)
        buttons_frame.pack(fill=tk.X, pady=(0,0))

        # Send button
        send_button = tk.Button(buttons_frame, text="Send", command=lambda: self.send_message(friend_name), font=(FONT,15))
        send_button.pack(side=tk.LEFT, padx=(0, 0))

        # Back to friends list button
        back_button = tk.Button(buttons_frame, text="Back", command=self.back_to_friends, font=(FONT,15))
        back_button.pack(side=tk.LEFT, padx=(0, 0))

        # Initialize chat-specific variables
        self.current_friend = friend_name  # Keep track of the current chat friend
        
        # Populate with recent messages
        self.populate_messages(friend_name, True)

        if friend_name in bots:
            return

        # Start updating chat
        self.update_chat()  # Initial call to start the update loop
        response = self.send_command(f"READ_MESSAGES|{self.username}|{self.friend_name}")

    def populate_messages(self, friend_name, force_scroll = False):
        self.messages_text.tag_configure('green_text', foreground='#00CC00', font=(FONT, 16))
        self.messages_text.tag_configure('blue_text', foreground='#3399FF', font=(FONT, 16))
        self.messages_text.tag_configure('system_text', foreground='#DC143C', font=(FONT,15))
        self.messages_text.tag_configure('chat_font', font=(FONT, 14), foreground='#E1D9D1')
        self.messages_text.tag_configure('time_font', font=(FONT, 11), foreground='#8A2BE2')

        if force_scroll != True and self.messages_text.yview()[1] != 1.0:
            return

        # Fetch messages from the server
        unread_message_line = None
        messages = self.send_long_command(f"GETCHAT|{self.username}|{friend_name}|{self.last_message}")
        time_padding = ' ' * 113
        if messages == "NO_MESSAGES":
            self.messages_text.config(state='normal')
            self.messages_text.delete(1.0, tk.END)  # Clear previous messages
            if friend_name == weather_bot:
                # Inserting new instructions and information into the messages_text widget
                self.messages_text.insert(tk.END, "Look up the up to date weather in any city\n", "chat_font")
                self.messages_text.insert(tk.END, "Command to use: option-city-state\n\n", "chat_font")
                self.messages_text.insert(tk.END, "Option choices: \n", "chat_font")
                self.messages_text.insert(tk.END, "1 - Brief Weather Report\n", "chat_font")
                self.messages_text.insert(tk.END, "2 - Detailed Weather Report\n", "chat_font")
                self.messages_text.insert(tk.END, "3 - Brief Weather Report with some Jokes\n\n", "chat_font")
                self.messages_text.insert(tk.END, "Example input: 1-Portland-Oregon\n", "chat_font")
                self.messages_text.config(state='disabled')
            elif friend_name == hundreds_game:
                self.messages_text.insert(tk.END, "Welcome to the Hundreds Game!\n\n", "chat_font")
                self.messages_text.insert(tk.END, "To start enter a number for the rows and columns.\n", "chat_font")
                self.messages_text.insert(tk.END, "Example input: 5 (min: 2, max: 10)\n", "chat_font") 
                self.messages_text.insert(tk.END, "The goal is to find the numbers from 1 to 25 in order.\n\n", "chat_font")
                self.messages_text.insert(tk.END, "Click on the numbers to find them.\n", "chat_font")
                self.messages_text.insert(tk.END, "Good luck!\n", "chat_font")
                self.messages_text.config(state='disabled')
            else:
                self.messages_text.insert(tk.END, f"Start chatting with {friend_name}.\n\n", 'chat_font')
                self.messages_text.config(state='disabled')
        elif messages != "NO_NEW_MESSAGES":
            messages_list = messages.split('|')
            self.messages_text.config(state='normal')
            #self.messages_text.delete(1.0, tk.END)  # Clear previous messages
            prev_msg_sign = self.last_message[0] if self.last_message != '' else ' '
            for msg in messages_list:
                if msg != ":Unread Messages":
                    self.last_message = msg
                if msg.startswith('+'):
                    if prev_msg_sign == '-' or prev_msg_sign == ' ':
                        # new snippet
                        self.messages_text.insert(tk.END, self.username, 'green_text')
                        self.messages_text.insert(tk.END, "\n" + msg[1:len(msg)-9] + '\n', 'chat_font')
                    else:
                        # send message in same snippet
                        self.messages_text.insert(tk.END, msg[1:len(msg)-9] + "\n", 'chat_font')
                    self.messages_text.insert(tk.END, time_padding + msg[len(msg)-9:] + "\n", 'time_font')
                    prev_msg_sign = "+"

                elif msg.startswith('-'):
                    if prev_msg_sign == '+' or prev_msg_sign == ' ':
                        # new snippet
                        self.messages_text.insert(tk.END, friend_name, 'blue_text')
                        self.messages_text.insert(tk.END, "\n" + msg[1:len(msg)-9] + '\n', 'chat_font')
                    else:
                        # send message in same snippet
                        self.messages_text.insert(tk.END, msg[1:len(msg)-9] + "\n", 'chat_font')
                    self.messages_text.insert(tk.END, time_padding + msg[len(msg)-9:] + "\n", 'time_font')
                    prev_msg_sign = "-"
                    self.same_message = msg
                else: # system messsage
                    # do not display unread messages if nothing was sent
                    if messages_list[len(messages_list)-1] != msg:
                        unread_message_line = self.messages_text.index('end-1c').split('.')[0]
                        padding = " " * 34 
                        self.messages_text.insert(tk.END, f"{padding}{msg[1:]}\n", 'system_text') 
                        prev_msg_sign = ' '

            self.messages_text.config(state='disabled')
            if unread_message_line:
                self.messages_text.see(f"{unread_message_line}.0")
            else:
                self.messages_text.see(tk.END)

    def fetch_weather(self, input_string):
        if not self.validate_entry(input_string):
            return

        input_string = input_string.split('-')
        if len(input_string) == 3:
            option, city, state = input_string
            input_data = f"{option}~{city}~{state}~"

            self.weather_report = '\n' + self.send_command(f"REPORT_WEATHER|{input_data}")
        else:
            self.weather_report = "Error: Invalid input"

        self.message_entry.delete(0, tk.END)

        self.display_weather_report()
    
    def start_game(self, message):
        self.messages_text.config(state='normal')
        grid_size = message if message.isdigit() else 0
        grid_size = int(grid_size) if int(grid_size) <= 10 and int(grid_size) >= 3 else 0
        if grid_size == 0:
            self.messages_text.insert(tk.END, f"\nInvalid matrix size\n", 'chat_font')
        else:
            numbers_list = random.sample(range(1, grid_size*grid_size + 1), grid_size*grid_size)
            chat_font = ('Arial', 14)
            self.messages_text.insert(tk.END, f"\nMatrix size: {grid_size} \nMatrix: {str(numbers_list)}\n", 'chat_font')
            self.messages_text.see(tk.END)
            HundredsGame(grid_size, numbers_list, self.send_message, self.friend_name, self.messages_text, chat_font)

        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

    def display_weather_report(self):
        if self.friend_name != weather_bot:
            self.send_message(self.friend_name, self.weather_report)
            return
        self.messages_text.tag_configure('red_text', foreground='#DC143C', font=(FONT, 14))
        self.messages_text.tag_configure('green_text', foreground='#32CD32', font=(FONT, 14))
        self.messages_text.tag_configure('blue_text', foreground='#3399FF', font=(FONT, 14))

        self.messages_text.config(state='normal')
        #self.messages_text.delete(1.0, tk.END)

        if "Error" in self.weather_report:
            self.messages_text.insert(tk.END, "\n" + self.weather_report, 'red_text')
        else:
            self.messages_text.insert(tk.END, "\n" + self.weather_report, 'green_text')
        
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

    def update_entire_chat(self):
        """
        Clears the message display area and repopulates it with messages,
        effectively refreshing the chat.
        """
        # Ensure there's a current friend selected to chat with
        if hasattr(self, 'current_friend') and self.current_friend:
            # Clear the Text widget
            self.messages_text.config(state='normal')  # Temporarily enable the widget for editing
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.config(state='disabled')  # Disable the widget to prevent user editing

            self.last_message = ''
            # Repopulate the messages for the current chat
            self.populate_messages(self.current_friend, force_scroll=True)


    def send_message(self, friend_name, message=''):
        # Retrieve the message from the entry
        start_numbers_game = False
        if message == '':
            message = self.message_entry.get()

        if not self.validate_entry(message):
            return
    
        if friend_name == weather_bot:
            self.message_entry.delete(0, tk.END)
            self.fetch_weather(message)
            return

        if friend_name == hundreds_game:
            self.message_entry.delete(0, tk.END)
            self.start_game(message)
            return

        if message == "#same":
            message = self.same_message[1:len(self.same_message)-9]

        if message:
            if message[:9] == "#weather ":
                self.fetch_weather(message[9:])
                return

            if message == "#clear":
                response = self.send_command(f"CLEAR_MESSAGES|{self.username}|{friend_name}")
                self.message_entry.delete(0, tk.END)
                self.update_entire_chat()
                self.last_message = ''
                return

            if message[:13] == "#numbers game":
                try:
                    _, grid_size, numbers_list = message[10:].split('#')
                    try:
                        numbers_list = ast.literal_eval(numbers_list)
                    except:
                        grid_size = 1
                    if not (len(numbers_list) == len(set(numbers_list)) and 
                            len(numbers_list) == int(grid_size)*int(grid_size) and
                            all(1 <= n <= int(grid_size)*int(grid_size) for n in numbers_list)):
                        grid_size = 1 #Invalid matrix
                except ValueError:
                    try:
                        _, grid_size = message[13:].split('#')
                        if not grid_size.isdigit():
                            grid_size = 0
                        else:
                            grid_size = int(grid_size) if int(grid_size) <= 10  and int(grid_size) >= 3 else 0
                    except ValueError:
                        grid_size = 5
                    numbers_list = random.sample(range(1, grid_size*grid_size + 1), grid_size*grid_size)
                if grid_size == 0:
                    message = "Invalid matrix size"
                elif grid_size == 1:
                    message = "Invalid matrix"
                else:
                    start_numbers_game = True
                    message = message[:13] + f" #{grid_size} #{str(numbers_list)}"
            send_again = False
            if len(message) > 900:
                send_again = True
            if '+' + message == self.last_message[:len(self.last_message)-9]:
                message += ' '
            response = self.send_command(f"SENDMESSAGE|{self.username}|{friend_name}|{message if not send_again else message[:900]}")
            if response == "Message sent":
                self.populate_messages(friend_name, True) 
            else:
                messagebox.showerror("Error", response)

            self.message_entry.delete(0, tk.END)
            if send_again:
                self.send_message(friend_name, message[900:])

            if start_numbers_game:
                HundredsGame(grid_size, numbers_list, self.send_message, self.friend_name)

    def back_to_friends(self):
        # Clear the chat frame, reinitialize the friends frame, and stop updates
        global screen_on
        if screen_on:
            messagebox.showerror("Error", "Close all other windows to go back")
            return
        if self.friend_name not in bots:
            response = self.send_command(f"FRIEND_OFF|{self.username}|{self.friend_name}")

        self.last_message = ''
        self.friend_name = ''

        if hasattr(self, 'current_friend'):
            del self.current_friend  # Stop updates by removing the current_friend attribute
        self.chat_frame.pack_forget()
        self.initialize_friends_frame()

    def populate_friends_buttons(self):
        response = self.send_command(f"SHOWFRIENDS|{self.username}")
        if response and response != "No friends":
            friends_list = response.split('\n')
            for index, friend in enumerate(friends_list):
                # Create a button for each friend
                btn = tk.Button(self.friends_frame, text=friend, command=lambda f=friend: self.open_chat(f))
                btn.grid(row=index + 1, column=0, sticky="ew")

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.initialize_signup_frame()
    
    def show_login_frame(self):
        self.signup_frame.pack_forget()
        self.initialize_login_frame()

    def show_friends_frame(self):
        self.login_frame.pack_forget()
        self.initialize_friends_frame()

    def delete_friend(self):
        friend_name = self.friendname_entry.get()  # Get the friend's name from the entry widget
        if friend_name == "":
            return
        response = self.send_command(f"DELETE_FRIEND|{self.username}|{friend_name}")
        if response != "Friend deleted":
            messagebox.showerror("Fail", response)
        else:
            self.friendname_entry.delete(0, tk.END)
            self.update_friends_list()

    def add_friend(self):
        friend_name = self.friendname_entry.get()  # Get the friend's name from the entry widget

        if not self.validate_entry(friend_name):
            return

        if friend_name == "":
            return

        response = self.send_command(f"FRIENDSCOUNT|{self.username}")
        if "None" == response or "" == response:
            messagebox.showerror("Fail", "User not found")
        elif int(response) >= MAX_FRIENDS:
            messagebox.showerror("Fail", "Max friends reached")
        else:
            if friend_name not in bots:
                response = self.send_command(f"FRIENDSCOUNT|{friend_name}")
                if response != 'None' and int(response) >= MAX_FRIENDS:
                    messagebox.showerror("Fail", "User max friends reached")
                    return

            response = self.send_command(f"ADDFRIEND|{self.username}|{friend_name}")
            if response != "Friend added":
                messagebox.showerror("Fail", response)
            else:
                self.friendname_entry.delete(0, tk.END)
                self.update_friends_list()
                if friend_name not in bots:
                    response = self.send_command(f"FRIEND_OFF|{self.username}|{friend_name}")
                    response = self.send_command(f"FRIEND_OFF|{friend_name}|{self.username}")
                    pass

    def login(self):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((HOST, PORT))
            except ConnectionRefusedError:
                messagebox.showerror("Connection Error", "Failed to connect to the server.")
                self.sock = None
                #self.destroy()
                return

        self.username = self.username_entry.get()
        password = self.password_entry.get()
        if not self.validate_entry(self.username) or not self.validate_entry(password):
            return

        response = self.send_command(f"LOGIN|{self.username}|{password}")
        if response == "Login successful":
            self.show_friends_frame()
        else:
            messagebox.showerror("Fail", response)

    def signup(self):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((HOST, PORT))
            except ConnectionRefusedError:
                messagebox.showerror("Connection Error", "Failed to connect to the server.")
                self.sock = None
                #self.destroy()
                return

        self.username = self.username_entry.get()
            
        if len(self.username) > 20:
            messagebox.showerror("Fail", "Name too long, max 20 characters")
            return
        elif len(self.username) < 1:
            messagebox.showerror("Fail", "Name too short")
            return
        elif self.username in bots:
            messagebox.showerror("Fail", "Username is taken")
            return

        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return

        if (not self.validate_entry(self.username) or not self.validate_entry(password) or
        not self.validate_entry(confirm_password)):
            return

        response = self.send_command(f"SIGNUP|{self.username}|{password}")
        if response != "Signup successful":
            messagebox.showerror("Fail", response)
        else:
            self.show_login_frame()

    def logout(self):
        self.username = ''
        response = self.send_command(f"LOGOUT|{self.username}")
        if self.sock:
            self.sock.close()
            self.sock = None
        self.friends_frame.pack_forget()
        self.initialize_login_frame()

    def on_closing(self):
        if screen_on == 0:
            if self.sock:
                self.sock.close()
            self.destroy()
        else:
            messagebox.showerror("Error", "Close all other windows before exiting")

class HundredsGame:
    def __init__(self, new_grid_size=5, numbers_list=None, send_message=None, friend_name=None, widget=None, chat_font=None):
        new_grid_size = int(new_grid_size)
        if numbers_list is None or len(numbers_list) != new_grid_size*new_grid_size:
            numbers_list = random.sample(range(1, new_grid_size*new_grid_size + 1), new_grid_size*new_grid_size)
        self.grid_size = new_grid_size if new_grid_size <= 10 and new_grid_size >= 3 else 5
        self.root = tk.Tk()
        self.padding = '\t' * (self.grid_size-1) if self.grid_size > 3 else ' '
        self.root.title(f"Find: 1{self.padding}Time: 00:00")
        self.root.resizable(False, False)
        self.send_message = send_message
        self.friend_name = friend_name
        self.widget = widget
        self.chat_font = chat_font
        self.numbers_count = self.grid_size*self.grid_size

        self.numbers_list = numbers_list
        self.number_to_find = 1
        self.button_height = 2  # Height in text units
        self.button_width = 2   # Width in text units
        self.button_font = ('Roboto', 20, 'bold')  # Font for the button text
        self.after_id = None

        self.buttons = {}  # Track buttons to update them

        global game_result
        global screen_on
        screen_on += 1

        self.start_time = time.time()
        self.initiate_grid()

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.mainloop()
    
    def button_command(self, number):
        if number == self.number_to_find:
            self.number_to_find += 1
            if number == self.numbers_count:
                self.print_result(finished=True)
                self.root.quit()
                self.root.destroy()
                return
            self.update_grid()

    def print_result(self, finished=False):
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        # Define the game_result message based on whether minutes > 0.
        if minutes > 0:
            time_msg = f"{int(minutes)} minutes and {int(seconds)} seconds"
        else:
            time_msg = f"{int(seconds)} seconds"

        # Check if we need to send a message or update the widget directly.
        if self.send_message and self.friend_name:
            if self.friend_name == hundreds_game:
                self.widget.config(state='normal')
                if not finished:
                    game_result = f"Game Over!\nYou found {self.number_to_find - 1} out of {self.numbers_count} numbers\nTime: {time_msg}"
                else:
                    game_result = f"Congradulations!\nYou found all the {self.number_to_find} numbers\nTime: {time_msg}"
                
                self.widget.insert(tk.END, "\n" + game_result + "\n", 'chat_font')
                self.widget.see(tk.END)
            else:
                if not finished:
                    game_result = f"Game Over!\nI found {self.number_to_find - 1} out of {self.numbers_count} numbers\nTime: {time_msg}"
                else:
                    game_result = f"Let's go!\nI found all the {self.number_to_find} numbers\nTime: {time_msg}"
                self.send_message(self.friend_name, game_result)
        global screen_on
        screen_on -= 1

    def initiate_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                number = self.numbers_list[row*self.grid_size + col]
                button = tk.Button(self.root, text=str(number), width=self.button_width, 
                                   height=self.button_height, font=self.button_font, 
                                   command=lambda n=number: self.button_command(n))
                button.grid(row=row, column=col, padx=1, pady=1)
                self.buttons[(row, col)] = button
        self.update_timer()

    def update_timer(self):
        global screen_on
        if screen_on < 1:
            self.on_close()
            return
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        self.root.title(f"Find: {self.number_to_find}{self.padding}Time: {int(minutes)}:{int(seconds)}")
        self.after_id = self.root.after(100, self.update_timer)  # Store the ID

    def update_grid(self):
        for idx, number in enumerate(self.numbers_list):
            row, col = divmod(idx, self.grid_size)
            button = self.buttons[(row, col)]
            if number >= self.number_to_find:
                button.config(text=str(number), command=lambda n=number: self.button_command(n))
            else:
                button.config(text=' ')

    def on_close(self):
        if hasattr(self, 'after_id') and self.after_id:
            self.root.after_cancel(self.after_id)
        self.print_result()
        self.root.destroy()

if __name__ == "__main__":
    app = AppClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
