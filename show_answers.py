import pickle
import pprint
from os import path

ANSWER_FILE = "answers.pkl"


if path.isfile(ANSWER_FILE):
    with open(ANSWER_FILE, "rb") as answer_file:
        pprint.pprint(pickle.load(answer_file))
