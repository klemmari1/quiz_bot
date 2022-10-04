import random

WORD_FILE = "words"
WORDS = open(WORD_FILE).read().splitlines()


WAIT_FOR_VERIFICATION_CODE_SECONDS = 60


def get_random_word():
    while True:
        random_word = random.choice(WORDS)
        if "'s" not in random_word:
            break
    return random_word.capitalize()
