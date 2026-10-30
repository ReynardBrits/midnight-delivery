import json
import os
import tempfile
from pathlib import Path


class Records:
    """Keep completed-night records in a local JSON file."""

    VERSION = 1

    def __init__(self, path=None):
        self.path = (
            Path(path)
            if path is not None
            else (
                Path(__file__).resolve().parent
                / "save_data"
                / "records.json"
            )
        )

        self.best_score: int | None = None
        self.completed_nights = 0
        self.new_best = False
        self.notice = ""

        self.load()

    @property
    def best_text(self):
        return (
            str(self.best_score)
            if self.best_score is not None
            else "NONE YET"
        )

    def load(self):
        try:
            data = json.loads(
                self.path.read_text(encoding="utf-8")
            )

            if not isinstance(data, dict):
                raise ValueError("Record must be an object.")

            if (
                type(data.get("version")) is not int
                or data["version"] != self.VERSION
                or type(data.get("best_score")) is not int
                or data["best_score"] < 0
                or type(data.get("completed_nights")) is not int
                or data["completed_nights"] < 1
            ):
                raise ValueError("Record fields are invalid.")

            self.best_score = data["best_score"]
            self.completed_nights = data["completed_nights"]

        except FileNotFoundError:
            pass

        except (OSError, ValueError, UnicodeError):
            self.notice = (
                "Saved record unreadable. "
                "New records start fresh."
            )

    def reset_night(self):
        self.new_best = False

    def record_completed(self, score):
        if type(score) is not int or score < 0:
            raise ValueError(
                "Score must be a non-negative integer."
            )

        self.new_best = (
            self.best_score is None
            or score > self.best_score
        )

        if self.new_best:
            self.best_score = score

        self.completed_nights += 1
        self.save()

    def save(self):
        data = {
            "version": self.VERSION,
            "best_score": self.best_score,
            "completed_nights": self.completed_nights,
        }

        temporary_path = None

        try:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Close the temporary file before replacing it on Windows.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix="records-",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                json.dump(
                    data,
                    temporary_file,
                    indent=2,
                )

                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            # A failed write leaves the previous record intact.
            temporary_path.replace(self.path)
            self.notice = ""

        except OSError:
            self.notice = (
                "Score kept this session; saving failed."
            )

        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass