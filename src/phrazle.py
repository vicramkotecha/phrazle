import itertools
import random

import language_tool_python
import numpy as np
from requests import get

import dictionary
from letter_validator import LetterValidator


class Phrazle:
    def __init__(self):
        self._solution_cache: dict = {}
        self._valid_words_cache: dict = {}
        self.dictionary = dictionary.word_list
        self.tool = language_tool_python.LanguageTool("en-US")
        self.vowels = {"A", "E", "I", "O", "U", "Y"}
        self.letters = self.generate_letters()

    MAX_SOLUTIONS = 5
    MAX_WORD_LENGTH = 8
    MAX_WORDS_TO_TRY = 20

    def generate_letters(self, num_letters=8):
        words = self.dictionary
        # concatenate all words in the dictionary
        all_words = "".join(words).upper()
        # find letter frequency
        sorted_words = sorted(all_words)
        letter_counts = {}
        for letter in sorted_words:
            if letter.isalpha():
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
        # get the most common letters
        most_common_letters = sorted(
            letter_counts, key=letter_counts.get, reverse=True
        )[:num_letters]
        letters = random.choices(
            most_common_letters,
            k=num_letters,
            weights=[letter_counts[letter] for letter in most_common_letters],
        )
        letter_counts = {letter: letters.count(letter) for letter in letters}
        # Apply validations
        validator = LetterValidator(letter_counts, self.vowels)
        letter_counts = validator.validate()
        solutions = []
        while not solutions:
            solutions = self.get_solutions(letter_counts)
            if len(solutions) == 0:
                # draw another letter
                new_letter = random.choices(
                    most_common_letters,
                    k=1,
                    weights=[letter_counts[letter] for letter in most_common_letters],
                )[0]
                letter_counts[new_letter] = letter_counts.get(new_letter, 0) + 1
        return letter_counts

    def get_solutions(self, letter_counts, words=None, max_words=4):
        letters_key = tuple(sorted(letter_counts.items()))
        words_key = tuple(words) if words else None
        cache_key = (letters_key, words_key)

        if cache_key in self._solution_cache:
            return self._solution_cache[cache_key]

        # Early termination conditions
        if words and len(words) >= max_words:  # Limit phrase length
            return []

        if all(count == 0 for count in letter_counts.values()):
            if words and not self.tool.check(" ".join(words)):
                # Only cache and return if it's a valid grammatical phrase
                # that uses all letters
                self._solution_cache[cache_key] = [words]  # Wrap words in list
                return [words]
            return []
        elif any(count < 0 for count in letter_counts.values()):
            return []

        # Minimum letters check - if remaining letters are too few, terminate
        remaining_letters = sum(letter_counts.values())
        if remaining_letters < 2:  # Need at least 2 letters for a valid word
            return []

        words = words or []
        possible_words = self._get_valid_words(letter_counts)

        # Sort words by length to prioritize longer words
        possible_words = sorted(possible_words, key=len, reverse=True)

        # Limit the number of words to try
        possible_words = possible_words[:self.MAX_WORDS_TO_TRY]

        valid_solutions = []
        for word in possible_words:
            leftover_letters = self._subtract_word_letters(letter_counts, word)
            result = self.get_solutions(leftover_letters, [word] + words, max_words)
            if result:
                valid_solutions.extend(result)
                if len(valid_solutions) >= self.MAX_SOLUTIONS:
                    break

        self._solution_cache[cache_key] = valid_solutions
        return valid_solutions

    def _get_valid_words(self, letter_counts):
        letters_key = tuple(sorted(letter_counts.items()))

        if letters_key in self._valid_words_cache:
            return self._valid_words_cache[letters_key]

        possible_words = set()
        total_letters = sum(letter_counts.values())

        for word in self.dictionary:
            # Skip words that are too long
            if len(word) > total_letters:
                continue

            word = word.strip().upper()
            # More aggressive filtering of short words
            if len(word) == 1 and word not in {"A", "I"}:
                continue
            if len(word) == 2 and not any(letter in self.vowels for letter in word):
                continue
            if len(word) > 8:  # Skip very long words
                continue

            if self._can_make_word(word, letter_counts):
                possible_words.add(word)

        self._valid_words_cache[letters_key] = possible_words
        return possible_words

    def _can_make_word(self, word, letter_counts):
        """Check if a word can be made from the given letters."""
        available_letters = letter_counts.copy()
        for char in word:
            if char not in available_letters or available_letters[char] <= 0:
                return False
            available_letters[char] -= 1
        return True

    def _subtract_word_letters(self, letter_counts, word):
        """Subtract the letters used in a word from the available letters."""
        result = letter_counts.copy()
        for char in word:
            result[char] -= 1
        return result

    def validate_phrase(self, phrase, letter_counts):
        # Check letter usage
        available_letters = letter_counts.copy()
        for char in phrase.replace(" ", "").upper():
            if char not in available_letters or available_letters[char] <= 0:
                return False, f"Invalid letter usage: '{char}' not allowed or overused."
            available_letters[char] -= 1
        # Make sure all letters are used
        if any(count > 0 for count in available_letters.values()):
            return False, "Not all letters used."

        # Grammar check
        matches = self.tool.check(phrase)
        if matches:
            return False, f"Grammar issue: {matches[0].message}"

        return True, "Valid phrase!"

    def phrazle_game(self):
        print("Welcome to Phrazle!")
        letter_counts = self.generate_letters()
        
        self._display_letters(letter_counts)
        self._display_instructions()
        
        while True:
            user_input = input("> ").strip()
            if user_input.lower() == "exit":
                print("Thanks for playing Phrazle!")
                break
            
            self._process_user_input(user_input, letter_counts)

    def _display_letters(self, letter_counts):
        print("\nYour letters:")
        letters_display = ''.join(letter * count for letter, count in letter_counts.items())
        print(letters_display)

    def _display_instructions(self):
        print("\nCreate a phrase using these letters, exactly as provided.")
        print("Type 'exit' to quit.\n")

    def _process_user_input(self, user_input, letter_counts):
        is_valid, message = self.validate_phrase(user_input, letter_counts)
        print(f"{'✅' if is_valid else '❌'} {message}")


# Entry point
if __name__ == "__main__":
    Phrazle().phrazle_game()
