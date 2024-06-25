from enum import StrEnum


class SkinType(StrEnum):
    NORMAL = "normal"
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"

    @classmethod
    def as_list(cls):
        return list(map(lambda x: x.value, cls))
