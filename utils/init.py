import os
from os import makedirs
from os.path import exists, join
import pathlib
import yaml
import sys


class Init(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def _check_if_initialized(self):
        folder_path = join(self.root_dir, ".mlbot")

        return exists(folder_path)

    def _create_folder_structure(self):
        makedirs(join(self.root_dir, ".mlbot"))
        makedirs(join(self.root_dir, ".mlbot", "configs"))
        makedirs(join(self.root_dir, ".mlbot", "logs"))
        makedirs(join(self.root_dir, ".mlbot", "errs"))

    def _create_config_file(self):
        config = dict(
            python_version="python",
            conda_env="",
            max_num_process=50,
            anaconda_path="~/anaconda3",
        )

        with open(join(self.root_dir, ".mlbot", "config.yaml"), "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    def __call__(self):
        if not self._check_if_initialized():
            self._create_folder_structure()
            self._create_config_file()


if __name__ == "__main__":
    curr_dir = ""

    if getattr(sys, "frozen", False):
        curr_dir = os.path.dirname(sys.executable)
    elif __file__:
        curr_dir = os.path.dirname(__file__)

    # print("Current Dir: ", curr_dir)
    a = Init(curr_dir)
    a()
