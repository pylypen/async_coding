import asyncio
import time
import multiprocessing as mp
from contextlib import contextmanager
from itertools import batched
from concurrent.futures import ProcessPoolExecutor
from functions import mp_count_words


FILE_PATH = "./googlebooks-eng-all-1gram-20120701-a"
WORD = "ära"


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} seconds")


def reduce_words(target: dict, source: dict) -> dict:
    for key, value in source.items():
        if key in target:
            target[key] += value
        else:
            target[key] = value
    return target


async def monitoring(counter, counter_lock, total):
    interval_seconds = 5  # can be adjusted

    while True:
        # with counter_lock:
        if counter.value == total:
            break
        await asyncio.sleep(interval_seconds)


async def main():
    loop = asyncio.get_event_loop()

    words = {}
    with open(FILE_PATH, "r") as file:
        data = file.readlines()

    batch_size = 60_000  # can be adjusted

    with mp.Manager() as manager:
        counter = manager.Value("i", 0)
        counter_lock = manager.Lock()

        monitoring_task = asyncio.shield(
            asyncio.create_task(monitoring(counter, counter_lock, len(data)))
        )

        with ProcessPoolExecutor() as executor:
            results = []
            for batch in batched(data, batch_size):
                results.append(
                    loop.run_in_executor(
                        executor,
                        mp_count_words,
                        batch,
                        counter,
                        counter_lock,
                    )
                )

            done, _ = await asyncio.wait(results)

        monitoring_task.cancel()

    for result in done:
        words = reduce_words(words, result.result())

    print("Total words: ", len(words))
    print("Total count for word : ", words[WORD])


if __name__ == "__main__":
    with timer("main_old_version MP calculation"):
        asyncio.run(main())

    print("=====================================")
