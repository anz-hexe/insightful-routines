from enum import StrEnum


class Allergies(StrEnum):
    YES = "yes"
    NO = "no"
    IDK = "not that i'm aware of"

    @classmethod
    def as_list(cls) -> list[str]:
        return list(map(lambda x: x.value, cls))

    @classmethod
    def name(cls) -> str:
        return str(f"{cls.__name__}_enum").lower()
