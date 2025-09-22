import os

from dotenv import load_dotenv

load_dotenv()


def _read_env_variable(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable {var_name} not set.")
    return value


# use naming of supported env variables
# see https://hub.docker.com/r/postgis/postgis/#supported-environment-variables
db_user = _read_env_variable("POSTGRES_USER")
db_password = _read_env_variable("POSTGRES_PASSWORD")
db_host = _read_env_variable("POSTGRES_HOST")
db_port = _read_env_variable("POSTGRES_PORT")
db_name = _read_env_variable("POSTGRES_DB")

DB_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
