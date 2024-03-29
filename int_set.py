#!/usr/bin/python3.10
class IntSet:
    def __init__(self, max_value: int):
        self.is_present = [False] * max_value

    def __contains__(self, value: int):
        return self.is_present[value]

    def __iter__(self):
        return iter(idx for idx, val in enumerate(self.is_present) if val is not False)

    def add(self, value: int) -> None:
        self.is_present[value] = True

    def pop(self, value: int) -> bool:
        ret = self.is_present[value]
        self.is_present[value] = False
        return ret








