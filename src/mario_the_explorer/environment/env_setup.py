import json

EMULATOR_SETUP_PATH = "/usr/local/lib/python3.12/dist-packages/stable_retro/data/stable/SuperMarioWorld-Snes-v0/data.json"

SCORE_ADDRESS = 8261428
LIVES_ADDRESS = 8261054
MARIO_X_POSITION_ADDRESS = 0x94
MARIO_Y_POSITION_ADDRESS = 0x96
CAMERA_SCROLL_X_ADDRESS = 0x1A
CAMERA_SCROLL_Y_ADDRESS = 0x1C
MARIO_POWERUP_ADDRESS = 0x0019
MARIO_PRIORITY_ADDRESS = 0x13F9

SPRITE_STATUS_BASE_ADDRESS = 0x14C8
SPRITE_TYPE_BASE_ADDRESS = 0x009E
SPRITE_X_LOW_BASE_ADDRESS = 0x00E4
SPRITE_X_HIGH_BASE_ADDRESS = 0x14E0
SPRITE_Y_LOW_BASE_ADDRESS = 0x00D8
SPRITE_Y_HIGH_BASE_ADDRESS = 0x14D4
SPRITE_PRIORITY_BASE_ADDRESS = 0x15F6

EXT_SPRITE_TYPE_BASE_ADDRESS = 0x170B
EXT_SPRITE_X_LOW_BASE_ADDRESS = 0x171F
EXT_SPRITE_X_HIGH_BASE_ADDRESS = 0x1733
EXT_SPRITE_Y_LOW_BASE_ADDRESS = 0x1715
EXT_SPRITE_Y_HIGH_BASE_ADDRESS = 0x1729



def setup_emulator_memory():
    setup = {
    "info": {
        "score": {"address": SCORE_ADDRESS, "type": "<u4"},
        "lives": {"address": LIVES_ADDRESS, "type": "|i1"},
        "x": {"address": MARIO_X_POSITION_ADDRESS, "type": "<u2"},
        "y": {"address": MARIO_Y_POSITION_ADDRESS, "type": "<u2"},
        "cam_x": {"address": CAMERA_SCROLL_X_ADDRESS,   "type": "<u2"},
        "cam_y": {"address": CAMERA_SCROLL_Y_ADDRESS,   "type": "<u2"},
        "mario_powerup": {"address": MARIO_POWERUP_ADDRESS, "type": "|u1"},
        "mario_priority": {"address": MARIO_PRIORITY_ADDRESS, "type": "|u1"},
    }
    }
    for sprite_index in range(12):
        setup["info"] = add_sprite(setup["info"], sprite_index)
    for extended_sprite_index in range(10):
        setup["info"] = add_extended_sprite(setup["info"], extended_sprite_index)
    update_emulator_setup(setup)

def add_sprite(info: dict, index: int) -> dict:
    info[f"sprite_status_{index}"] = {"address": SPRITE_STATUS_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_type_{index}"] = {"address": SPRITE_TYPE_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_x_low_{index}"]  = {"address": SPRITE_X_LOW_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_x_high_{index}"] = {"address": SPRITE_X_HIGH_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_y_low_{index}"]  = {"address": SPRITE_Y_LOW_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_y_high_{index}"] = {"address": SPRITE_Y_HIGH_BASE_ADDRESS + index, "type": "|u1"}
    info[f"sprite_priority_{index}"] = {"address": SPRITE_PRIORITY_BASE_ADDRESS + index, "type": "|u1"}
    return info

def add_extended_sprite(info: dict, index: int) -> dict:
    info[f"ext_sprite_type_{index}"]   = {"address": EXT_SPRITE_TYPE_BASE_ADDRESS + index, "type": "|u1"}
    info[f"ext_sprite_x_low_{index}"]  = {"address": EXT_SPRITE_X_LOW_BASE_ADDRESS + index, "type": "|u1"}
    info[f"ext_sprite_x_high_{index}"] = {"address": EXT_SPRITE_X_HIGH_BASE_ADDRESS + index, "type": "|u1"}
    info[f"ext_sprite_y_low_{index}"]  = {"address": EXT_SPRITE_Y_LOW_BASE_ADDRESS + index, "type": "|u1"}
    info[f"ext_sprite_y_high_{index}"] = {"address": EXT_SPRITE_Y_HIGH_BASE_ADDRESS + index, "type": "|u1"}
    return info

def update_emulator_setup(setup: dict):
    with open(EMULATOR_SETUP_PATH, "w") as setup_file:
        json.dump(setup, setup_file, indent=2)