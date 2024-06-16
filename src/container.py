import os
import time

from docker import errors as docker_errors
from docker.models.containers import Container

from . import utils


def check_container(container_name: str) -> bool:
    with utils.docker_client() as client:
        try:
            client.containers.get(container_name)
        except docker_errors.NotFound:
            return False
        return True


def start_container(
    image_name: str,
    container_name: str,
    database: str,
    user: str,
    password: str,
    port: int,
    heartbeat_check: bool,
) -> Container:
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    init_db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "initialize", "init_user"
    )
    local_db_path = os.path.join(workspace_path, "storage")
    heartbeat_path = os.path.join(workspace_path, "heartbeat")
    if check_container(container_name) is True:
        with utils.docker_client() as client:
            container = client.containers.get(container_name)
    else:
        with utils.docker_client() as client:
            try:
                container = client.containers.run(
                    image=image_name,
                    name=f"{container_name}",
                    network_mode="host",
                    environment=[
                        "PGDATA=/var/lib/postgresql/data/pgdata",
                        f"POSTGRES_USER={user}",
                        f"POSTGRES_PASSWORD={password}",
                        "POSTGRES_INITDB_ARGS='--data-checksums'",
                        f"POSTGRES_DB={database}",
                    ],
                    volumes=[
                        f"{local_db_path}:/var/lib/postgresql/data",
                        f"{init_db_path}:/docker-entrypoint-initdb.d",
                        f"{heartbeat_path}:/inno",
                    ],
                    command=["-c", "max_connections=200", f"-p {port}"],
                    stream=True,
                    auto_remove=True,
                    detach=True,
                )
                if isinstance(container, Container):
                    while True:
                        check_pg_status = container.exec_run(
                            f"pg_isready -d {database} -U {user} -p {port} -q"
                        )
                        if check_pg_status.exit_code == 0:
                            break
                        else:
                            print(
                                "Waiting,postgresql is not ready",
                                end="\r",
                                flush=True,
                            )
                        time.sleep(0.01)
                    if heartbeat_check is True:
                        container.exec_run(
                            f"/inno/redis_heartbeat cold_database {port}",
                            detach=True,
                        )
            except docker_errors.ContainerError:
                return start_container(
                    image_name,
                    container_name,
                    database,
                    user,
                    password,
                    port,
                    heartbeat_check,
                )
            except docker_errors.APIError as a:
                time.sleep(0.5)
                container = client.containers.get(container_name)
                if not isinstance(container, Container):
                    raise TypeError() from a
                return container
    if not isinstance(container, Container):
        raise TypeError()
    return container


def stop_container(container_name: str) -> bool:
    if check_container(container_name) is True:
        with utils.docker_client() as client:
            container = client.containers.get(container_name)
            if not isinstance(container, Container):
                raise TypeError()
            container.stop()
        return True
    else:
        return False
