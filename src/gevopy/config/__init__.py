import configparser
import os
import pathlib


import gevopy

# Get configuration from user env and merge with pkg settings
DEFAULTS_FILE = pathlib.Path(__file__).parent / "settings.ini"
SETTINGS_FILE = os.getenv("GEVOPY_SETTINGS", default="")
settings = configparser.ConfigParser()
settings.read(DEFAULTS_FILE)
settings.read(SETTINGS_FILE)


# -- available definitions
available_algorithm = tuple(gevopy._algorithms.available_algorithms)
algorithms = {k: gevopy._algorithms.__dict__[k] for k in available_algorithm}

available_selection = tuple(gevopy._selections.available_selections)
selections = {k: gevopy._selections.__dict__[k] for k in available_selection}


# --Runtime configuration
try:  # Defines the default algorithm to use on evolution runtime
    value = os.getenv("GEVOPY_ALGORITHM", settings['runtime']['algorithm'])
    DEFAULT_ALGORITHM = algorithms[value]
except KeyError as err:
    raise RuntimeError(f"Invalid runtime algorithm {err}") from err

try:  # Defines the default selection to use on evolution runtime
    value = os.getenv("GEVOPY_SELECTION", settings['runtime']['selection'])
    DEFAULT_SELECTION = selections[value]
except KeyError as err:
    raise RuntimeError(f"Invalid for runtime selection {err}") from err

try:  # Defines the default scheduler to use on evolution runtime
    value = os.getenv("GEVOPY_SCHEDULER", settings['runtime']['scheduler'])
    DEFAULT_SCHEDULER = gevopy._schedulers.validate_scheduler(mode=value)
except KeyError as err:
    raise RuntimeError(f"Invalid for runtime scheduler {err}") from err


# --Leaderboard configuration
def leaderboard_timeout():
    """Actual value for envrionment variable GEVOPY_LBTOUT."""
    return os.getenv("GEVOPY_LBTOUT", settings['leaderboard']['timeout'])


def leaderboard_uri():
    """Actual value for envrionment variable GEVOPY_LBURI."""
    return os.getenv("GEVOPY_LBURI", settings['leaderboard']['uri'])


# Database configuration
def database_timeout():
    """Actual value for envrionment variable GEVOPY_DBTOUT."""
    return os.getenv("GEVOPY_DBTOUT", settings['database']['timeout'])


def database_uri():
    """Actual value for envrionment variable GEVOPY_DBURI."""
    return os.getenv("GEVOPY_DBURI", settings['database']['uri'])


def database_auth():
    """Actual value for envrionment variable GEVOPY_DBAUTH."""
    return os.getenv("GEVOPY_DBAUTH", settings['database']['auth'])
