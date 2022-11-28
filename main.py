from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import os
from os.path import join
from os import listdir
import glob
import random
import yaml
import pickle
from dotenv import load_dotenv
from flask import Flask, request
import sys

from slackapihandler import SlackAPIHandler
from flaskapihandler import FlaskAPIHandler
from utils.argsparser import ArgsParser

root_dir = ""

if getattr(sys, "frozen", False):
    root_dir = os.path.dirname(sys.executable)
elif __file__:
    root_dir = os.path.dirname(__file__)

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]

flask_app = Flask(__name__)
slack_app = App(token=SLACK_BOT_TOKEN)

config = yaml.load(
    open(join(root_dir, ".mlbot", "config.yaml"), "r"),
    Loader=yaml.FullLoader,
)

arg_parser = ArgsParser(config, root_dir)

slack_api_handler = SlackAPIHandler(config, root_dir)
flask_api_handler = FlaskAPIHandler(config, root_dir)

### Slack APIs


## Process APIs


@slack_app.event("app_mention")
def handle_app_mention(message, say):
    slack_api_handler.handle_app_mention(message, say)


@slack_app.message("Run Process")
def handle_run_process(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Run Process"):
        slack_api_handler.handle_run_process(message, say)


@slack_app.message("Get Process")
def handle_get_process(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Get Process"):
        slack_api_handler.handle_get_process(message, say)


@slack_app.message("Stop Process")
def handle_stop_process(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Stop Process"):
        slack_api_handler.handle_stop_process(message, say)


## Args APIs


@slack_app.message("Create Args")
def handle_create_args(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Create Args"):
        slack_api_handler.handle_create_args(message, say)


@slack_app.message("Show Args")
def handle_show_args(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Show Args"):
        slack_api_handler.handle_show_args(message, say)


@slack_app.message("Delete Args")
def handle_delete_args(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Delete Args"):
        slack_api_handler.handle_delete_args(message, say)


@slack_app.message("Update Args")
def handle_update_args(message, say):
    if arg_parser.check_if_valid_prompt(message, say, "Update Args"):
        slack_api_handler.handle_update_args(message, say)


# Flask APIs
"""

@flask_app.route("/services/run_process", methods=["POST"])
def run_process():
    # Run a new process with given hparams
    pass


@flask_app.route("/services/stop_process", methods=["POST"])
def stop_process():
    # Stop a process when queried with a PID, otherwise send list of PIDs
    pass


@flask_app.route("/services/get_process_list", methods=["GET"])
def get_process_list():
    # Get list of all running process
    pass


@flask_app.route("/services/get_process_stats", methods=["GET"])
def get_process_stat():
    # Get train & eval stats of a running process when queried with a PID, otherwise send list of PIDs
    pass


# @flask_app.route("/services/get_ckpt_list", methods=["GET"])
def get_ckpt_list():
    # Get the list of last 5 ckpt
    pass
"""

if __name__ == "__main__":
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()

    # flask_app.run(host="localhost", port=8080, debug=False)
