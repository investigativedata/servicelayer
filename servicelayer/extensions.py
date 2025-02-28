import logging
from threading import RLock
from importlib.metadata import entry_points

log = logging.getLogger(__name__)
lock = RLock()
EXTENSIONS = {}


def get_entry_points(section):
    """Load all Python classes registered at a given entry point."""
    with lock:
        if section not in EXTENSIONS:
            EXTENSIONS[section] = {}
            for ep in entry_points(group=section):
                EXTENSIONS[section][ep.name] = ep.load()
        return EXTENSIONS[section]


def get_entry_point(section, name):
    return get_entry_points(section).get(name)


def get_extensions(section):
    """Iterate entry point objects."""
    return list(get_entry_points(section).values())
