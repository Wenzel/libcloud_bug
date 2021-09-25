import subprocess
from pytest import fixture
from libcloud.storage.providers import get_driver
from requests.exceptions import ConnectionError
import time

MINIO_VERSION = "RELEASE.2021-05-11T23-27-41Z"

@fixture(scope="session")
def minio_db():
    """start a MinIO db using Docker"""
    port = 9000
    cont_name = "libcloud_bug_objectmistmatch_miniodb"
    cmdline = [
        "docker",
        "run",
        "--detach",
        f"--publish=9000:{port}",
        f"--name={cont_name}",
        f"minio/minio:{MINIO_VERSION}",
        "server",
        "/data",
    ]
    subprocess.check_call(cmdline)
    yield
    cmdline = ["docker", "rm", "--force", cont_name]
    subprocess.check_call(cmdline)


@fixture(scope="session")
def ready_minio_db(minio_db):
    """ensures that the minioDB is ready to receive connections"""
    driver_cls = get_driver("minio")
    driver = None
    while not driver:
        try:
            driver = driver_cls(key="minioadmin", secret="minioadmin", host="127.0.0.1",
                    port=9000, secure=False)
            list(driver.iterate_containers())
        except ConnectionError:
            driver = None
            time.sleep(0.1)
    return driver


@fixture(scope="function")
def clean_minio_db(ready_minio_db):
    """cleanup DB after test"""
    libcloud_drv = ready_minio_db
    # ensure cleanup up before test if pytest crashed or process killed, or teardown skipped for whatever reason
    for container in libcloud_drv.iterate_containers():
        for obj in libcloud_drv.iterate_container_objects(container):
            libcloud_drv.delete_object(obj)
        libcloud_drv.delete_container(container)
    # do the test
    yield libcloud_drv
    # cleanup
    for container in libcloud_drv.iterate_containers():
        for obj in libcloud_drv.iterate_container_objects(container):
            libcloud_drv.delete_object(obj)
        libcloud_drv.delete_container(container)
