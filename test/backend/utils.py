import os

def check_login(username, password):
    base = os.path.dirname(os.path.dirname(__file__))
    users_file = os.path.join(base, "securite", "users.txt")
    try:
        with open(users_file, "r") as f:
            for line in f:
                parts = line.strip().split("||")
                if len(parts) != 2:
                    continue
                u, p = parts
                if u == username and p == password:
                    return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
    return False