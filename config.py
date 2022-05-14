import tkinter
from dataclasses import dataclass, fields
from typing import List

import yaml


class Updateable(object):
    def update(self, new):
        for key, value in new.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class MPEConfig(Updateable):
    cycle_count: int
    agent_count: int
    s_agent_count: int
    k_min: int
    k_max: int
    expoA: float
    expoG: float
    s_type: str
    good_will_x: float
    good_will_y: float
    good_will_z: float
    delta: float
    scenario: int
    V_0: float


_MPE_CONFIG = None
MPE_CONFIG_PATH = "./config.yaml"


def get_mpe_config(file_path: str = MPE_CONFIG_PATH) -> MPEConfig:
    global _MPE_CONFIG

    if _MPE_CONFIG is None:
        _MPE_CONFIG = _load_mpe_config(file_path)

    return _MPE_CONFIG


def _load_mpe_config(file_path: str) -> MPEConfig:
    with open(file_path) as file:
        config_dict = yaml.safe_load(file)
        return MPEConfig(
            cycle_count = config_dict["cycle_count"],
            agent_count=config_dict["agent_count"],
            s_agent_count=config_dict["s_agent_count"],
            k_min=config_dict["k_min"],
            k_max=config_dict["k_max"],
            expoA=config_dict["expoA"],
            expoG=config_dict["expoG"],
            s_type=config_dict["s_type"],
            good_will_x=config_dict["good_will_x"],
            good_will_y=config_dict["good_will_y"],
            good_will_z=config_dict["good_will_z"],
            delta=config_dict["delta"],
            scenario=config_dict["scenario"],
            V_0=config_dict["V_0"],
        )


def update_mpe_config(entries: List[tkinter.Entry], mpe_config: MPEConfig) -> MPEConfig:
    updated_values = {}
    for entry, field in zip(entries, fields(MPEConfig)):
        value = entry.get()
        if value:
            value_type = field.type
            value = value_type(value)
            updated_values[entry.cget("textvariable")] = value

    mpe_config.update(updated_values)
    return mpe_config
