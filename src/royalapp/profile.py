import json
from pathlib import Path
from typing import Iterable
import warnings
from platformdirs import user_data_dir
from pydantic_compat import BaseModel, Field

USER_DATA_DIR = Path(user_data_dir("royalapp"))


def profile_dir() -> Path:
    _dir = USER_DATA_DIR / "profiles"
    if not _dir.exists():
        _dir.mkdir(parents=True)
    return _dir


def _default_plugins() -> list[str]:
    """Factory function for the default plugin list."""
    out = []
    _builtins_dir = Path(__file__).parent.joinpath("builtins")
    for path in _builtins_dir.joinpath("qt").glob("*"):
        if path.name == "__pycache__":
            continue
        out.append(f"royalapp.builtins.qt.{path.name}")
    for path in _builtins_dir.glob("*.py"):
        out.append(f"royalapp.builtins.{path.stem}")
    return out


class AppProfile(BaseModel):
    """Model of a profile."""

    name: str = Field(default="default", description="Name of the profile.")
    plugins: list[str] = Field(
        default_factory=_default_plugins, description="List of plugins to load."
    )
    theme: str = Field(default="default", description="Theme to use.")

    @classmethod
    def from_json(cls, path) -> "AppProfile":
        """Construct an AppProfile from a json file."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def default(self) -> "AppProfile":
        """Return the default profile."""
        return AppProfile()

    def save(self, path):
        """Save profile as a json file."""
        with open(path, "w") as f:
            json.dump(self.dict(), f, indent=4)
        return None


def load_app_profile(name: str) -> AppProfile:
    path = profile_dir() / f"{name}.json"
    return AppProfile.from_json(path)


def iter_app_profiles() -> Iterable[AppProfile]:
    for path in profile_dir().glob("*.json"):
        try:
            yield AppProfile.from_json(path)
        except Exception:
            warnings.warn(f"Could not load profile {path}.")


def define_app_profile(name: str, plugins: list[str]):
    path = profile_dir() / f"{name}.json"
    profile = AppProfile(name=name, plugins=plugins)
    profile.save(path)
    return None
