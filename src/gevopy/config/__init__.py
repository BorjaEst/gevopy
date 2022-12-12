"""Configuration subpackage loader for evolutionary algorithms."""

import configparser
import pathlib
import os

settings = configparser.ConfigParser()
GEVOPY_USER_CONFIG = os.getenv("GEVOPY_USER_CONFIG", default="")


settings.read(pathlib.Path(__file__).parent / "defaults.toml")
settings.read(GEVOPY_USER_CONFIG)
