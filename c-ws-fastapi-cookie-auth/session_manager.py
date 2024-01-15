import csv
import uuid
from pathlib import Path

ROOT_DIR = Path(__file__).parent

# Sessions cache loaded from file.
_SESSIONS_CACHE = {}
_SESSIONS_FILE = ROOT_DIR / "sessions.csv"


class SessionManager:
    def __init__(self):
        _SESSIONS_FILE.touch()
        self.load_sessions_from_file()

    def load_sessions_from_file(self) -> None:
        with open(_SESSIONS_FILE, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";", quotechar="|")
            global _SESSIONS_CACHE
            for row in reader:
                sessionid = row[0]
                username = row[1]
                _SESSIONS_CACHE[sessionid] = username

    def write_sessions_to_file(self) -> None:
        with open(_SESSIONS_FILE, "w", newline="") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            for sessionid, username in _SESSIONS_CACHE.items():
                writer.writerow([sessionid, username])

    def create_new_session(self, username: str) -> str:
        sessionid = str(uuid.uuid4())
        global _SESSIONS_CACHE
        _SESSIONS_CACHE[sessionid] = username

        # As a limitation for this demo we only store 100 sessions max.
        # So if there are more than 100 sessions we delete the oldest. The effect is
        #  that the deleted user will be logged out on her next request.
        while len(_SESSIONS_CACHE) > 100:
            # Mind that as of Python 3.7 dict keys are sorted in insertion order:
            # https://docs.python.org/3/tutorial/datastructures.html#dictionaries
            oldest_sessionid = list(_SESSIONS_CACHE)[0]
            del _SESSIONS_CACHE[oldest_sessionid]

        self.write_sessions_to_file()

        return sessionid

    def delete_session(self, sessionid: str) -> None:
        global _SESSIONS_CACHE
        try:
            del _SESSIONS_CACHE[sessionid]
        except KeyError as exc:
            pass

        self.write_sessions_to_file()

    def get_session(self, sessionid: str) -> tuple[str, str]:
        try:
            username = _SESSIONS_CACHE[sessionid]
        except KeyError as exc:
            raise SessionNotFound

        return sessionid, username


class BaseSessionManagerException(Exception):
    pass


class SessionNotFound(BaseSessionManagerException):
    pass
