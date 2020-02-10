import json
from pathlib import Path
from typing import List, Tuple

import typer
import pandas as pd


def main(source: str):
    with open(source) as f:
        data = json.load(f)

    sources: List[Tuple[int, str]] = []
    quotes: List[Tuple[str, int]] = []
    for key, val in data.items():
        source_id = len(sources)
        for row in val:
            quotes.append((str(row), source_id))
        sources.append((source_id, str(key)))

    print(f"# of quotes: {len(quotes)}")
    print(f"# of sources: {len(sources)}")

    base_name = Path(source).stem
    df_sources = pd.DataFrame(sources, columns=("source_id", "name"))
    df_sources.to_csv(f"{base_name}-sources.csv", index=False)

    df_quotes = pd.DataFrame(quotes, columns=("quote", "source_id"))
    df_quotes.to_csv(f"{base_name}-quotes.csv", index=False)


if __name__ == "__main__":
    typer.run(main)
