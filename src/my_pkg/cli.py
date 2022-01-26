import time

import hydra
from omegaconf import OmegaConf

from .config import Config


@hydra.main(config_path=None, config_name="main")
def main(cfg: Config) -> None:
    # this line actually runs the checks of pydantic
    OmegaConf.to_object(cfg)
    print(OmegaConf.to_yaml(cfg))
    # note that IDEs allow auto-complete for accessing the attributes!
    time.sleep(cfg.main.sleep)
