from contextlib import contextmanager
import time


FILE_PATH = "./googlebooks-eng-all-1gram-20120701-a"
WORD = "ära"


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} seconds")


words = {}

with open(FILE_PATH, "r") as file:
    data = file.readlines()

with timer("main_one calculation"):
    for line in data:
        _word, _, match_count, _ = line.split("\t")
        words[_word] = words.get(_word, 0) + int(match_count)

    print("Total words: ", len(words))
    print("Total count for word : ", words[WORD])
print("=====================================")

