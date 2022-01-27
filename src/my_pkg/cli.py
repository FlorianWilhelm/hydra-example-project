import logging
import time

import hydra
from omegaconf import OmegaConf

from .config import Config

# A logger for this file
log = logging.getLogger(__name__)


@hydra.main(config_path=None, config_name="main")
def main(cfg: Config) -> None:
    # this line actually runs the checks of pydantic
    OmegaConf.to_object(cfg)
    # log to console and into the `outputs` folder per default
    log.info(f"\n{OmegaConf.to_yaml(cfg)}")
    # note that IDEs allow auto-complete for accessing the attributes!
    time.sleep(cfg.main.sleep)
