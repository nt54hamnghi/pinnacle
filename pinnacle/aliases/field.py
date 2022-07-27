from functools import partial

from attrs import field
from attrs.validators import instance_of

noninit = partial(field, init=False)
string = partial(field, validator=instance_of(str))
noneable = partial(field, default=None)
