from ctypes import c_bool, c_uint64
from enum import Enum, auto

from _ctypes import Structure

TIME_I = 0
IS_DOWN_I = 1
KEY_I = 2

# Modifier keys
MOD_KEYS = {'alt', 'alt_gr', 'alt_l', 'alt_r', 'cmd', 'cmd_r', 'ctrl', 'ctrl_l', 'ctrl_r', 'shift', 'shift_r'}

MAIN_AREA_KEYS = set("abcdefghijklmnopqrstuvwxyzäöüß,.-<")

# We disabled the following for one of two reasons
# 1. on a traditional keyboard they are far away (e.g. left key), possibly skewing the timing, or
# 2. they are most likely not an actual shortcut (ctrl + left is, but shift + backspace is not)
# MAIN_AREA_KEYS.update('left right backspace space enter tab'.split())


class TrainingDataColId(Enum):
    prev_down_time = 0
    prev_up_time = auto()
    th_down_time = auto()
    next_down_time = auto()
    next_up_time = auto()
    th_up_time = auto()
    last_down_time = auto()
    prev_is_mod = auto()
    is_mod = auto()

    @classmethod
    @property
    def member_names(cls) -> list[str]:
        return cls._member_names_

    @property
    def c_type(self):
        if self.is_bool():
            return c_bool
        return c_uint64

    def is_bool(self):
        return self == TrainingDataColId.is_mod or self == TrainingDataColId.prev_is_mod

    def parse(self, val: str):
        if self.is_bool():
            return val == 'True'
        return int(val)

    def to_csv(self, val):
        if self.is_bool():
            return 1 if val else 0
        return val


class TrainingEvent(Structure):
    _fields_ = [(v.name, v.c_type) for v in TrainingDataColId]
