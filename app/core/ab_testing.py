import hashlib
from app.config import SALT,GROUP_A_PERCENTAGE

def get_exp_group(user_id: int) -> str:
    h = hashlib.md5((str(user_id) + SALT).encode()).hexdigest()
    return "control" if int(h, 16) % 100 < GROUP_A_PERCENTAGE else "test"
