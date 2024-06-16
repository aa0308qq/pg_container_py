import argparse
import atexit
import os
import socket
import time

import redis
import yaml
from pydantic import BaseModel


class SyncRedis:
    """Handle Redis Connection"""

    def __init__(self, redis_host: str, redis_port: int, redis_password: str) -> None:
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_sync_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True,
        )
        atexit.register(self.close_redis_pool)
        while self._redis_ping() is False:
            print("The Redis client waits for a pingpong from the server.")
            time.sleep(0.5)
        print("The Redis client starts connecting to the server.")

    def _redis_ping(self) -> bool:
        try:
            self.redis_sync_client.ping()
            return True
        except BaseException:
            return False

    def close_redis_pool(self):
        if self.redis_sync_client is not None:
            self.redis_sync_client.close()


class SyncRedisHandler(SyncRedis):
    def __init__(
        self,
        redis_host: str,
        redis_port: int,
        redis_password: str,
        postgres_port: int,
        process_uuid: str,
    ) -> None:
        super().__init__(redis_host, redis_port, redis_password)
        self.postgres_port = postgres_port
        self.process_uuid = process_uuid

    def is_postgres_alive(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", self.postgres_port)) == 0

    def start_heartbeat(self):
        while True:
            try:
                if self.is_postgres_alive():
                    self.redis_sync_client.setex(self.process_uuid, 5, "active")
                    time.sleep(1)
            except BaseException:
                while self._redis_ping() is False:
                    time.sleep(1)
                    continue


def build_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "process_uuid", type=str, help="the process-uuid of the triton server"
    )
    parser.add_argument(
        "postgres_port", type=int, help="the port number of the triton server"
    )
    return parser.parse_args()


class RedisYaml(BaseModel):
    redis_host: str
    redis_password: str
    redis_port: int


class RedisHeartBeatYaml(BaseModel):
    process_uuid: str
    postgres_port: int
    redis_yaml: RedisYaml


if __name__ == "__main__":
    args = build_arguments()
    file_name = os.path.splitext(os.path.basename(__file__))[0]
    yaml_path = f"/inno/{file_name}.yaml"
    with open(f"{yaml_path}", encoding="utf-8") as y:
        yaml_dict = yaml.safe_load(y)
    args_schema = RedisHeartBeatYaml(
        process_uuid=args.process_uuid,
        postgres_port=args.postgres_port,
        redis_yaml=yaml_dict,
    ).model_dump()
    sync_redis_client = SyncRedisHandler(
        redis_host=args_schema["redis_yaml"]["redis_host"],
        redis_port=args_schema["redis_yaml"]["redis_port"],
        redis_password=args_schema["redis_yaml"]["redis_password"],
        postgres_port=args_schema["postgres_port"],
        process_uuid=args_schema["process_uuid"],
    )
    sync_redis_client.start_heartbeat()
