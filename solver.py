from dataclasses import dataclass
from random import choice
from string import ascii_lowercase
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from unidecode import unidecode


@dataclass
class Letter:
    char: str
    class_: str
    location: int


class Solver:
    _words_file = 'words.txt'  # change to 'possible_words.txt' to use only possible words instead of all the words in the portuguese language
    def __init__(self, driver: Chrome):
        self._driver = driver
        self._configure_driver()

        self._words = self._load_words()
        self._data = []

    def solve(self) -> bool:
        """
        Tries to find the word of the day. Returns wheter or not it succeeded.
        """
        for _ in range(6):
            word = self._choose_word()

            self._enter_word(word)

            sleep(1.3)

            self._update_data()

            if self._was_word_correct():
                return True

            if self._was_word_invalid():
                self._words.remove(word)
                self._delete_word()

        return False

    @property
    def word(self) -> str:
        """
        Returns the word of the day, if it could be identified.
        """
        if self._was_word_correct():
            return ''.join(letter.char for letter in self._data[-5:])

        return None

    @property
    def guesses(self) -> list[str]:
        """
        Returns the list of words that the solver guessed.
        If it succeeded in finding the word of the day, the last element of the list will be the same as the "word" property.
        """
        guesses = []
        number_of_words = len(self._data) // 5

        for i in range(number_of_words):
            start = i * 5
            end = (i + 1) * 5
            letters = self._data[start:end]

            guesses.append(
                ''.join(map(lambda letter: letter.char, letters))
            )

        return guesses

    def _update_data(self):
        elements = self._driver.find_elements(
            By.XPATH,
            '//*[@id="board"]/div/div'
        )

        new_data = []

        for index, element in enumerate(elements):
            class_ = element.get_attribute('class').split()[-1]
            char = unidecode(element.text.lower())

            if class_ == 'letter' or not char:
                continue

            letter = Letter(
                char,
                class_,
                index % 5
            )

            new_data.append(letter)

        self._data = new_data

    def _choose_word(self) -> str:
        if not self._data:
            return choice([
                word
                for word in self._words
                if len(set(word)) == len(word)
            ])

        self._filter_words()

        return choice(self._words)

    def _filter_words(self):
        right = self._filter_from_data('right')
        wrong = self._filter_from_data('wrong')
        place = self._filter_from_data('place')

        right_pred = lambda word: all(
            word[r.location] == r.char 
            for r in right
        )

        wrong_pred = lambda word: all(
            word[w.location] != w.char 
            for w in wrong
        )

        place_pred = lambda word: all(
            word[p.location] != p.char and p.char in word 
            for p in place
        )

        self._apply_predicates(
            right_pred,
            wrong_pred,
            place_pred
        )

    def _apply_predicates(self, *preds):
        for pred in preds:
            self._words = list(filter(pred, self._words))

    def _filter_from_data(self, class_name) -> list[Letter]:
        pred = lambda letter: letter.class_ == class_name

        return list(filter(pred, self._data))  # has to be a list for some reason

    def _enter_word(self, word: str):
        for char in word:
            self._click_element_by_xpath(f'//*[@id="kbd_{char}"]')

        self._click_element_by_xpath('//*[@id="kbd_enter"]')

    def _delete_word(self):
        for _ in range(5):
            self._click_element_by_xpath('//*[@id="kbd_backspace"]')

    def _was_word_invalid(self) -> bool:
        element = self._driver.find_element(
            By.XPATH,
            '//*[@id="msg"]'
        )

        return 'normal' in element.get_attribute('style')

    def _was_word_correct(self) -> bool:
        return self._data[-1].class_ == 'done'

    def _load_words(self) -> list[str]:
        with self._read_file(self._words_file) as file:
            converted_words = map(self._convert_word, file)

            filtered_words = filter(self._validate_word, converted_words)

            return list(filtered_words)

    def _convert_word(self, word):
        decoded = unidecode(word)
        return decoded.strip().lower()

    def _validate_word(self, word: str) -> bool:
        return len(word) == 5 and all(char in ascii_lowercase for char in word)

    def _read_file(self, filename):
        return open(
            file=filename,
            encoding='utf-8',
            mode='r'
        )

    def _click_element_by_xpath(self, xpath):
        self._driver.find_element(By.XPATH, xpath).click()

    def _configure_driver(self):
        self._driver.get('https://term.ooo/')
        self._click_element_by_xpath('//*[@id="help"]')
