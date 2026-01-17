import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

'''
Please make sure to create a .env file first in this directory, like:

    BINARY_PATH=<absolute path for local or debugging>
    MODEL_PATH=<abolute path for local or debugging>
    FLASK_ENV=development <or testing etc>
    FLASK_PORT=5000
    MAX_PROMPT_LENGTH=5000
    GENERATION_TIMEOUT=60
'''


class Config:
    BINARY_PATH = os.getenv('BINARY_PATH')
    MODEL_PATH = os.getenv('MODEL_PATH')

    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = FLASK_ENV == 'development'

    MAX_PROMPT_LENGTH = int(os.getenv('MAX_PROMPT_LENGTH', 5000))
    GENERATION_TIMEOUT = int(os.getenv('GENERATION_TIMEOUT', 60))

    @classmethod
    def validate(cls):
        if not cls.BINARY_PATH:
            raise ValueError("BINARY_PATH not set in .env file")
        if not cls.MODEL_PATH:
            raise ValueError("MODEL_PATH not set in .env file")

        binary_path = Path(cls.BINARY_PATH)
        if not binary_path.exists():
            raise FileNotFoundError(f"Binary not found: {cls.BINARY_PATH}")
        if not binary_path.is_file():
            raise ValueError(f"BINARY_PATH is not a file: {cls.BINARY_PATH}")

        model_path = Path(cls.MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {cls.MODEL_PATH}")
        if not model_path.is_file():
            raise ValueError(f"MODEL_PATH is not a file: {cls.MODEL_PATH}")

        print(f"Config validated successfully")
        print(f"\tBinary: {cls.BINARY_PATH}")
        print(f"\tModel: {cls.MODEL_PATH}")
        print(f"\tEnvironment: {cls.FLASK_ENV}")

