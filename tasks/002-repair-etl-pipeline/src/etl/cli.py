import argparse
from .config import load_config
from .pipeline import deduplicate, read_rows, summarize, write_rejections
from .validation import validate_row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    rows = read_rows(args.input, config["input"]["encoding"])
    rows = deduplicate(rows, config["deduplication"]["key"], config["deduplication"]["keep"])

    valid, rejected = [], []
    for row in rows:
        ok, reason = validate_row(row)
        if ok:
            valid.append(row)
        else:
            rejected.append((row, reason))

    write_rejections(rejected, "output/rejected.csv")
    summary = summarize(valid, args.output)
    print(summary)

if __name__ == "__main__":
    main()
