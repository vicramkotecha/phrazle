import random

class LetterValidator:
    def __init__(self, letter_counts, vowels):
        self.letter_counts = letter_counts.copy()
        self.vowels = vowels
        self.original_total = sum(letter_counts.values())
        self.excess_letters = 0

    def validate(self) -> dict:
        """Validate and balance letter distribution."""
        self._limit_consonants()
        self._ensure_min_vowels()
        self._redistribute_excess()
        assert sum(self.letter_counts.values()) == self.original_total
        return self.letter_counts

    def _limit_consonants(self):
        for letter, count in self.letter_counts.items():
            if letter not in self.vowels and count > 3:
                self.excess_letters += count - 3
                self.letter_counts[letter] = 3

    def _ensure_min_vowels(self):
        total_vowels = sum(self.letter_counts.get(v, 0) for v in self.vowels)
        vowels_needed = max(0, 3 - total_vowels)

        # Use excess consonants first
        while vowels_needed > 0 and self.excess_letters > 0:
            vowel = random.choice(list(self.vowels))
            self.letter_counts[vowel] = self.letter_counts.get(vowel, 0) + 1
            vowels_needed -= 1
            self.excess_letters -= 1

        # If still need vowels, remove consonants
        while vowels_needed > 0:
            reducible = [
                (l, c)
                for l, c in self.letter_counts.items()
                if l not in self.vowels and c > 0
            ]
            if not reducible:
                break
            letter, _ = random.choice(reducible)
            self.letter_counts[letter] -= 1
            vowel = random.choice(list(self.vowels))
            self.letter_counts[vowel] = self.letter_counts.get(vowel, 0) + 1
            vowels_needed -= 1

    def _redistribute_excess(self):
        while self.excess_letters > 0:
            letter = random.choice(list(self.letter_counts.keys()))
            self.letter_counts[letter] += 1
            self.excess_letters -= 1 