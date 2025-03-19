from ulid import ULID
from charidfield import CharIDField
from functools import partial

ULIDField = partial(
    CharIDField,
    default=ULID,
    max_length=12,
    help_text="ulid-format identifier for this entity.",
)
