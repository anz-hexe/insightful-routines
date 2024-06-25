from enum import StrEnum


class AgeGroup(StrEnum):
    GROUP1 = "up to 25"
    GROUP2 = "25 - 30"
    GROUP3 = "30 - 45"
    GROUP14 = "45+"

    @classmethod
    def as_list(cls):
        return list(map(lambda x: x.value, cls))
