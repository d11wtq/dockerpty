import docker
from docker.utils import kwargs_from_env


def get_client():
    kwargs = kwargs_from_env(assert_hostname=False)
    return docker.AutoVersionClient(**kwargs)
