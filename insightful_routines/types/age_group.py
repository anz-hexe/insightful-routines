from enum import StrEnum


class AgeGroup(StrEnum):
    GROUP1 = "up to 25"
    GROUP2 = "25 - 30"
    GROUP3 = "30 - 45"
    GROUP4 = "45+"

    @classmethod
    def as_list(cls) -> list[str]:
        return list(map(lambda x: x.value, cls))

    @classmethod
    def name(cls) -> str:
        return str(f"{cls.__name__}_enum").lower()
