"""Configuration subpackage loader for evolutionary algorithms."""
import configparser
import os
import pathlib

from gevopy import algorithms, schedulers, selections

# Get configuration from user env and merge with pkg settings
DEFAULTS_FILE = pathlib.Path(__file__).parent / "settings.ini"
SETTINGS_FILE = os.getenv("GEVOPY_SETTINGS", default="")
settings = configparser.ConfigParser()
settings.read(DEFAULTS_FILE)
settings.read(SETTINGS_FILE)

SCHEDULER_MODES = ['synchronous', 'threads', 'processes']


# Runtime configuration
def scheduler():
    """Actual scheduler from envrionment variable GEVOPY_SCHEDULER."""
    value = os.getenv("GEVOPY_SCHEDULER", settings['runtime']['scheduler'])
    if value not in SCHEDULER_MODES:
        raise RuntimeError(f"Undefined scheduler {value}")
    return value


def algorithm():
    """Actual algorithm from envrionment variable GEVOPY_ALGORITHM."""
    return algorithms.get(
        os.getenv("GEVOPY_ALGORITHM", settings['runtime']['algorithm'])
    )


def selection():
    """Actual value for envrionment variable GEVOPY_SELECTION."""
    return selections.get(
        os.getenv("GEVOPY_SELECTION", settings['runtime']['selection'])
    )


# Leaderboard configuration
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
