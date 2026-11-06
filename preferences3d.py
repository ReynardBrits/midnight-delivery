"""Validated local preferences with atomic saving."""

import json
import math
import os
from pathlib import Path
import tempfile


class Preferences:
    def __init__(self, path=None):
        self.path = (
            Path(path)
            if path is not None
            else Path(__file__).resolve().parent
            / "save_data" / "settings_3d.json"
        )

        self.muted = False
        self.headlights = True
        self.show_map = True
        self.zoom = 760.0

        try:
            data = json.loads(
                self.path.read_text(encoding="utf-8")
            )

            if (
                not isinstance(data, dict)
                or type(data.get("version")) is not int
                or data["version"] != 1
            ):
                return

            for name in ("muted", "headlights", "show_map"):
                value = data.get(name)

                if type(value) is bool:
                    setattr(self, name, value)

            zoom = data.get("zoom")

            if (
                isinstance(zoom, (int, float))
                and not isinstance(zoom, bool)
                and math.isfinite(zoom)
            ):
                self.zoom = max(
                    500.0, min(1600.0, float(zoom))
                )

        except (
            OSError, ValueError,
            UnicodeError, OverflowError,
        ):
            pass

    def save(self, muted, headlights, show_map, zoom):
        data = {
            "version": 1,
            "muted": bool(muted),
            "headlights": bool(headlights),
            "show_map": bool(show_map),
            "zoom": max(500.0, min(1600.0, float(zoom))),
        }

        temporary_path = None

        try:
            self.path.parent.mkdir(
                parents=True, exist_ok=True
            )

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix="settings-",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(data, temporary, indent=2)
                temporary.flush()
                os.fsync(temporary.fileno())

            temporary_path.replace(self.path)
            return True

        except OSError as error:
            print(f"Could not save preferences: {error}")
            return False

        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass