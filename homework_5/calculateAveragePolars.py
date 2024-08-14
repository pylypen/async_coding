import polars as pl
from contextlib import contextmanager
import time


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} seconds")


with timer('Polars calculation'):
    # Read data file
    df = pl.scan_csv('./googlebooks-eng-all-1gram-20120701-a', separator='\t', has_header=False)

    # df_csv = pl.read_csv("docs/data/output.csv")
    # df.select(pl.col("column_1")).unique().collect()
    data = df.select(pl.col("column_1")).unique().collect()
    all_words = data.to_dict(as_series=False).get('column_1')
    # .select(pl.col("column_4").value_counts())
    data = df.filter(pl.col("column_1") == 'ära').select(pl.col("column_3")).collect()
    ara_words = data.to_dict(as_series=False).get('column_3')

    print("Total words: ", len(all_words))
    print("Total count for word : ", sum(ara_words))

print("=====================================")

