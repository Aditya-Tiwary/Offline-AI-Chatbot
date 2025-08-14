# Aditya AI Assistant
Hello, I aimed the project to be a book of knowledge for people in remote areas with no access to the internet a knowledge base that lives on your laptop. However, I discontinued it due to slow response times for simple prompts (around 10 minutes) and a limited knowledge base. In the future, more powerful PCs may make such projects more feasible.
<div align="center">
  <img src="gif/logo.gif" alt="Aditya AI Logo" width="150">
</div>

An offline, privacy-focused AI chatbot built with Python, Tkinter, and powered by the DeepSeek-R1:8b model from Ollama. This application allows users to have natural language conversations with an AI assistant without requiring an internet connection. All data stays on your local device.

This project was developed as a college project for MCA Semester 4 but was discontinued. It is designed to run on modest hardware, including systems with Radeon Integrated Graphics (512MB VRAM) and 8GB RAM, with an average response time of approximately 10 minutes for simple prompts.

## Features

- **Offline Operation**: Runs entirely locally using Ollama – no internet or cloud services needed.
- **Privacy-First**: No data is sent externally; everything stays on your device.
- **Unlimited Conversation Depth**: No context limits for ongoing chats.
- **Modern GUI**: Built with Tkinter, featuring animated elements, gradient backgrounds, and a responsive interface.
- **Conversation Management**:
  - Save chats as PDF with formatted export.
  - Regenerate responses.
  - Clear chat history.
  - Stop ongoing responses.
- **Message Interactions**: Right-click messages to copy, delete, resend, or select text.
- **Formatting Support**: Handles bold, headers, lists, quotes, and code blocks in responses.
- **Animated Elements**: Includes loading GIFs and animated logo.
- **Customizable Themes**: Predefined color scheme for a sleek look.

Key Highlights:
- Natural language processing for human-like conversations.
- Supports starting chats with an initial prompt.
- Timestamped messages for better tracking.

## Screenshots

### Welcome Screen
<img width="1920" height="1026" alt="image" src="https://github.com/user-attachments/assets/ed0c9f56-f5bb-46a3-bdec-72eabed2a013" />
<img width="1920" height="1030" alt="{611175C2-D19D-4CA5-A9DE-D0000BBC5635}" src="https://github.com/user-attachments/assets/18a5eb4f-2612-418b-b8c4-d2a34927efdf" />


### Chat Interface
<img width="1920" height="1033" alt="{926FE561-4C49-426C-86C9-CB43602434F5}" src="https://github.com/user-attachments/assets/f7f31f0d-c5bc-4231-893d-900b7367fd30" />



### PDF Export Example
<img width="1920" height="1079" alt="{0E098830-6FA2-4AE6-AC75-C67F3BA91D22}" src="https://github.com/user-attachments/assets/8d6e6889-711d-4dbe-9bdf-d5e4d412f78a" />


## Installation

### Prerequisites
- Python 3.8+ (tested on Python 3.12)
- Ollama installed (download from [ollama.com](https://ollama.com))
- DeepSeek-R1:8b model (run `ollama run deepseek-r1:8b` to download and install)
- Minimum hardware: Radeon Integrated Graphics (512MB VRAM), 8GB RAM

### Dependencies
Install required Python libraries:
```
pip install tkinter reportlab pillow ollama
```
Note: Tkinter is usually included with Python installations. Other libraries like `subprocess`, `threading`, `re`, `datetime`, and `os` are standard.

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Offline-AI-Chatbot.git
   cd Offline-AI-Chatbot
   ```

2. Ensure paths to GIFs and icons are correct (e.g., update absolute paths in `main.py` to relative ones if needed).

3. Run the starter script to initialize Ollama (if not already running):
   ```
   python start.py
   ```

4. Launch the application:
   ```
   python main.py
   ```

## Usage

1. **Start the App**: Run `python main.py`. You'll see the welcome screen with project details and instructions.
2. **Begin Chatting**:
   - Click "Start Chatting" to enter the input screen.
   - Type your initial message and press Enter or click the arrow button.
3. **Interact**:
   - Send messages via the input box.
   - Use buttons for Regenerate, Clear Chat, Stop, or Save as PDF.
   - Right-click on messages for options like Copy, Delete, or Resend.
4. **Export Chat**: Click "Save as PDF" to generate a formatted PDF of the conversation.
5. **Stop/Regenerate**: Control ongoing responses or retry the last user message.

The app auto-generates a conversation name based on the first user prompt for better organization. Note that response times average around 10 minutes for simple prompts due to the offline processing on modest hardware.

## Project Structure

- `main.py`: Core application script with GUI and logic.
- `start.py`: Helper script to run Ollama model.
- `gif/`: Directory for animated GIFs (logo.gif, loading.gif).
- `icons/`: Directory for feature icons (offline.png, privacy.png, etc.).

## Project Status

This was a college project developed for MCA Semester 4 but was discontinued. It remains functional for educational purposes or as a starting point for further development.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

© 2025 Aditya Tiwary - All Rights Reserved.
