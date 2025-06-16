import os
import shutil
from typing import List

import pkg_resources

from core.config.configmanager import  ConfigContainer


def init_resources():
    package_name = "core"
    package_dir = pkg_resources.resource_filename(package_name, "resources")
    from core.utils.file_utils import list_all_files
    parentRoot = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    resource_path = os.path.join(parentRoot, "config/resources")
    if not os.path.exists(resource_path):
        os.makedirs(resource_path)
    files: List[str] = list_all_files(package_dir, ext=None)
    for source_file in files:
        dst_file = os.path.join(resource_path, source_file[len(package_dir) + 1 :])
        if not os.path.exists(dst_file):
            shutil.copyfile(source_file, dst_file)
    zvt_env = {}
    zvt_env["resource_path"] = resource_path
    ConfigContainer.set_env(zvt_env)