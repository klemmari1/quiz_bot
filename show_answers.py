import pickle
from os import path


ANSWER_FILE = "answers.pkl"


if path.isfile(ANSWER_FILE):
    with open(ANSWER_FILE, "rb") as answer_file:
        print(pickle.load(answer_file))
else:
    print()
