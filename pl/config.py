from pathlib import Path

import yaml

class Config(dict):
    """
    Wrapper around dict for configuration
    """
    DEFAULT_PATH = "~/.config/plconf.yaml"
    DEFAULTS = {
        "search_command": "fzf",
        "open_command": "xdg-open",
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.DEFAULTS.items():
            if key not in self:
                self[key] = value

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError as ex:
            raise AttributeError(ex)

    def __setattr__(self, k, v):
        self[k] = v

    @classmethod
    def from_path(cls, path=None):
        """
        Initialise a Config object from a pathlib.Path
        """
        path = path or Path(cls.DEFAULT_PATH).expanduser()
        with path.open() as f:
            return cls(yaml.safe_load(f))
