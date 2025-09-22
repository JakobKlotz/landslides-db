import os

from dotenv import load_dotenv

load_dotenv()


def _read_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable {var_name} not set.")
    return value


db_user = _read_env_variable("DB_USER")
db_password = _read_env_variable("DB_PASSWORD")
db_host = _read_env_variable("DB_HOST")
db_name = _read_env_variable("DB_NAME")

DB_URI = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
