from collections.abc import Mapping
from typing import Any

# Based on the one in the argparse library.
class Namespace:
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        for key, value in mapping.items():
            setattr(self, key, value)

    def __eq__(self, other):
        if not isinstance(other, Namespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
