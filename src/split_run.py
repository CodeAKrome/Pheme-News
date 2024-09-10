import sys
import fire


def main(batches: int = 5, prefix: str = "batch-"):
    handles = {}
    n = 0
    for line in sys.stdin:
        line = line.strip()
        if line:
            batchnum = n % batches
            handle_name = f"{prefix}{batchnum}"
            if not handle_name in handles:
                handles[handle_name] = open(f"{prefix}{batchnum}.sh", "w")
            print(line, file=handles[handle_name])
            n += 1


if __name__ == "__main__":
    fire.Fire(main)
