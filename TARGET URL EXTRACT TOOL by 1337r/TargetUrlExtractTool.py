import os
import ctypes
import win32api
import re
import traceback
import sys
from multiprocessing import Pool, cpu_count

MAX_PROCESSES = cpu_count() // 1  
PROGRAM_TITLE = "Target URL Extractor by 1337r" 



def set_console_size(width, height):
    """
    Set the size and position of the console window.
    """
    try:
        kernel32 = ctypes.WinDLL('kernel32.dll')
        user32 = ctypes.WinDLL('user32.dll')

        # Get the handle to the console window
        console_handle = kernel32.GetConsoleWindow()

        # Get the screen resolution
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        # Calculate the position to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the new window size and position
        user32.MoveWindow(console_handle, x, y, width, height, True)
    except Exception as e:
        print(f"Error setting console size and position: {str(e)}")

# Set the console window size (width, height) and position
set_console_size(500, 300)










def set_console_title(title):
    """
    Set the console window title.
    """
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception as e:
        log_error(f"Error setting console title: {str(e)}")

def extract_target(args):
    try:
        file_path, targets = args
        matches = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            for target in targets:
                # Escape special characters in the target
                escaped_target = re.escape(target)

                # Use a pattern to match the target in the full line
                pattern = re.compile(r'^(.*)(%s)(.*)$' % escaped_target, re.IGNORECASE)

                matches[target] = []
                for line in text.splitlines():
                    match = pattern.search(line)
                    if match:
                        matches[target].append(match.group(0))  # Append the full line

        return matches
    except Exception as e:
        log_error(f"Error extracting targets from file '{file_path}': {str(e)}")
        return {}

def main():
    try:
        # Get the current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the input folder path
        input_folder_path = os.path.join(script_dir, 'input')

        # Check if the input folder exists
        if not os.path.isdir(input_folder_path):
            log_error(f"The 'input' folder was not found in {script_dir}. Please create the folder and add text files.")
            return

        targets = input("Search URLS (example, example) -> ").split(',')
        targets = [target.strip() for target in targets]

        file_paths = []
        for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                if file.endswith(('.txt', '.pass')):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)

        print(f"Checking {len(file_paths)} files...")

        with Pool(processes=MAX_PROCESSES) as pool:
            args = [(file_path, targets) for file_path in file_paths]
            results = pool.map(extract_target, args)
            all_targets = {target: [] for target in targets}
            for result in results:
                for target, matches in result.items():
                    all_targets[target].extend(matches)

        for target, matches in all_targets.items():
            if matches:
                output_file_path = os.path.join(script_dir, f'found_{target}.txt')
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write('\n'.join(matches))
                print(f"Extracted targets for '{target}' saved to {output_file_path}")

                # Remove duplicates from found_{target}.txt
                with open(output_file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                unique_lines = list(set(lines))
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    file.writelines(unique_lines)
                print(f"Removed duplicates from {output_file_path}")
            else:
                print(f"No occurrences of '{target}' found in the input files.")
    except Exception as e:
        log_error(f"Error in main function: {str(e)}")

def log_error(message):
    try:
        with open('ignore.txt', 'a', encoding='utf-8') as debug_file:
            debug_file.write(f"{message}\n")
            traceback.print_exc(file=debug_file)
    except Exception as e:
        print(f"Error logging to debug.txt: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        # Set the console window title
        set_console_title(PROGRAM_TITLE)
        main()
    except Exception as e:
        log_error(f"Unhandled exception: {str(e)}")
        sys.exit(1)
