# time python3 calculateAverage.py
import os
from gc import disable as gc_disable, enable as gc_enable
import multiprocessing as mp
from contextlib import contextmanager
import time
WORD = "ära"

@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} seconds")


def get_file_chunks(
    file_name: str,
    max_cpu: int = 8,
) -> tuple[int, list[tuple[str, int, int]]]:
    """Split flie into chunks"""
    cpu_count = min(max_cpu, mp.cpu_count())

    file_size = os.path.getsize(file_name)
    chunk_size = file_size // cpu_count

    start_end = list()
    with open(file_name, encoding="utf-8", mode="r") as f:

        def is_new_line(position):
            if position == 0:
                return True
            else:
                f.seek(position - 1)
                return f.read(1) == "\n"

        def next_line(position):
            f.seek(position)
            f.readline()
            return f.tell()

        chunk_start = 0
        while chunk_start < file_size:
            chunk_end = min(file_size, chunk_start + chunk_size)

            while not is_new_line(chunk_end):
                chunk_end -= 1

            if chunk_start == chunk_end:
                chunk_end = next_line(chunk_end)

            start_end.append(
                (
                    file_name,
                    chunk_start,
                    chunk_end,
                )
            )

            chunk_start = chunk_end

    return (
        cpu_count,
        start_end,
    )


def _process_file_chunk(
    file_name: str,
    chunk_start: int,
    chunk_end: int,
) -> dict:
    """Process each file chunk in a different process"""
    result = dict()
    with open(file_name, encoding="utf-8", mode="r") as f:
        f.seek(chunk_start)
        gc_disable()
        for line in f:
            chunk_start += len(line)
            if chunk_start > chunk_end:
                break
            c1, c2, c3, c4 = line.split("\t")
            result[c1] = int(c3) if not result.get(c1) else result.get(c1) + int(c3)

        gc_enable()
    return result


def process_file(
    cpu_count: int,
    start_end: list,
) -> dict:
    """Process data file"""
    with mp.Pool(cpu_count) as p:
        # Run chunks in parallel
        chunk_results = p.starmap(
            _process_file_chunk,
            start_end,
        )

    # # Combine all results from all chunks
    result = dict()
    for chunk_result in chunk_results:
        for idx, count in chunk_result.items():
            result[idx] = count if not result.get(idx) else result.get(idx) + count

    # Print final results
    print("Total words: ", len(result))
    print("Total count for word : ", result.get(WORD))


if __name__ == "__main__":
    with timer("calculateAverage MP calculation"):
        cpu_count, *start_end = get_file_chunks("./googlebooks-eng-all-1gram-20120701-a")
        process_file(cpu_count, start_end[0])

    print("=====================================")
