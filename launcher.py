import os

from docker.models.containers import Container

if __name__ != "__main__":
    from .src import container, image, initialize, utils
else:
    from src import container, image, initialize, utils


def start() -> Container:
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(workspace_path, "postgres.yaml")
    config = utils.get_config(yaml_path)
    pg_container = container.start_container(
        image_name=config["image_name"],
        container_name=config["container_name"],
        database=config["connection_info"]["database"],
        user=config["connection_info"]["user"],
        password=config["connection_info"]["password"],
        port=config["connection_info"]["port"],
        heartbeat_check=config["heartbeat"],
    )
    initialize.init_schema.postgres_init(
        database=config["connection_info"]["database"],
        user=config["connection_info"]["user"],
        password=config["connection_info"]["password"],
        host=config["connection_info"]["host"],
        port=config["connection_info"]["port"],
    )
    return pg_container


def stop() -> bool:
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(workspace_path, "postgres.yaml")
    config = utils.get_config(yaml_path)
    check = container.stop_container(
        container_name=config["container_name"],
    )
    return check


def pull_image() -> bool:
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(workspace_path, "postgres.yaml")
    config = utils.get_config(yaml_path)
    check = image.pull_docker_image(
        image_name=config["image_name"],
    )
    return check


if __name__ == "__main__":
    pull_image()
    start()
    stop()
