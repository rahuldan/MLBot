from os.path import isfile, join

## To Do:
# Add more exhaustive check in the validation checker like *.py files


class ArgsParser(object):
    def __init__(self, config, root_dir):
        self.config = config
        self.root_dir = root_dir

    def _get_arg_type(self, arg):
        if arg[:2] == "--":
            return "long"
        elif arg[0] == "-":
            return "short"
        else:
            return "value"

    def check_if_valid_config(self, config_name):
        if config_name == "new":
            return True
        else:
            return isfile(join(self.root_dir, ".mlbot", "configs", config_name))

    # Format of message: <Process Command> <Config Name or "New" or "Last"> <Run File Relative Path> <Config Parameters>
    # If Config Name is "New", then the next argument should be the relative path of the run file
    # List of argument types:
    # -s            Simple Flag
    # --long        Long Flag
    # --key v1 v2   Parameter Value
    def __call__(self, args, say):
        # print("############ Args: ", args)
        start_idx = 4

        args_dict = {"config_name": args[2], "run_file": args[3]}
        arg_value = ""
        last_arg_name = ""

        for idx in range(start_idx, len(args)):
            arg_type = self._get_arg_type(args[idx])

            if idx == start_idx and arg_type == "value":
                say(
                    "Invalid format. Enter config parameters in `--key value_1 value_2` format"
                )
                return False, {}

            if arg_type == "long" or arg_type == "short":
                if idx != start_idx:
                    args_dict[last_arg_name] = arg_value
                arg_value = ""
                args_dict[args[idx]] = ""
                last_arg_name = args[idx]
            elif arg_type == "value":
                if arg_value == "":
                    arg_value = args[idx]
                else:
                    arg_value = arg_value + " " + args[idx]

        args_dict[last_arg_name] = arg_value

        return True, args_dict

    def check_if_valid_prompt(self, message, say, prompt):
        str_split = message["text"].split(" ")
        prompt_split = prompt.split(" ")

        if (str_split[0] == prompt_split[0]) and (str_split[1] == prompt_split[1]):
            return True
        else:
            say("Invalid Command. Send message '@MLBot --help' for documentation.")
            return False


if __name__ == "__main__":
    args_parser = ArgsParser(None, None)
    out_dict = args_parser(
        "Run Process new temp.py --param1 value1 --param2 value2_1 value2_2 -f --flag --param3 value3_1 value3_2",
        None,
    )
    print(out_dict)
