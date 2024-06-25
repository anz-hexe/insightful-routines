from enum import StrEnum


class Allergies(StrEnum):
    YES = "yes"
    NO = "no"
    IDK = "not that i'm aware of"

    @classmethod
    def as_list(cls):
        return list(map(lambda x: x.value, cls))
