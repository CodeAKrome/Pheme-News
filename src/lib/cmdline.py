import argparse


def cmdargs():
    init = {
        "prog": "Prog",
        "description": "Desc",
        "epilog": "Hackers of the world, unite!",
    }
    ap = argparse.ArgumentParser(**init)
    ap.add_argument("-r", "--rss", help="File containing RSS URLs.")
    ap.add_argument("-m", "--mode", help="Operating mode.")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-i", "--items", nargs="*", help="List of items for mode.")
    return ap.parse_args()
