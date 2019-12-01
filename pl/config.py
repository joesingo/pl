from pathlib import Path

class Config(dict):
    """
    Wrapper around dict for configuration
    """
    DEFAULT_PATH = Path("~/.config/plconf.yaml").expanduser()
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
