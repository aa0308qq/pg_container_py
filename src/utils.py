from contextlib import contextmanager

import yaml
from docker import from_env

from . import validator


def read_yaml(path: str):
    with open(path) as y:
        yaml_dict = yaml.safe_load(y)
    return yaml_dict


def get_config(yaml_path: str) -> dict:
    config_dict = read_yaml(yaml_path)
    config_dict = validator.DatabaseConfig.model_validate(config_dict).model_dump()
    return config_dict


@contextmanager
def docker_client():
    client = from_env()
    try:
        yield client
    finally:
        client.close()
