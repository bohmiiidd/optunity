#/usr/bin/python3

import os
import sys
import time
import requests
import json
from threading import Thread
from plyer import notification
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def daemonize():
    if os.fork() > 0:
        # Exit from the parent process
        sys.exit()

    os.setsid()
    if os.fork() > 0:
        # Exit from the first child process
        sys.exit()

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "wb", 0) as null_file:
        os.dup2(null_file.fileno(), sys.stdin.fileno())
        os.dup2(null_file.fileno(), sys.stdout.fileno())
        os.dup2(null_file.fileno(), sys.stderr.fileno())



# Function to get the size and content of a webpage
def get_page_size_and_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        size = len(content)
        return size, content, response.status_code, response.headers
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error fetching the page: {e}")
        return None, None, None, None

# Function to send a graphical notification
def send_notification(message):
    notification.notify(
        title="Website Monitor Alert",
        message=message,
        app_name="Website Monitor",
        timeout=10
    )

# Function to save content to a file
def save_content_to_file(url, content):
    filename = f"page_change_{url.replace('://', '_').replace('/', '_')}.html"
    file_path = os.path.join("logs", filename)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    return file_path

# Main function to monitor the websites
def monitor_websites_from_json(file_path, interval=3):
    try:
        with open(file_path, 'r') as file:
            websites = json.load(file)
            if not isinstance(websites, list):
                raise ValueError("JSON file must contain a list of URLs.")
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        print(f"{Fore.RED}Error reading JSON file: {e}")
        return

    print(f"{Fore.GREEN}Monitoring websites every {interval} seconds...{Style.RESET_ALL}")
    prev_sizes = {url: None for url in websites}

    def monitor():
        while True:
            for url in websites:
                print(f"\n{Fore.CYAN}--- Checking {url} ---{Style.RESET_ALL}")
                size, content, status_code, headers = get_page_size_and_content(url)

                if size is None:
                    continue

                if prev_sizes[url] is None:
                    prev_sizes[url] = size
                    print(f"{Fore.GREEN}Initial page size for {url}: {size} bytes{Style.RESET_ALL}")
                elif size != prev_sizes[url]:
                    send_notification(f"Page size for {url} changed from {prev_sizes[url]} to {size} bytes!")

                    # Save the page content in the current directory
                    file_path = save_content_to_file(url, content)
                    send_notification(f"{Fore.GREEN}Saved updated page for {url} to {file_path}{Style.RESET_ALL}")

                    prev_sizes[url] = size

            time.sleep(interval)

    monitor_thread = Thread(target=monitor, daemon=True)
    monitor_thread.start()

    print(f"\n{Fore.CYAN}Process running in background with PID: {os.getpid()}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}To stop the process, use the command: kill -9 {os.getpid()}{Style.RESET_ALL}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Monitoring stopped by user.{Style.RESET_ALL}")


def banner():
    print(f"""\n{Fore.CYAN}
                     █████                           ███   █████              
                    ░░███                           ░░░   ░░███               
  ██████  ████████  ███████   █████ ████ ████████   ████  ███████   █████ ████
 ███░░███░░███░░███░░░███░   ░░███ ░███ ░░███░░███ ░░███ ░░░███░   ░░███ ░███ 
░███ ░███ ░███ ░███  ░███     ░███ ░███  ░███ ░███  ░███   ░███     ░███ ░███ 
░███ ░███ ░███ ░███  ░███ ███ ░███ ░███  ░███ ░███  ░███   ░███ ███ ░███ ░███ 
░░██████  ░███████   ░░█████  ░░████████ ████ █████ █████  ░░█████  ░░███████ 
 ░░░░░░   ░███░░░     ░░░░░    ░░░░░░░░ ░░░░ ░░░░░ ░░░░░    ░░░░░    ░░░░░███ 
          ░███                                                       ███ ░███ 
          █████                                                     ░░██████  
         ░░░░░                                                       ░░░░░░   """)
    print(f"""\n{Fore.RED}
┌─┐┌─┐┬  ┬  ┌─┐┌─┐┌┬┐┌─┐┬─┐
│  │ ││  │  ├┤ │   │ ├┤ ├┬┘
└─┘└─┘┴─┘┴─┘└─┘└─┘ ┴ └─┘┴└─
by ₈₀₇""")
    print("For automation lookup use :$ python3 optunity.py --background ")


if __name__ == "__main__":
    banner()
    if "--background" in sys.argv:
        print(f"Process running in background with PID: {os.getpid()}")
        print("To stop the process, use the command: kill -9 PID")
        daemonize()
    json_file = "web_db.json"
    monitor_websites_from_json(json_file)
