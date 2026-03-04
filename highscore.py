import os

def get_high_score_path(filename="highscore.txt"):
    # Store file in a writable folder with same filename
    folder = os.path.join(os.path.expanduser("~"), ".astro_shooter")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, filename)

def load_high_score(filename="highscore.txt"):
    path = get_high_score_path(filename)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return int(f.read().strip() or 0)
        except:
            return 0
    return 0

def save_high_score(newHigh, filename="highscore.txt"):
    path = get_high_score_path(filename)
    with open(path, "w") as f:
        f.write(str(newHigh))