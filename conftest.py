import os
import tempfile
# pyright: reportUnusedImport=false

# Create a temporary file-based SQLite DB for tests
_tmpdir = tempfile.TemporaryDirectory()
os.environ["TASKS_DB_PATH"] = os.path.join(_tmpdir.name, "testtasks.db")


# TEMPORARY: view test DB for inspection in local file
#os.environ["TASKS_DB_PATH"] = "test_tasks_debug.db"

