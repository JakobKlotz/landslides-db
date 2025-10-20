# Helper file to delete the db and build the images
import shutil
import subprocess
from pathlib import Path

subprocess.run(["docker", "compose", "down"])
# delete db
db_dir = Path("./db")
if db_dir.exists() and db_dir.is_dir():
    shutil.rmtree(db_dir)

subprocess.run(["docker", "compose", "build"])
subprocess.run(["docker", "compose", "up", "db", "-d"])
