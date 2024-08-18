import re
import tkinter as tk
from tkinter import ttk


# Function to style emojis in the message
def style_emojis(message):
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F]|"  # emoticons
        "[\U0001F300-\U0001F5FF]|"  # symbols & pictographs
        "[\U0001F680-\U0001F6FF]|"  # transport & map symbols
        "[\U0001F1E0-\U0001F1FF]"  # flags (iOS)
        "+", flags=re.UNICODE)

    styled_message = ""
    last_end = 0
    for match in emoji_pattern.finditer(message):
        start, end = match.span()
        # Add normal text
        styled_message += message[last_end:start]
        # Add emoji with styling
        styled_message += f"{{emoji:{message[start:end]}}}"
        last_end = end
    # Add the remaining part of the message
    styled_message += message[last_end:]

    return styled_message


# Function to display the styled message in the chat
def display_message(chat, message):
    styled_message = style_emojis(message)
    parts = styled_message.split("{emoji:")
    for part in parts:
        if "}" in part:
            emoji, rest = part.split("}", 1)
            chat.insert(tk.END, emoji, "emoji")
            chat.insert(tk.END, rest)
        else:
            chat.insert(tk.END, part)
    chat.insert(tk.END, "\n")
    chat.see(tk.END)


# Example usage with tkinter
def main():
    root = tk.Tk()
    root.title("School Chat")

    chat_frame = ttk.Frame(root)
    chat_frame.pack(fill=tk.BOTH, expand=True)

    chat = tk.Text(chat_frame, wrap=tk.WORD)
    chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    chat.tag_configure("emoji", foreground="red")  # Example styling for emojis

    # Example messages
    messages = [
        "Hello 😊",
        "How are you? 😃",
        "I'm good, thanks! 🚀"
    ]

    for msg in messages:
        display_message(chat, msg)

    root.mainloop()


if __name__ == "__main__":
    main()
