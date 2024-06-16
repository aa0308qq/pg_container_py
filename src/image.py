from docker import errors as docker_errors

from . import utils


def check_docker_image(
    repository: str,
    tag: str = "latest",
) -> bool:
    with utils.docker_client() as client:
        try:
            client.images.get(f"{repository}:{tag}")
            print(f"Check docker image: {repository}:{tag}   OK", flush=True)
            return True
        except docker_errors.ImageNotFound:
            print(f"Check docker image: {repository}:{tag}   NO", flush=True)
            return False


def pull_docker_image(image_name: str) -> bool:
    repository, tag = image_name.split(":")
    if check_docker_image(repository=repository, tag=tag) is False:
        print(f"Pull docker image: {repository}:{tag}", flush=True)
        with utils.docker_client() as client:
            try:
                resp = client.api.pull(
                    repository=repository,
                    tag=tag,
                    stream=True,
                    decode=True,
                )
                for info_dict in resp:
                    prev_mesg, end = "", "\n"
                    status = info_dict["status"]
                    if "progressDetail" in info_dict:
                        progress = (
                            info_dict["progress"] if "progress" in info_dict else ""
                        )
                        mesg = f"\t- {status} {progress}"
                        end = "\r"
                    else:
                        mesg = f"\t- {status}"

                    if prev_mesg != mesg:
                        print(mesg, end=end, flush=True)
                        prev_mesg = mesg
                print()
            except BaseException:
                return False
    return True
