from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_CONTROL_PATH = os.getenv("MODEL_CONTROL_PATH")
MODEL_TEST_PATH = os.getenv("MODEL_TEST_PATH")
AB_TEST_ENABLED = os.getenv("AB_TEST_ENABLED", "False").lower() == "true"
SALT = os.getenv("SALT", "salt")
GROUP_A_PERCENTAGE = int(os.getenv("GROUP_A_PERCENTAGE", "50"))
