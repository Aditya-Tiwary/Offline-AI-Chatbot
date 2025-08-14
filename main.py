import tkinter as tk
from tkinter import scrolledtext, filedialog, Menu, ttk
import ollama
import threading
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import time
from PIL import Image, ImageTk, ImageSequence
from datetime import datetime
import os

# Initialize Ollama with model
model_name = "deepseek-r1:8b"

# Conversation tracking variables
conversation_name_set = False
conversation_name = "New Chat"
stop_thread = None
current_message_tag = None
message_data = {}

# Color scheme
COLORS = {
    "primary": "#4361ee",  # Primary blue
    "secondary": "#3a0ca3",  # Deep purple
    "accent": "#7209b7",  # Vibrant purple
    "light_accent": "#f72585",  # Pink accent
    "background": "#f8f9fa",  # Light gray background
    "card": "#ffffff",  # White card background
    "text_primary": "#212529",  # Dark text
    "text_secondary": "#6c757d",  # Gray text
    "success": "#4ade80",  # Green
    "warning": "#fbbf24",  # Yellow/Orange
    "danger": "#ef4444",  # Red
    "user_msg_bg": "#e9ecef",  # Light gray for user messages
    "bot_msg_bg": "#e7f5ff",  # Light blue for bot messages
    "yellow_highlight": "#FFFF00",  # Yellow for inline code
}

class GifPlayer:
    def __init__(self, parent, gif_path):
        self.parent = parent
        self.gif_path = gif_path
        self.frames = []
        self.frame_count = 0
        self.current_frame = 0
        self.delay = 10
        self.active = False

        # Create label for GIF display
        self.label = tk.Label(parent, bg=COLORS["background"])
        self.load_gif()

    def load_gif(self):
        """Load and prepare the animated GIF"""
        try:
            if not os.path.exists(self.gif_path):
                print(f"GIF file not found: {self.gif_path}")
                return

            gif = Image.open(self.gif_path)
            try:
                while True:
                    frame = ImageTk.PhotoImage(gif.copy())
                    self.frames.append(frame)
                    self.frame_count += 1
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass

            try:
                self.delay = gif.info['duration']
            except:
                pass

        except Exception as e:
            print(f"Error loading GIF: {e}")

    def start(self):
        """Start the animation"""
        if self.frames and not self.active:
            self.active = True
            self.label.pack(side=tk.BOTTOM, padx=5, pady=5)
            self.animate()

    def stop(self):
        """Stop the animation"""
        self.active = False
        self.label.pack_forget()

    def animate(self):
        """Display the next frame in the animation"""
        if self.active and self.frames:
            self.label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.parent.after(self.delay, self.animate)

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aditya AI Assistant")
        self.root.state('zoomed')
        self.root.geometry("1920x1080")
        self.root.configure(bg=COLORS["background"])

        # Create frames
        self.welcome_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.input_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])

        # Load and prepare logo
        self.logo_path = r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\gif\logo.gif"
        self.logo_images = []
        self.logo_frame = 0
        self.logo_animation_id = None
        self.load_and_prepare_logo()

        # Initialize loading GIF
        self.loading_gif_path = r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\gif\loading.gif"

        # Initialize UI components
        self.create_welcome_screen()
        self.create_input_screen()
        self.create_main_interface()

        # Show welcome screen initially
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)

    def load_and_prepare_logo(self):
        try:
            gif = Image.open(self.logo_path)
            frames = []
            for frame in ImageSequence.Iterator(gif):
                frame = frame.copy()
                frame = frame.resize((250, 250), Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
            self.logo_images = frames
            if not self.logo_images:
                print("No frames found in GIF.")
                self.logo = ImageTk.PhotoImage(Image.new("RGBA", (250, 250), (255, 255, 255, 0)))
            else:
                self.logo = self.logo_images[0]
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.logo = ImageTk.PhotoImage(Image.new("RGBA", (250, 250), (255, 255, 255, 0)))

    def animate_logo(self):
        if self.logo_images and len(self.logo_images) > 1:
            self.logo_frame = (self.logo_frame + 1) % len(self.logo_images)
            self.logo = self.logo_images[self.logo_frame]
            if hasattr(self, 'input_canvas') and hasattr(self, 'input_logo_item'):
                self.input_canvas.itemconfig(self.input_logo_item, image=self.logo)
            if hasattr(self, 'welcome_logo_label'):
                self.welcome_logo_label.config(image=self.logo)
            self.logo_animation_id = self.root.after(100, self.animate_logo)

    def create_welcome_screen(self):
        # Main welcome content frame with a split layout
        welcome_content = tk.Frame(self.welcome_frame, bg=COLORS["background"])
        welcome_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Split into left and right sections
        left_frame = tk.Frame(welcome_content, bg=COLORS["card"], padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_frame = tk.Frame(welcome_content, bg=COLORS["background"], padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left Frame: Header and Tabs
        header_frame = tk.Frame(left_frame, bg=COLORS["card"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        logo_label = tk.Label(header_frame, text="DISSERATION", font=("Segoe UI", 36, "bold"),
                             fg=COLORS["primary"], bg=COLORS["card"])
        logo_label.pack(pady=(10, 0))

        self.tagline_label = tk.Label(header_frame, text="",
                                      font=("Segoe UI", 14), fg=COLORS["text_secondary"], bg=COLORS["card"])
        self.tagline_label.pack(pady=(0, 20))

        main_content_frame = tk.Frame(left_frame, bg=COLORS["card"])
        main_content_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))

        welcome_tabs = ttk.Notebook(main_content_frame)
        welcome_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        about_tab = tk.Frame(welcome_tabs, bg=COLORS["card"])
        developer_tab = tk.Frame(welcome_tabs, bg=COLORS["card"])
        instructions_tab = tk.Frame(welcome_tabs, bg=COLORS["card"])

        welcome_tabs.add(about_tab, text="About Project")
        welcome_tabs.add(developer_tab, text="My Information")
        welcome_tabs.add(instructions_tab, text="Instructions")

        about_text = """
        This chatbot application is designed to provide an interactive AI experience built using built using Python with the 
        Tkinter library for the GUI and powered by the DeepSeek-R1:8b model from Ollama, the DeepSeek-R1 model with 8 
        billion parameters. The application facilitates natural language conversation with an AI assistant trained on a diverse 
        range of knowledge.

        Key Features:

        • Natural language processing for human-like conversations
        • Fully offline operation – no internet required
        • Complete privacy – no data sent outside your device
        • No context limits – unlimited conversation depth and history
        • Conversation history management
        • PDF export functionality for saving chats
        • Modern, intuitive user interface
        • Message management with right-click options (copy, delete, resend)
        """

        about_content = tk.Text(about_tab, wrap=tk.WORD, font=("Segoe UI", 11), bg=COLORS["card"],
                                fg=COLORS["text_primary"], relief=tk.FLAT, height=15)
        about_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        about_content.insert(tk.END, about_text)
        about_content.config(state=tk.DISABLED)

        dev_info = [
            ("Name:", "Aditya Tiwary"),
            ("University Roll Number:", "2XMCA92X0XXX"),
            ("Registration Number:", "XXXXXX"),
            ("Class Roll Number:", "MCA-XX"),
            ("Session:", "202X–202X"),
            ("Semester:", "4"),
            ("Subject:", "C11 XXMCA404 (Final Project)"),
            ("Institution:", "XXXXXXX College, XXXXXX University")
        ]

        dev_frame = tk.Frame(developer_tab, bg=COLORS["card"], padx=15, pady=15)
        dev_frame.pack(fill=tk.BOTH, expand=True)

        for i, (label_text, value_text) in enumerate(dev_info):
            info_frame = tk.Frame(dev_frame, bg=COLORS["card"])
            info_frame.pack(fill=tk.X, pady=5, anchor="w")

            label = tk.Label(info_frame, text=label_text, font=("Segoe UI", 11, "bold"),
                             bg=COLORS["card"], fg=COLORS["text_primary"], width=20, anchor="w")
            label.pack(side=tk.LEFT)

            value = tk.Label(info_frame, text=value_text, font=("Segoe UI", 11),
                             bg=COLORS["card"], fg=COLORS["text_primary"], anchor="w")
            value.pack(side=tk.LEFT, fill=tk.X, expand=True)

        instructions_text = """
        Using the Chatbot:

        1. Click "Start Chatting" to begin.
        2. Type your message and press Enter or click Send.
        3. The AI will respond in the conversation area.
        4. Additional Features:
           • "Regenerate" for a new response
           • "Clear Chat" to reset
           • Right-click messages to copy, delete, or resend
           • "Save as PDF" to export
        """

        instructions_content = tk.Text(instructions_tab, wrap=tk.WORD, font=("Segoe UI", 11),
                                       bg=COLORS["card"], fg=COLORS["text_primary"], relief=tk.FLAT, height=15)
        instructions_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        instructions_content.insert(tk.END, instructions_text)
        instructions_content.config(state=tk.DISABLED)

        # Right Frame: Animated Logo and Feature Showcase
        right_inner_frame = tk.Frame(right_frame, bg=COLORS["card"], padx=20, pady=20)
        right_inner_frame.pack(fill=tk.BOTH, expand=True)

        # Animated Logo
        self.welcome_logo_label = tk.Label(right_inner_frame, image=self.logo, bg=COLORS["card"])
        self.welcome_logo_label.pack(pady=(20, 20))

        # Feature Showcase
        feature_frame = tk.Frame(right_inner_frame, bg=COLORS["card"])
        feature_frame.pack(fill=tk.BOTH, expand=True)

        # Assume we have these icon paths (you'll need to provide actual paths to icons)
        feature_icons = {
            "offline": r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\icons\offline.png",
            "privacy": r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\icons\privacy.png",
            "history": r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\icons\history.png",
            "export": r"C:\Users\Aditya_Tiwary\Desktop\Disseration\Offline Chatbot\icons\export.png"
        }

        features = [
            ("Offline Operation", "No internet required", feature_icons.get("offline")),
            ("Complete Privacy", "Your data stays on your device", feature_icons.get("privacy")),
            ("Unlimited History", "No context limits", feature_icons.get("history")),
            ("Export Chats", "Save conversations as PDF", feature_icons.get("export"))
        ]

        self.feature_images = []
        for title, description, icon_path in features:
            feature_card = tk.Frame(feature_frame, bg=COLORS["card"], pady=10)
            feature_card.pack(fill=tk.X, padx=10, pady=5)

            # Load and resize icon
            try:
                icon_img = Image.open(icon_path).resize((40, 40), Image.Resampling.LANCZOS)
                icon = ImageTk.PhotoImage(icon_img)
                self.feature_images.append(icon)  # Keep a reference to avoid garbage collection
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
                icon = ImageTk.PhotoImage(Image.new("RGBA", (40, 40), (255, 255, 255, 0)))

            icon_label = tk.Label(feature_card, image=icon, bg=COLORS["card"])
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

            text_frame = tk.Frame(feature_card, bg=COLORS["card"])
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            title_label = tk.Label(text_frame, text=title, font=("Segoe UI", 12, "bold"),
                                   fg=COLORS["primary"], bg=COLORS["card"], anchor="w")
            title_label.pack(fill=tk.X)

            desc_label = tk.Label(text_frame, text=description, font=("Segoe UI", 10),
                                  fg=COLORS["text_secondary"], bg=COLORS["card"], anchor="w")
            desc_label.pack(fill=tk.X)

        # Footer with Start Button
        footer_frame = tk.Frame(left_frame, bg=COLORS["card"])
        footer_frame.pack(fill=tk.X, pady=10)

        self.start_button = tk.Button(footer_frame, text="Start Chatting", font=("Segoe UI", 14, "bold"),
                                      command=self.start_chat, bg=COLORS["primary"], fg="white",
                                      activebackground=COLORS["secondary"], activeforeground="white",
                                      bd=0, padx=30, pady=12, relief="flat", cursor="hand2")
        self.start_button.pack(pady=10)
        self.start_button.bind("<Enter>", lambda e: self.button_hover(self.start_button, COLORS["secondary"]))
        self.start_button.bind("<Leave>", lambda e: self.button_leave(self.start_button, COLORS["primary"]))
        self.start_button.bind("<Button-1>", lambda e: self.button_click_animation(self.start_button))

        copyright_label = tk.Label(footer_frame, text="© 2025 Aditya - All Rights Reserved",
                                   font=("Segoe UI", 8), bg=COLORS["card"], fg=COLORS["text_secondary"])
        copyright_label.pack(side=tk.BOTTOM, pady=5)

        self.create_animations()

    def create_input_screen(self):
        self.input_canvas = tk.Canvas(self.input_frame, bg=COLORS["background"], highlightthickness=0)
        self.input_canvas.pack(fill=tk.BOTH, expand=True)
        self.create_gradient(self.input_canvas, "#FFFFFF", COLORS["primary"])

        center_x = self.root.winfo_screenwidth() // 2
        center_y = self.root.winfo_screenheight() // 2

        arrow_y_position = center_y + 20
        height = self.root.winfo_screenheight()
        color1 = "#FFFFFF"
        color2 = COLORS["primary"]
        r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
        steps = height // 2
        step_position = (arrow_y_position / height) * steps
        r = int(r1 + (r2 - r1) * step_position / steps)
        g = int(g1 + (g2 - g1) * step_position / steps)
        b = int(b1 + (b2 - b1) * step_position / steps)
        arrow_canvas_bg = f"#{r:02x}{g:02x}{b:02x}"

        if self.logo:
            self.input_logo_item = self.input_canvas.create_image(center_x, center_y - 125, image=self.logo, anchor="center")
        self.animate_logo()

        self.initial_input_entry = tk.Entry(self.input_canvas, font=("Segoe UI", 14), width=60,
                                            bg=COLORS["card"], fg=COLORS["text_primary"],
                                            bd=1, relief="solid", insertbackground=COLORS["text_primary"])
        self.initial_input_entry.insert(0, "What's on your mind?")
        self.initial_input_entry.bind("<FocusIn>", lambda e: self.clear_placeholder())
        self.initial_input_entry.bind("<Return>", self.start_chat_with_input)

        self.arrow_canvas = tk.Canvas(self.input_canvas, width=40, height=40, bg=arrow_canvas_bg,
                                      highlightthickness=0, bd=0)
        self.arrow_circle = self.arrow_canvas.create_oval(5, 5, 35, 35, fill=COLORS["primary"], outline="")
        self.arrow_text = self.arrow_canvas.create_text(20, 20, text="↑", font=("Segoe UI", 18, "bold"),
                                                        fill="white")

        self.initial_input_entry.update()
        self.arrow_canvas.update()

        input_window = self.input_canvas.create_window(center_x, center_y + 20,
                                                       window=self.initial_input_entry, anchor="center")
        input_bbox = self.input_canvas.bbox(input_window)
        input_width = input_bbox[2] - input_bbox[0]
        input_x = center_x - (input_width // 2)
        arrow_position_x = input_x + input_width + 10
        self.input_canvas.create_window(arrow_position_x, center_y + 20,
                                        window=self.arrow_canvas, anchor="center")

        self.arrow_canvas.tag_bind(self.arrow_circle, "<Button-1>", self.start_chat_with_input)
        self.arrow_canvas.tag_bind(self.arrow_text, "<Button-1>", self.start_chat_with_input)
        self.arrow_canvas.tag_bind(self.arrow_circle, "<Enter>", lambda e: self.button_hover_canvas(COLORS["secondary"]))
        self.arrow_canvas.tag_bind(self.arrow_text, "<Enter>", lambda e: self.button_hover_canvas(COLORS["secondary"]))
        self.arrow_canvas.tag_bind(self.arrow_circle, "<Leave>", lambda e: self.button_leave_canvas(COLORS["primary"]))
        self.arrow_canvas.tag_bind(self.arrow_text, "<Leave>", lambda e: self.button_leave_canvas(COLORS["primary"]))
        self.arrow_canvas.tag_bind(self.arrow_circle, "<Button-1>", lambda e: self.button_click_animation_canvas())

    def create_main_interface(self):
        main_header_frame = tk.Frame(self.main_frame, bg=COLORS["card"], height=60)
        main_header_frame.pack(fill="x", padx=0, pady=0)
        main_header_frame.pack_propagate(False)

        header_logo = tk.Label(main_header_frame, text="Aditya AI", font=("Segoe UI", 18, "bold"),
                               fg=COLORS["primary"], bg=COLORS["card"])
        header_logo.pack(side="left", padx=20)

        self.conversation_name_label = tk.Label(main_header_frame, text="New Chat",
                                                font=("Segoe UI", 14), bg=COLORS["card"],
                                                fg=COLORS["text_primary"])
        self.conversation_name_label.pack(side="left", padx=20)

        chat_container = tk.Frame(self.main_frame, bg=COLORS["background"])
        chat_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.chat_box = scrolledtext.ScrolledText(chat_container, wrap=tk.WORD,
                                                  font=("Segoe UI", 11), bg=COLORS["card"],
                                                  fg=COLORS["text_primary"], bd=0,
                                                  insertbackground=COLORS["text_primary"],
                                                  selectbackground=COLORS["primary"],
                                                  padx=20, pady=20)
        self.chat_box.pack(fill="both", expand=True, padx=0, pady=0)
        self.chat_box.config(state=tk.DISABLED)  # Set to disabled by default

        # Bind chat_box to ignore keyboard input
        self.chat_box.bind("<Key>", lambda e: "break")  # Prevent typing
        self.chat_box.bind("<Button-1>", lambda e: "break")  # Prevent focus on click

        # Define tags for text formatting
        self.chat_box.tag_configure("timestamp", font=("Segoe UI", 9), foreground=COLORS["text_secondary"])
        self.chat_box.tag_configure("user_text", font=("Segoe UI", 11), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("bot_text", font=("Segoe UI", 11), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("bold_text", font=("Segoe UI", 11, "bold"), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("header1", font=("Segoe UI", 16, "bold"), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("header2", font=("Segoe UI", 14, "bold"), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("header3", font=("Segoe UI", 12, "bold"), foreground=COLORS["text_primary"],
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("code_block", font=("Consolas", 10), foreground="#0000FF", background="#FFFFFF",
                                    spacing1=2, spacing3=2)
        self.chat_box.tag_configure("inline_code", font=("Consolas", 11), foreground=COLORS["text_primary"],
                                    background=COLORS["yellow_highlight"], spacing1=2, spacing3=2)

        self.chat_box.bind("<Button-3>", self.show_context_menu)

        input_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        input_frame.pack(fill="x", padx=20, pady=(0, 10))

        input_container = tk.Frame(input_frame, bg=COLORS["card"], bd=0, highlightthickness=1,
                                   highlightbackground=COLORS["text_secondary"])
        input_container.pack(fill="x", pady=(0, 5))

        self.user_input_entry = tk.Entry(input_container, font=("Segoe UI", 11), bg=COLORS["card"],
                                         fg=COLORS["text_primary"], bd=0,
                                         insertbackground=COLORS["text_primary"])
        self.user_input_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=10, pady=10)

        self.send_button = tk.Button(input_container, text="Send", font=("Segoe UI", 10, "bold"),
                                     command=self.get_response, bg=COLORS["primary"], fg="white",
                                     activebackground=COLORS["secondary"], activeforeground="white",
                                     bd=0, padx=15, pady=5, relief="flat", cursor="hand2")
        self.send_button.pack(side=tk.RIGHT, padx=(0, 10), pady=5)
        self.send_button.bind("<Enter>", lambda e: self.button_hover(self.send_button, COLORS["secondary"]))
        self.send_button.bind("<Leave>", lambda e: self.button_leave(self.send_button, COLORS["primary"]))
        self.send_button.bind("<Button-1>", lambda e: self.button_click_animation(self.send_button))

        # Combined button and GIF frame
        control_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        control_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Initialize GIF player within control frame
        self.gif_player = GifPlayer(control_frame, self.loading_gif_path)

        # Add buttons to the same frame as the GIF
        self.regenerate_button = tk.Button(control_frame, text="Regenerate", font=("Segoe UI", 10, "bold"),
                                           command=self.regenerate_response, bg=COLORS["warning"], fg="white",
                                           activebackground=COLORS["accent"], activeforeground="white",
                                           bd=0, padx=15, pady=5, relief="flat", cursor="hand2")
        self.regenerate_button.pack(side=tk.LEFT, padx=(0, 10))
        self.regenerate_button.bind("<Enter>", lambda e: self.button_hover(self.regenerate_button, COLORS["accent"]))
        self.regenerate_button.bind("<Leave>", lambda e: self.button_leave(self.regenerate_button, COLORS["warning"]))
        self.regenerate_button.bind("<Button-1>", lambda e: self.button_click_animation(self.regenerate_button))

        clear_button = tk.Button(control_frame, text="Clear Chat", font=("Segoe UI", 10, "bold"),
                                 command=self.clear_chat, bg=COLORS["light_accent"], fg="white",
                                 activebackground=COLORS["accent"], activeforeground="white",
                                 bd=0, padx=15, pady=5, relief="flat", cursor="hand2")
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        clear_button.bind("<Enter>", lambda e: self.button_hover(clear_button, COLORS["accent"]))
        clear_button.bind("<Leave>", lambda e: self.button_leave(clear_button, COLORS["light_accent"]))
        clear_button.bind("<Button-1>", lambda e: self.button_click_animation(clear_button))

        stop_button = tk.Button(control_frame, text="Stop", font=("Segoe UI", 10, "bold"),
                                command=self.stop_bot, bg=COLORS["danger"], fg="white",
                                activebackground=COLORS["secondary"], activeforeground="white",
                                bd=0, padx=15, pady=5, relief="flat", cursor="hand2")
        stop_button.pack(side=tk.LEFT, padx=(0, 10))
        stop_button.bind("<Enter>", lambda e: self.button_hover(stop_button, COLORS["secondary"]))
        stop_button.bind("<Leave>", lambda e: self.button_leave(stop_button, COLORS["danger"]))
        stop_button.bind("<Button-1>", lambda e: self.button_click_animation(stop_button))

        self.save_button = tk.Button(control_frame, text="Save as PDF", font=("Segoe UI", 10, "bold"),
                                     command=self.save_chat_to_pdf, bg=COLORS["success"], fg="white",
                                     activebackground=COLORS["secondary"], activeforeground="white",
                                     bd=0, padx=15, pady=5, relief="flat", cursor="hand2")
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        self.save_button.bind("<Enter>", lambda e: self.button_hover(self.save_button, COLORS["secondary"]))
        self.save_button.bind("<Leave>", lambda e: self.button_leave(self.save_button, COLORS["success"]))
        self.save_button.bind("<Button-1>", lambda e: self.button_click_animation(self.save_button))

        self.status_frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        self.status_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.status_label = tk.Label(self.status_frame, text="", font=("Segoe UI", 10),
                                     fg=COLORS["text_secondary"], bg=COLORS["background"])
        self.status_label.pack()

    def start_chat(self):
        self.welcome_frame.pack_forget()
        self.input_frame.pack(fill=tk.BOTH, expand=True)

    def start_chat_with_input(self, event=None):
        user_input = self.initial_input_entry.get().strip()
        if not user_input:
            return
        self.input_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.user_input_entry.insert(0, user_input)
        self.get_response()
        if self.logo_animation_id:
            self.root.after_cancel(self.logo_animation_id)
            self.logo_animation_id = None

    def get_response(self, event=None):
        global conversation_name_set, conversation_name, stop_thread
        user_input = self.user_input_entry.get().strip()
        if not user_input:
            return

        self.send_button.config(state=tk.DISABLED)
        self.regenerate_button.config(state=tk.DISABLED)
        self.chat_box.config(state=tk.NORMAL)  # Temporarily enable to insert text
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_msg_tag = f"user_msg_{self.chat_box.index('end-1c').split('.')[0]}"

        # Insert timestamp
        self.chat_box.insert(tk.END, f"You • {timestamp}\n", "timestamp")
        start_pos = self.chat_box.index("end-1c")
        
        # Insert each line of user input with dynamic background highlight
        lines = user_input.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                line_tag = f"{user_msg_tag}_line_{i}"
                self.chat_box.insert(tk.END, line, "user_text")
                if i < len(lines) - 1 or not lines[-1].strip():
                    self.chat_box.insert(tk.END, '\n')
                # Apply background highlight for this specific line
                line_start = start_pos if i == 0 else f"{start_pos}+{i}lines"
                line_end = f"{line_start} lineend"
                self.chat_box.tag_add(line_tag, line_start, line_end)
                self.chat_box.tag_configure(line_tag, background=COLORS["user_msg_bg"])

        self.chat_box.insert(tk.END, '\n\n')  # Add spacing after message
        message_data[user_msg_tag] = user_input
        self.user_input_entry.delete(0, tk.END)
        self.gif_player.start()
        stop_thread = threading.Thread(target=self.generate_summary_and_response, args=(user_input,))
        stop_thread.start()
        self.chat_box.config(state=tk.DISABLED)  # Disable after inserting

    def generate_summary_and_response(self, user_input):
        global conversation_name_set, conversation_name, stop_thread
        try:
            summary_prompt = f"Summarize the user's prompt '{user_input}' in a few words suitable for naming a conversation. Respond with the conversation name only."
            summary_response = ollama.chat(model=model_name, messages=[{"role": "user", "content": summary_prompt}])
            summary = self.remove_think_tags_for_summary(summary_response['message']['content'].strip())
            if not conversation_name_set:
                conversation_name = summary
                conversation_name_set = True
            self.root.after(0, self.update_conversation_name)
            response = ollama.chat(model=model_name, messages=[{"role": "user", "content": user_input}])
            bot_response = response['message']['content']
            formatted_bot_response = self.format_bot_response(bot_response)
        except Exception as e:
            print(f"Error: {e}")
            bot_response = "Sorry, I couldn't get a response. Try again later."
            formatted_bot_response = self.format_bot_response(bot_response)
            conversation_name = "Conversation Error"
            conversation_name_set = True
        self.root.after(0, self.update_chat, formatted_bot_response)

    def format_bot_response(self, response):
        clean_response = self.remove_think_tags_for_response(response)
        formatted_response = self.apply_basic_formatting(clean_response)
        return formatted_response

    def apply_basic_formatting(self, response):
        lines = response.split('\n')
        formatted_lines = []
        in_code_block = False
        code_block_content = []

        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('```'):
                    if in_code_block:
                        formatted_lines.extend(code_block_content)
                        code_block_content = []
                    in_code_block = not in_code_block
                elif in_code_block:
                    code_block_content.append(line)
                else:
                    formatted_line = self.format_line_for_display(line)
                    formatted_lines.append(formatted_line)
            else:
                formatted_lines.append("")

        if in_code_block and code_block_content:
            formatted_lines.extend(code_block_content)

        return '\n'.join(formatted_lines)

    def format_line_for_display(self, line):
        formatted_line = line.strip()
        if not formatted_line:
            return ""

        if formatted_line == "---":
            return ""

        header_match = re.match(r'^#{1,6}\s+', formatted_line)
        if header_match:
            header_level = len(header_match.group())
            header_text = re.sub(r'^#{1,6}\s+', '', formatted_line)
            header_text = re.sub(r'\*\*(.*?)\*\*', r'\1', header_text)
            header_text = re.sub(r'__(.*?)__', r'\1', header_text)
            return f"{'  ' * (header_level - 1)}{header_text}"

        bold_matches = re.findall(r'\*\*(.*?)\*\*|__(.*?)__', formatted_line)
        for match in bold_matches:
            bold_text = match[0] if match[0] else match[1]
            if bold_text:
                formatted_line = formatted_line.replace(f"**{bold_text}**", bold_text)
                formatted_line = formatted_line.replace(f"__{bold_text}__", bold_text)

        italic_matches = re.findall(r'\*(.*?)\*|_(.*?)_', formatted_line)
        for match in italic_matches:
            italic_text = match[0] if match[0] else match[1]
            if italic_text:
                formatted_line = formatted_line.replace(f"*{italic_text}*", italic_text)
                formatted_line = formatted_line.replace(f"_{italic_text}_", italic_text)

        if re.match(r'^[-*+]\s+', formatted_line):
            list_text = re.sub(r'^[-*+]\s+', '• ', formatted_line)
            list_text = re.sub(r'\*\*(.*?)\*\*', r'\1', list_text)
            list_text = re.sub(r'__(.*?)__', r'\1', list_text)
            return f"   {list_text}"

        if re.match(r'^\d+\.\s+', formatted_line):
            num, text = re.match(r'(\d+)\.\s+(.*)', formatted_line).groups()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'__(.*?)__', r'\1', text)
            return f"    {text}"

        if re.match(r'^>\s+', formatted_line):
            quote_text = re.sub(r'^>\s+', '', formatted_line)
            quote_text = re.sub(r'\*\*(.*?)\*\*', r'\1', quote_text)
            quote_text = re.sub(r'__(.*?)__', r'\1', quote_text)
            return f"> {quote_text}"

        inline_code_matches = re.findall(r'`([^`]+)`', formatted_line)
        for code_text in inline_code_matches:
            formatted_line = formatted_line.replace(f"`{code_text}`", f"{code_text}")

        return formatted_line

    def remove_think_tags_for_summary(self, response):
        clean_response = re.sub(r'<think.*?>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        clean_response = re.sub(r'\s+', ' ', clean_response).strip()
        clean_response = re.sub(r'["\'`](.*?)["\'`]', r'\1', clean_response)
        clean_response = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', clean_response)
        return clean_response

    def remove_think_tags_for_response(self, response):
        clean_response = re.sub(r'<think.*?>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
        return clean_response

    def update_conversation_name(self):
        self.conversation_name_label.config(text=conversation_name)

    def update_chat(self, bot_response):
        self.gif_player.stop()
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_box.config(state=tk.NORMAL)  # Temporarily enable to insert text
        bot_msg_tag = f"bot_msg_{self.chat_box.index('end-1c').split('.')[0]}"

        # Insert timestamp
        self.chat_box.insert(tk.END, f"Aditya AI • {timestamp}\n", "timestamp")
        start_pos = self.chat_box.index("end-1c")

        # Insert each line of bot response with dynamic background highlight
        lines = bot_response.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                line_tag = f"{bot_msg_tag}_line_{i}"
                if re.match(r'^#{1,6}\s+', line):
                    header_level = len(re.match(r'^#+', line).group())
                    if header_level == 1:
                        self.chat_box.insert(tk.END, line, ("bot_text", "header1"))
                    elif header_level == 2:
                        self.chat_box.insert(tk.END, line, ("bot_text", "header2"))
                    elif header_level == 3:
                        self.chat_box.insert(tk.END, line, ("bot_text", "header3"))
                elif re.search(r'\*\*(.*?)\*\*', line):
                    self.chat_box.insert(tk.END, line, "bold_text")
                elif re.match(r'^[-*+]\s+', line) or re.match(r'^\d+\.\s+', line):
                    self.chat_box.insert(tk.END, line, "bot_text")
                elif re.match(r'^>\s+', line):
                    self.chat_box.insert(tk.END, line, "bot_text")
                else:
                    self.chat_box.insert(tk.END, line, "bot_text")
                
                if i < len(lines) - 1 or not lines[-1].strip():
                    self.chat_box.insert(tk.END, '\n')
                
                # Apply background highlight for this specific line
                line_start = start_pos if i == 0 else f"{start_pos}+{i}lines"
                line_end = f"{line_start} lineend"
                self.chat_box.tag_add(line_tag, line_start, line_end)
                self.chat_box.tag_configure(line_tag, background=COLORS["bot_msg_bg"])

        self.chat_box.insert(tk.END, '\n\n')  # Add spacing after message
        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)  # Disable after inserting
        self.send_button.config(state=tk.NORMAL)
        self.regenerate_button.config(state=tk.NORMAL)

    def insert_formatted_response(self, response, bot_msg_tag):
        lines = response.split('\n')
        current_pos = self.chat_box.index("end-1c")

        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                if line.startswith('```'):
                    code_lines = []
                    while lines and not lines[0].startswith('```'):
                        code_lines.append(lines.pop(0).strip())
                        if not lines:
                            break
                    code_content = '\n'.join(code_lines)
                    if code_content:
                        self.chat_box.insert(tk.END, f"\n{code_content}\n", "code_block")
                    if lines and lines[0].startswith('```'):
                        lines.pop(0)
                else:
                    formatted_line = self.format_line_for_chat(line)
                    line_tag = f"{bot_msg_tag}_line_{i}"
                    if re.match(r'^#{1,6}\s+', line):
                        header_level = len(re.match(r'^#+', line).group())
                        if header_level == 1:
                            self.chat_box.insert(tk.END, formatted_line + '\n', ("bot_text", "header1"))
                        elif header_level == 2:
                            self.chat_box.insert(tk.END, formatted_line + '\n', ("bot_text", "header2"))
                        elif header_level == 3:
                            self.chat_box.insert(tk.END, formatted_line + '\n', ("bot_text", "header3"))
                    elif re.search(r'\*\*(.*?)\*\*', line):
                        self.chat_box.insert(tk.END, formatted_line + '\n', "bold_text")
                    elif re.match(r'^[-*+]\s+', line) or re.match(r'^\d+\.\s+', line):
                        self.chat_box.insert(tk.END, formatted_line + '\n', "bot_text")
                    elif re.match(r'^>\s+', line):
                        self.chat_box.insert(tk.END, formatted_line + '\n', "bot_text")
                    else:
                        self.chat_box.insert(tk.END, formatted_line + '\n', "bot_text")
                    
                    # Apply background highlight for this specific line
                    line_start = current_pos if i == 0 else f"{current_pos}+{i}lines"
                    line_end = f"{line_start} lineend"
                    self.chat_box.tag_add(line_tag, line_start, line_end)
                    self.chat_box.tag_configure(line_tag, background=COLORS["bot_msg_bg"])
            else:
                continue

    def format_line_for_chat(self, line):
        formatted_line = line.strip()
        if not formatted_line:
            return ""

        inline_code_matches = re.findall(r'`([^`]+)`', formatted_line)
        if inline_code_matches:
            for code_text in inline_code_matches:
                start_pos = 0
                while True:
                    match = re.search(r'`([^`]+)`', formatted_line[start_pos:])
                    if not match:
                        break
                    start, end = match.span()
                    global_pos_start = start_pos + start
                    global_pos_end = start_pos + end
                    text_before = formatted_line[:global_pos_start]
                    text_after = formatted_line[global_pos_end:]
                    code_content = match.group(1)
                    formatted_line = text_before + code_content + text_after
                    start_pos = global_pos_start + len(code_content)

        return formatted_line

    def regenerate_response(self):
        user_tags = [tag for tag in message_data.keys() if tag.startswith("user_msg_")]
        if user_tags:
            last_user_tag = sorted(user_tags, key=lambda x: int(x.split('_')[2]))[-1]
            last_user_input = message_data[last_user_tag]
            self.chat_box.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            user_msg_tag = f"user_msg_{self.chat_box.index('end-1c').split('.')[0]}"
            self.chat_box.insert(tk.END, f"You • {timestamp}\n", "timestamp")
            start_pos = self.chat_box.index("end-1c")
            
            # Insert each line with dynamic background highlight
            lines = last_user_input.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    line_tag = f"{user_msg_tag}_line_{i}"
                    self.chat_box.insert(tk.END, line, "user_text")
                    if i < len(lines) - 1 or not lines[-1].strip():
                        self.chat_box.insert(tk.END, '\n')
                    line_start = start_pos if i == 0 else f"{start_pos}+{i}lines"
                    line_end = f"{line_start} lineend"
                    self.chat_box.tag_add(line_tag, line_start, line_end)
                    self.chat_box.tag_configure(line_tag, background=COLORS["user_msg_bg"])

            self.chat_box.insert(tk.END, '\n\n')
            message_data[user_msg_tag] = last_user_input
            self.gif_player.start()
            self.send_button.config(state=tk.DISABLED)
            self.regenerate_button.config(state=tk.DISABLED)
            threading.Thread(target=self.generate_summary_and_response, args=(last_user_input,)).start()
            self.chat_box.config(state=tk.DISABLED)  # Disable after inserting

    def save_chat_to_pdf(self):
        chat_content = self.chat_box.get("1.0", tk.END)
        self.save_button.config(state=tk.DISABLED)
        self.gif_player.start()
        threading.Thread(target=self.generate_pdf_with_ai_summary, args=(chat_content,)).start()

    def generate_pdf_with_ai_summary(self, chat_content):
        try:
            pdf_filename = f"{conversation_name}.pdf" if conversation_name_set else "Untitled Conversation.pdf"
            pdf_filename = re.sub(r'[\\/*?:"<>|]', "_", pdf_filename)
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=pdf_filename,
                                                     filetypes=[("PDF Files", "*.pdf")])
            if file_path:
                pdf = canvas.Canvas(file_path, pagesize=letter)
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(30, 770, conversation_name)
                pdf.setFont("Helvetica", 10)
                pdf.drawString(30, 755, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                pdf.line(30, 745, 550, 745)
                pdf.setFont("Helvetica", 10)
                margin = 30
                max_width = 550
                y_position = 725
                lines = chat_content.splitlines()
                processed_lines = []
                i = 0
                while i < len(lines):
                    if "•" in lines[i] and ":" in lines[i]:
                        sender = "Aditya AI: " if "Aditya AI" in lines[i] else "You: "
                        timestamp = lines[i].split("•")[1].strip()
                        processed_lines.append(f"{sender} [{timestamp}]")
                        if i + 1 < len(lines):
                            processed_lines.append(lines[i + 1])
                            i += 2
                        else:
                            i += 1
                    else:
                        if lines[i].strip():
                            processed_lines.append(lines[i])
                        i += 1
                for line in processed_lines:
                    if line.strip():
                        if pdf.stringWidth(line, "Helvetica", 10) > max_width:
                            wrapped_lines = self.wrap_text(line, max_width, pdf)
                            for wrapped_line in wrapped_lines:
                                if y_position < 50:
                                    pdf.showPage()
                                    pdf.setFont("Helvetica", 10)
                                    y_position = 750
                                pdf.drawString(margin, y_position, wrapped_line)
                                y_position -= 12
                        else:
                            if y_position < 50:
                                pdf.showPage()
                                pdf.setFont("Helvetica", 10)
                                y_position = 750
                            pdf.drawString(margin, y_position, line)
                            y_position -= 12
                    else:
                        y_position -= 6
                page_num = pdf.getPageNumber()
                pdf.drawString(280, 30, f"Page {page_num}")
                pdf.save()
        except Exception as e:
            print(f"Error generating PDF: {e}")
        self.root.after(0, self.update_after_pdf_generation)

    def update_after_pdf_generation(self):
        self.gif_player.stop()
        self.status_label.config(text="PDF saved successfully")
        self.root.after(2000, lambda: self.status_label.config(text=""))
        self.save_button.config(state=tk.NORMAL)

    def wrap_text(self, text, max_width, pdf):
        words = text.split(" ")
        wrapped_lines = []
        current_line = words[0]
        for word in words[1:]:
            if pdf.stringWidth(current_line + " " + word, "Helvetica", 10) <= max_width:
                current_line += " " + word
            else:
                wrapped_lines.append(current_line)
                current_line = word
        wrapped_lines.append(current_line)
        return wrapped_lines

    def clear_chat(self):
        global stop_thread, message_data, conversation_name_set, conversation_name
        if stop_thread is not None and stop_thread.is_alive():
            stop_thread = None
            self.gif_player.stop()
            self.status_label.config(text="Stopped and Cleared Chat")
            self.root.after(2000, lambda: self.status_label.config(text=""))
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete("1.0", tk.END)
        self.chat_box.config(state=tk.DISABLED)
        conversation_name = "New Chat"
        conversation_name_set = False
        self.conversation_name_label.config(text=conversation_name)
        message_data = {}

    def stop_bot(self):
        global stop_thread
        if stop_thread is not None and stop_thread.is_alive():
            stop_thread = None
            self.gif_player.stop()
            self.status_label.config(text="Bot Stopped")
            self.root.after(2000, lambda: self.status_label.config(text=""))
            self.send_button.config(state=tk.NORMAL)
            self.regenerate_button.config(state=tk.NORMAL)

    def show_context_menu(self, event):
        try:
            clicked_index = self.chat_box.index(f"@{event.x},{event.y}")
            tags = self.chat_box.tag_names(clicked_index)
            message_tags = [tag for tag in tags if tag.startswith("user_msg_") or tag.startswith("bot_msg_")]
            if message_tags:
                global current_message_tag
                current_message_tag = message_tags[0]
                context_menu = Menu(self.root, tearoff=0, bg=COLORS["card"], fg=COLORS["text_primary"],
                                    activebackground=COLORS["primary"], activeforeground="white")
                context_menu.add_command(label="Copy Message", command=self.copy_message)
                if current_message_tag.startswith("user_msg_"):
                    context_menu.add_command(label="Send Again", command=self.send_again)
                context_menu.add_command(label="Delete Message", command=self.delete_message)
                if current_message_tag.startswith("bot_msg_"):
                    context_menu.add_command(label="Select Text", command=self.select_text)
                context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Context menu error: {e}")

    def copy_message(self):
        try:
            if current_message_tag:
                tag_ranges = self.chat_box.tag_ranges(current_message_tag)
                start_index = tag_ranges[0]
                end_index = tag_ranges[1]
                message_text = self.chat_box.get(start_index, end_index)
                self.root.clipboard_clear()
                self.root.clipboard_append(message_text)
                self.status_label.config(text="Message copied to clipboard")
                self.root.after(2000, lambda: self.status_label.config(text=""))
        except Exception as e:
            print(f"Copy error: {e}")

    def send_again(self):
        try:
            if current_message_tag in message_data:
                original_input = message_data[current_message_tag]
                self.user_input_entry.delete(0, tk.END)
                self.user_input_entry.insert(0, original_input)
                self.user_input_entry.focus()
                self.status_label.config(text="Message loaded into input box")
                self.root.after(2000, lambda: self.status_label.config(text=""))
        except Exception as e:
            print(f"Send again error: {e}")

    def delete_message(self):
        try:
            if current_message_tag:
                self.chat_box.config(state=tk.NORMAL)
                tag_ranges = self.chat_box.tag_ranges(current_message_tag)
                start_index = tag_ranges[0]
                end_index = tag_ranges[1]
                self.chat_box.delete(start_index, end_index)
                if current_message_tag in message_data:
                    del message_data[current_message_tag]
                self.status_label.config(text="Message deleted")
                self.root.after(2000, lambda: self.status_label.config(text=""))
                self.chat_box.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Delete error: {e}")

    def select_text(self):
        try:
            if current_message_tag and current_message_tag.startswith("bot_msg_"):
                tag_ranges = self.chat_box.tag_ranges(current_message_tag)
                start_index = tag_ranges[0]
                end_index = tag_ranges[1]
                message_text = self.chat_box.get(start_index, end_index).strip()

                select_window = tk.Toplevel(self.root)
                select_window.title("Select Text")
                select_window.geometry("400x300")
                select_window.configure(bg=COLORS["card"])
                select_window.transient(self.root)
                select_window.grab_set()

                select_text_box = scrolledtext.ScrolledText(select_window, wrap=tk.WORD,
                                                            font=("Segoe UI", 11), bg=COLORS["card"],
                                                            fg=COLORS["text_primary"], bd=0,
                                                            insertbackground=COLORS["text_primary"],
                                                            selectbackground=COLORS["primary"],
                                                            padx=10, pady=10)
                select_text_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                select_text_box.insert(tk.END, message_text)
                select_text_box.config(state=tk.NORMAL)

                close_button = tk.Button(select_window, text="Close", font=("Segoe UI", 10, "bold"),
                                         command=select_window.destroy, bg=COLORS["primary"],
                                         fg="white", activebackground=COLORS["secondary"],
                                         activeforeground="white", bd=0, padx=15, pady=5, relief="flat")
                close_button.pack(pady=10)

                select_window.update_idletasks()
                width = select_window.winfo_width()
                height = select_window.winfo_height()
                x = (select_window.winfo_screenwidth() // 2) - (width // 2)
                y = (select_window.winfo_screenheight() // 2) - (height // 2)
                select_window.geometry(f"{width}x{height}+{x}+{y}")

        except Exception as e:
            print(f"Select text error: {e}")

    def create_gradient(self, canvas, color1, color2):
        canvas.update()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
        r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]

        steps = height // 2

        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y_start = i * 2
            canvas.create_rectangle(0, y_start, width, y_start + 2, fill=color, outline="")

    def create_animations(self):
        self.typing_animation_index = 0
        self.typing_animation_text = "Your Intelligent Conversation Partner Aditya AI Chatbot"
        self.typing_animation()

    def button_hover(self, button, hover_color):
        button.config(bg=hover_color, relief="raised")

    def button_leave(self, button, normal_color):
        button.config(bg=normal_color, relief="flat")

    def button_click_animation(self, button):
        original_bg = button.cget("bg")
        button.config(bg=COLORS["accent"])
        self.root.after(100, lambda: button.config(bg=original_bg))

    def button_hover_canvas(self, hover_color):
        self.arrow_canvas.itemconfig(self.arrow_circle, fill=hover_color)

    def button_leave_canvas(self, normal_color):
        self.arrow_canvas.itemconfig(self.arrow_circle, fill=normal_color)

    def button_click_animation_canvas(self):
        self.arrow_canvas.itemconfig(self.arrow_circle, fill=COLORS["accent"])
        self.root.after(100, lambda: self.arrow_canvas.itemconfig(self.arrow_circle, fill=COLORS["primary"]))

    def typing_animation(self):
        if self.typing_animation_index < len(self.typing_animation_text):
            self.tagline_label.config(text=self.typing_animation_text[:self.typing_animation_index + 1])
            self.typing_animation_index += 1
            self.root.after(100, self.typing_animation)

    def clear_placeholder(self):
        if self.initial_input_entry.get() == "What's on your mind?":
            self.initial_input_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.bind('<Return>', app.get_response)
    root.mainloop()