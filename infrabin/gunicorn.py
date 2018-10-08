from prometheus_client import multiprocess

import multiprocessing
import os

port = os.getenv("PORT", 8080)

bind = f"0.0.0.0:{port}"
timeout = 180
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"
pythonpath = "/infrabin/infrabin"

# check for prometheus settings
if "prometheus_multiproc_dir" not in os.environ:
    raise Exception("prometheus_multiproc_dir is required as environment variable")


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
