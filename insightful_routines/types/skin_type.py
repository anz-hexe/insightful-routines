from enum import StrEnum


class SkinType(StrEnum):
    NORMAL = "normal"
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"

    @classmethod
    def as_list(cls) -> list[str]:
        return list(map(lambda x: x.value, cls))

    @classmethod
    def name(cls) -> str:
        return str(f"{cls.__name__}_enum").lower()
