import subprocess

def run_ollama_command():
    try:
        # Command to run in cmd
        command = "ollama run deepseek-r1:8b"
        
        # Run the command in cmd
        subprocess.run(command, shell=True, check=True)
        
        print("Command executed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def main():
    run_ollama_command()

if __name__ == "__main__":
    main()

    #Put in main.py
    #import start
#start.main()