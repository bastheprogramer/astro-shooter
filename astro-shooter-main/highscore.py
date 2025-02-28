import os

def load_high_score(filename="highscore.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_high_score(new_high, filename="highscore.txt"):
    with open(filename, "w") as f:
        f.write(str(new_high))
