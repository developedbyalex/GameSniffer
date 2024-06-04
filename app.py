import time
import re
import os
import random
import json
from datetime import datetime, timedelta
from art import text2art
from pynput.keyboard import Key, Listener
import enchant
from itertools import permutations
import pyautogui

CHAT_LOG_PATH = r'PATH_TO_LATEST.LOG'
JSON_FILE_PATH = 'typed_words.json'

# Regular expressions to match the specific phrases
SOLVE_REGEX = re.compile(r'First one to solve (.*)', re.IGNORECASE)
TYPE_REGEX = re.compile(r'First one to type (\w+)', re.IGNORECASE)
UNSCRAMBLE_REGEX = re.compile(r'First one to unscramble (\w+)', re.IGNORECASE)

running = True
dictionary = enchant.Dict("en_US")
mode = None

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def tail_log(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        file.seek(0, os.SEEK_END)
        while running:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                file.seek(file.tell())
                continue
            yield line

def solve_equation(equation):
    try:
        answer = eval(equation)
        return answer
    except Exception:
        return None

def unscramble_word(scrambled_word):
    for perm in permutations(scrambled_word):
        word = ''.join(perm)
        if dictionary.check(word):
            return word
    return None

def type_in_minecraft(text):
    time.sleep(random.uniform(1.5, 2.0))
    pyautogui.typewrite(text)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('t')

def record_word(word):
    try:
        if os.path.exists(JSON_FILE_PATH):
            with open(JSON_FILE_PATH, 'r') as file:
                data = json.load(file)
        else:
            data = {"words": []}

        for entry in data["words"]:
            if entry["word"] == word:
                entry["count"] += 1
                with open(JSON_FILE_PATH, 'w') as file:
                    json.dump(data, file, indent=4)
                print(f" - Added +1 count to word {word}.")
                return

        data["words"].append({"word": word, "count": 1})
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print(f" - NEW WORD! Added to json and set count to 1.")
    except Exception as e:
        print(f"Error recording word: {e}")

def countdown(seconds):
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        print(f"👀 Watching... (next game expected in {time_format})", end='\r', flush=True)
        time.sleep(1)
        seconds -= 1

def monitor_log():
    print("👀 Searching...", end='\r', flush=True)
    try:
        for line in tail_log(CHAT_LOG_PATH):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            solve_match = SOLVE_REGEX.search(line)
            if solve_match:
                equation = solve_match.group(1)
                answer = solve_equation(equation)
                if answer is not None:
                    result = f"{equation} = {answer}"
                    print(f"\r🎉 Equation found ({result}) {timestamp}", flush=True)
                    record_word(str(answer))
                    if mode == '2':
                        type_in_minecraft(str(answer))
                        countdown(420)  
                continue

            type_match = TYPE_REGEX.search(line)
            if type_match:
                word = type_match.group(1)
                print(f"\r🎉 Word found ({word}) {timestamp}", flush=True)
                record_word(word)
                if mode == '2':
                    type_in_minecraft(word)
                    countdown(420) 
                continue

            unscramble_match = UNSCRAMBLE_REGEX.search(line)
            if unscramble_match:
                scrambled_word = unscramble_match.group(1)
                unscrambled_word = unscramble_word(scrambled_word)
                if unscrambled_word:
                    result = f"{scrambled_word} -> {unscrambled_word}"
                    print(f"\r🎉 Unscramble word found ({result}) {timestamp}", flush=True)
                    record_word(unscrambled_word)
                    if mode == '2':
                        type_in_minecraft(unscrambled_word)
                        countdown(420) 
                else:
                    print(f"\r🎉 Unscramble word found ({scrambled_word} -> No valid word found) {timestamp}", flush=True)
                continue

            print("👀 Searching...", end='\r', flush=True)
            time.sleep(0.1)

    except FileNotFoundError:
        print(f"File not found: {CHAT_LOG_PATH}")
    except Exception as e:
        print(f"Error reading log file: {e}")

def on_press(key):
    global running
    try:
        if key == Key.delete:
            print("\rDEL key pressed. Exiting...")
            running = False
            return False
    except AttributeError:
        pass

if __name__ == "__main__":
    clear_console()

    # Display ASCII art and program details
    ascii_art = text2art("GameSniffer")
    print(ascii_art)
    print("Made by Rooftop")
    print()

    # Check for JSON file
    print("Checking for .json file...")
    if os.path.exists(JSON_FILE_PATH):
        print("json file found")
    else:
        print("json file not found. Creating one")
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump({"words": []}, file, indent=4)

    time.sleep(1)
    clear_console()

    # Display ASCII art and mode selection
    print(ascii_art)
    print("Made by Rooftop")
    print("\nChoose a mode below:\n")
    print("[1] Passive mode (word collection)")
    print("[2] AFK Mode\n")
    mode = input("Enter the mode number: ").strip()

    clear_console()
    print(ascii_art)
    print("Made by Rooftop")
    print(f"Running in {'Passive Mode' if mode == '1' else 'AFK Mode'}")

    listener = Listener(on_press=on_press)
    listener.start()

    monitor_log()
    listener.join()
