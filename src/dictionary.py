import os
import requests

DICTIONARY_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
OUTPUT_FILE_PATH = "data/dictionary.txt"

def load_dictionary(file_path: str) -> list:
    try:
        with open(file_path, 'r') as file:
            words = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(words)} words.")
        return words
    except FileNotFoundError:
        print(f"Dictionary file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return []

def download_dictionary(url, output_file):
    if os.path.exists(output_file):
        print(f"Dictionary already exists at {output_file}")
        return
    try:
        print("Downloading dictionary...")
        response = requests.get(url)
        response.raise_for_status()
        with open(output_file, 'wb') as file:
            file.write(response.content)
        print(f"Dictionary saved to {output_file}")
    except requests.RequestException as e:
        print(f"Error downloading dictionary: {e}")

# Download the dictionary if needed
download_dictionary(DICTIONARY_URL, OUTPUT_FILE_PATH)

# Load dictionary at module level
word_list = load_dictionary(OUTPUT_FILE_PATH)

if __name__ == "__main__":
    # Can keep this for testing
    print(f"Loaded {len(word_list)} words directly.")
