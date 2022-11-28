import os
from os.path import join, isfile
from os import listdir, remove
import subprocess
import psutil
import glob
import random
import yaml
import pickle
import sys
from collections import OrderedDict

sys.path.append("/home/foneme/Desktop/MLBot/")

from utils.argsparser import ArgsParser

## To Do:
# Delete older log files, add a config parameter for max number of log files to be saved
# Do proper error handling if the command line throws some error in
#   SlackAPIHandler.handle_run_process, SlackAPIHandler.handle_stop_process & SlackAPIHandler.handle_get_process
# Add webhooks to be able to subscribe to a training or eval stats
# Clear the process_list.pickle when the slack bot server starts running

## Function in SlackAPIHandler class:
# Private Function:
#   _add_pid_to_file        ✔
#   _run_cmd_process        ✔
# Public Function:
#   handle_run_process      ✔
#   handle_get_process      ✔
#   handle_stop_process     ✔
#   handle_app_mention      ❌
#   handle_create_args      ✔
#   handle_show_args        ✔
#   handle_delete_args      ✔
#   handle_update_args      ❌

## Notes:
# Only one process can run with a particular config name
# The _run_cmd_process does not handle exception while starting a process
# On the fly update to an existing config file is not implemented yet

## Code Practice
# While printing error messages, always print the function and class name that throws the error
# Put Slack "say" messages for errors whenever there's a caught error
# Add return flags (and handle them) to the functions (Only partially there)
# When sending Slack "say" messages for incorrect prompt format,
#   send the correct input format or tool docs prompt "@MLBot --help"
# Write input format at the top of all API endpoint handlers


class SlackAPIHandler(object):
    def __init__(self, config, root_dir):
        self.config = config
        self.root_dir = root_dir
        self.args_parser = ArgsParser(config, root_dir)
        self.process_obj_list = {}

        # Removing old processes as currently the running processes are connected to the python process
        # if isfile(join(self.root_dir, ".mlbot", "process_list.pickle")):
        #     remove(join(self.root_dir, ".mlbot", "process_list.pickle"))

    # This function adds config name and PID to process_list.pickle
    def _add_pid_to_file(self, pid, config_name):
        if isfile(join(self.root_dir, ".mlbot", "process_list.pickle")):
            with open(join(self.root_dir, ".mlbot", "process_list.pickle"), "rb") as f:
                try:
                    pid_list = pickle.load(f)
                except EOFError:
                    print(
                        "Empty process_list.pickle in SlackAPIHandler._add_pid_to_file function"
                    )
                    pid_list = OrderedDict()
                except:
                    print(
                        "Error in reading process list file in SlackAPIHandler._add_pid_to_file function"
                    )
                    return False
        else:
            pid_list = OrderedDict()

        if len(pid_list) == self.config["max_num_process"]:
            del_config_name = pid_list.popitem(
                last=False
            )  # False removes in FIFO order

            log_filepath = join(
                self.root_dir, ".mlbot", "logs", "{}.txt".format(del_config_name)
            )
            err_filepath = join(
                self.root_dir, ".mlbot", "errs", "{}.txt".format(del_config_name)
            )

            remove(log_filepath)  # Deleting older log file
            remove(err_filepath)  # Deleting older err file

        pid_list[config_name] = pid

        with open(join(self.root_dir, ".mlbot", "process_list.pickle"), "wb") as f:
            pickle.dump(pid_list, f)

    # This function removes the config name and PID from process_list.pickle
    def _remove_pid_from_file(self, config_name):
        if isfile(join(self.root_dir, ".mlbot", "process_list.pickle")):
            with open(join(self.root_dir, ".mlbot", "process_list.pickle"), "rb") as f:
                try:
                    pid_list = pickle.load(f)
                except EOFError:
                    print(
                        "Empty process_list.pickle in SlackAPIHandler._remove_pid_from_file function"
                    )
                    return
                except:
                    print(
                        "Error in reading process list file in SlackAPIHandler._add_pid_to_file function"
                    )
                    return False

            _ = pid_list.pop(config_name)
            with open(join(self.root_dir, ".mlbot", "process_list.pickle"), "wb") as f:
                pickle.dump(pid_list, f)

        else:
            print(
                "process_list.pickle is missing in SlackAPIHandler._remove_pid_from_file function"
            )

    # This function runs executes the shell command given a args dictionary
    def _run_cmd_process(self, args_dict):
        # command = "nohup {} -u {}".format(
        #     self.config["python_version"], join(self.root_dir, args_dict["run_file"])
        # )

        # command = [
        #     "bash",
        #     "-c",
        #     "conda activate {}".format(self.config["conda_env"]),
        #     # "nohup",
        #     self.config["python_version"],
        #     "-u",
        #     join(self.root_dir, args_dict["run_file"]),
        # ]

        anaconda_path = join(self.config["anaconda_path"], "etc/profile.d/conda.sh")
        python_run_file_path = join(self.root_dir, args_dict["run_file"])

        command = ". {}; conda activate {}; {} -u {}".format(
            anaconda_path,
            self.config["conda_env"],
            self.config["python_version"],
            python_run_file_path,
        )

        for key in args_dict.keys():
            if (key != "config_name") and (key != "run_file"):
                command = command + " " + key
                # command.append(key)
                if args_dict[key] != "":
                    # command.append(args_dict[key])
                    command = command + " " + args_dict[key]

        log_filepath = join(
            self.root_dir, ".mlbot", "logs", "{}.txt".format(args_dict["config_name"])
        )
        err_filepath = join(
            self.root_dir, ".mlbot", "errs", "{}.txt".format(args_dict["config_name"])
        )

        print(command)
        # Write proper error handling if this command throws some error
        p = subprocess.Popen(
            command,
            stdout=open(log_filepath, "w"),
            stderr=open(err_filepath, "w"),
            shell=True,
        )
        # self._add_pid_to_file(p.pid, args_dict["config_name"])
        self.process_obj_list[args_dict["config_name"]] = p

    def _check_if_config_name_running(self, config_name):
        return config_name in self.process_obj_list.keys()

    def _kill_process_using_pid(self, pid):
        process = psutil.Process(pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    # This function will send a usage guide for the tool
    def handle_app_mention(self, message, say):
        say("Hi there!!")

    ## All process related APIs

    # This function handles chat prompt to run a new process
    # Input format: Run Process <Config Name> <Run File Relative Path> <Config Parameters>
    def handle_run_process(self, message, say):
        flag, args_dict = self.args_parser(message["text"].split(" "), say)

        if self._check_if_config_name_running(args_dict["config_name"]):
            print(
                "Process with the same config name already running in SlackAPIHandler.handle_run_process function"
            )
            say("Process with the same config name is already running")
            return

        if not flag:
            print("Error in args parsing")
            return False

        # Refactor this later and add to the args parser class
        if not self.args_parser.check_if_valid_config(args_dict["config_name"]):
            say(
                "Invalid config name. Check the list of config files using <Enter Config List Command>"
            )
            return False

        # Check if we want to run with old or new configs
        # If we are running with new config, then parse the arguments
        if args_dict["config_name"] == "new":
            self._run_cmd_process(args_dict)
        else:
            if isfile(
                join(
                    self.root_dir,
                    ".mlbot",
                    "configs",
                    "{}.pickle".format(args_dict["config_name"]),
                )
            ):
                with open(
                    join(
                        self.root_dir,
                        ".mlbot",
                        "configs",
                        "{}.pickle".format(args_dict["config_name"]),
                    ),
                    "rb",
                ) as f:
                    args_dict = pickle.load(f)
                    self._run_cmd_process(args_dict)
            else:
                print("Config file not present")
                say("Incorrect config file name")

    # Input format: "Get Process <config_name> <number of log file lines to tail - Optional>"
    # This function tails the logfile and send message on the slack channel
    def handle_get_process(self, message, say):
        msg_split = message["text"].split(" ")

        if len(msg_split) > 4:
            print(
                "Too many parameter given in SlackAPIHandler.handle_get_process function"
            )
            say("Enter only one config name")
        elif len(msg_split) == 4:
            config_name = msg_split[2]
            num_lines = msg_split[3]
            log_filepath = join(
                self.root_dir, ".mlbot", "logs", "{}.txt".format(config_name)
            )

            # Write proper error handling if this command throws some error
            p = subprocess.run(
                ["tail", "-n", str(num_lines), log_filepath],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            say(p.stdout.decode("utf-8"))
        elif len(msg_split) == 3:
            config_name = msg_split[2]
            log_filepath = join(
                self.root_dir, ".mlbot", "logs", "{}.txt".format(config_name)
            )

            # Write proper error handling if this command throws some error
            p = subprocess.run(
                ["tail", log_filepath],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            say(p.stdout.decode("utf-8"))
        else:
            print(
                "Config name not given in SlackAPIHandler.handle_get_process function"
            )
            say("Enter a config name")

    # Input format: "Stop Process <config_name>"
    def handle_stop_process(self, message, say):
        msg_split = message["text"].split(" ")

        if len(msg_split) > 3:
            print(
                "Too many parameters in SlackAPIHandler.handle_stop_function function"
            )
            say("Enter only one config name")
        elif len(msg_split) == 3:
            config_name = msg_split[2]

            try:
                p = self.process_obj_list.pop(config_name)
            except KeyError:
                print(
                    "Process with this config name is not running in SlackAPIHandler.handle_stop_process function"
                )
                say("Process with this config name is not running")
                return
            # Write proper error handling if this command throws some error
            # p.terminate()
            self._kill_process_using_pid(p.pid)
            # self._remove_pid_from_file(config_name)

        else:
            print(
                "Config name not given in SlackAPIHandler.handle_stop_process function"
            )
            say("Enter a config name")

    ## All args files related APIs

    # Input format: "Create Args <Config Name> <Config Parameters>"
    def handle_create_args(self, message, say):
        flag, args_dict = self.args_parser(message["text"].split(" "), say)

        if not flag:
            print(
                "Incorrect config file format in SlackAPIHandler.handle_create_args function"
            )
            return

        if isfile(
            join(
                self.root_dir,
                ".mlbot",
                "configs",
                "{}.pickle".format(args_dict["config_name"]),
            )
        ):
            print(
                "Config file already exists in SlackAPIHandler.handle_create_args function"
            )
            say("This config file already exists")
            return

        with open(
            join(
                self.root_dir,
                ".mlbot",
                "configs",
                "{}.pickle".format(args_dict["config_name"]),
            ),
            "wb",
        ) as f:
            pickle.dump(args_dict, f)

    # Input format: "Show Args"
    def handle_show_args(self, message, say):
        msg_split = message["text"].split(" ")

        if len(msg_split) == 2:
            config_list = listdir(join(self.root_dir, ".mlbot", "configs"))
            config_print_str = "List of config files:"

            for config in config_list:
                config_print_str = config_print_str + "\n" + config

            say(config_print_str)

        else:
            print(
                "Incorrect prompt format in SlackAPIHandler.handle_show_args function"
            )
            say("Incorrect prompt format. Expected input format: 'Show Args'")

    # Input format: "Delete Args <Config Name>"
    def handle_delete_args(self, message, say):
        msg_split = message["text"].split(" ")

        if len(msg_split) == 3:
            config_name = msg_split[2]

            if not isfile(
                join(
                    self.root_dir, ".mlbot", "configs", "{}.pickle".format(config_name)
                )
            ):
                print(
                    "Config file does not exist in SlackAPIHandler.handle_delete_args function"
                )
                say(
                    "Config file does not exist. Check out list of config files using 'Show Args'"
                )

                return

            config_filepath = join(
                self.root_dir, ".mlbot", "configs", "{}.pickle".format(config_name)
            )
            remove(config_filepath)
        else:
            print(
                "Incorrect prompt format in SlackAPIHandler.handle_delete_args function"
            )
            say(
                "Incorrect prompt format. Expected input format: 'Delete Args <Config Name>'"
            )

    def handle_update_args(self, message, say):
        pass

    # Slack Webhooks

    # Check if a process if stopped in every 5 secs, if yes, then send a message on the app


if __name__ == "__main__":
    a = SlackAPIHandler(None, None)
    # a.handle_run_process(None, None)
