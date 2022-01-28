"""
Schema definition and validation of the hierarchical config files.
"""
from typing import List

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from pydantic import validator

# we use pydantic as a replacement of default dataclasses for more validation features
from pydantic.dataclasses import dataclass


@dataclass
class Experiment:
    model: str
    l2: float
    n_steps: int


@dataclass
class DataBase:
    driver: str
    host: str
    @validator("port")
    def check_non_privileged_port(cls, port: int) -> int:
        if port < 1024:
            raise ValueError("Choose a non-privileged port!")
        return port
    port: int
    username: str
    password: str


@dataclass
class Neptune:
    project: str
    api_token: str
    tags: List[str]
    description: str
    mode: str


@dataclass
class Main:
    sleep: int


@dataclass
class Config:
    main: Main
    db: DataBase
    neptune: Neptune
    experiment: Experiment = MISSING


cs = ConfigStore.instance()
# name `base_config` is used for matching it with the main.yaml's default section
cs.store(name="base_config", node=Config)
