#!python3
import json
import subprocess
import os
import time
import getopt
import sys
def info(info_str):
    """
    Print information log.

    :param info_str: str, the string to be printed.
    """
    print(f"[bidebug][info][{time.asctime()}] {info_str}", flush=True)


# Add a global verbose flag
verbose = False
def verbose_info(message):
    """
    Print verbose logs if verbose mode is enabled.

    :param message: str, the message to be printed.
    """
    if verbose:
        info(message)

def err(err_str):
    """
    Print error log.

    :param err_str: str, the string to be printed.
    """
    print(f"[bidebug][error][{time.asctime()}] {err_str}", flush=True)

def load_cfg(cfg_file_name):
    """
    Load a configuration file.

    This function reads a JSON configuration file specified by cfg_file_name. The expected format is:
    {
        "cmd": "command to execute",         # The shell command to run.
        "env_name": "environment variable",  # The name of the environment variable to change.
        "start": integer,                    # The starting value of the environment variable.
        "end": integer,                      # The ending value of the environment variable (must be greater than 'start').
        "pass_count": integer                # The number of successful command executions required to consider the test passed.
    }

    :param cfg_file_name: str, the path to the configuration file.
    :return: dict, the parsed dictionary object from the configuration file.
    :raises FileNotFoundError: If the configuration file cannot be found.
    :raises json.JSONDecodeError: If there is an error parsing the JSON.
    """
    try:
        with open(cfg_file_name, 'r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        err(f"Configuration file not found: {cfg_file_name}, use -h for help")
        sys.exit(1)
    except json.JSONDecodeError:
        err(f"Error decoding JSON from the configuration file: {cfg_file_name}")
        sys.exit(1)

def validate_cfg(cfg):
    """
    Validate the necessary fields in the configuration dictionary.

    :param cfg: dict, the configuration dictionary to validate.
    :return: bool, True if validation passes, otherwise False.
    """
    required_fields = ["cmd", "env_name", "start", "end", "pass_count"]
    missing_fields = [field for field in required_fields if field not in cfg]
    if missing_fields:
        err(f"Missing configuration fields: {', '.join(missing_fields)}")
        return False
    if not isinstance(cfg["start"], int) or not isinstance(cfg["end"], int) or not isinstance(cfg["pass_count"], int):
        err("Configuration fields 'start', 'end', and 'pass_count' must be integers.")
        return False
    if cfg["start"] >= cfg["end"]:
        err("Configuration field 'start' must be less than 'end'.")
        return False
    return True

def generate_config_template():
    """
    Generate a default configuration template.
    """
    config = {
        "cmd": "python3 test.py",
        "env_name": "TEST_ENV",
        "start": 1,
        "end": 100,
        "pass_count": 5
    }
    with open("bidebug_cfg.json", 'w') as f:
        json.dump(config, f, indent=4)
    info("Configuration template generated as 'bidebug_cfg.json'.")

def run_cmd(cmd_str, env_name, env_value, pass_count, quiet=False):
    verbose_info("start test with " + env_name + "=" + str(env_value))
    round = 0
    env = os.environ.copy()
    env[env_name] = str(env_value)
    while round < pass_count:
        verbose_info("round=" + str(round))
        if quiet:
            p = subprocess.Popen(cmd_str, shell=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            p = subprocess.Popen(cmd_str, shell=True, env=env)
        p.wait()
        if p.returncode == 0:
            round += 1
        else:
            verbose_info("test failed with " + env_name + "=" + str(env_value) + ", cnt=" + str(round))
            return 1
    verbose_info("test passed with " + env_name + "=" + str(env_value))
    return 0


def bidebug(cfg, quiet=False):
    """
    Use binary search method for debugging.

    :param cfg: dict, contains debugging configuration dictionary.
    """
    cmd = cfg["cmd"]
    env_name = cfg["env_name"]
    start = int(cfg["start"])
    end = int(cfg["end"])
    pass_count = int(cfg["pass_count"])

    start_ret = run_cmd(cmd, env_name, start, pass_count, quiet) if "start_ret" not in cfg else int(cfg["start_ret"])
    end_ret = run_cmd(cmd, env_name, end, pass_count, quiet) if "end_ret" not in cfg else int(cfg["end_ret"])

    info("start_ret=" + str(start_ret))
    info("end_ret=" + str(end_ret))

    if start_ret == end_ret:
        err("Error, no transition found as start_ret equals end_ret")
        return

    while start < end:
        mid = (start + end) // 2
        mid_ret = run_cmd(cmd, env_name, mid, pass_count, quiet)

        info(f"Checking mid point {mid} with result {mid_ret}")

        # When the mid value returns the same result as the start, increase the start
        if mid_ret == start_ret:
            start = mid + 1
        else:
            end = mid

        info(f"Updated search range - start: {start}, end: {end}")
        # If the range is narrowed down to two adjacent values, check for the transition directly
        if start + 1 == end:
            if run_cmd(cmd, env_name, end, pass_count, quiet) != start_ret:
                info(f"Transition found at {end}")
                return end
            else:
                err("Error, no transition found after exhaustive search")
                return

    # If end becomes equal to start, the transition should be at start
    info(f"Transition found at {start}")
    return start


def seqDebug(cfg, quiet=False):
    cmd = cfg["cmd"]
    env_name = cfg["env_name"]
    start = int(cfg["start"])
    end = int(cfg["end"])
    pass_count = int(cfg["pass_count"])

    last_code = run_cmd(cmd, env_name, start, pass_count, quiet)
    for i in range(start+1, end):
        this_code = run_cmd(cmd, env_name, i, pass_count, quiet)
        if last_code != this_code:
            return i
        last_code = this_code
    err("error, can not find")
    



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Binary or Sequential Debugging Tool",
                                     epilog="Example: python script.py --config myconfig.json --quiet")
    parser.add_argument("-c", "--config", metavar="FILE", default="bidebug_cfg.json",
                        help="specify the configuration file (default: bidebug_cfg.json)")
    parser.add_argument("-s", "--sequential", action="store_true",
                        help="use sequential debugging instead of binary search")
    parser.add_argument("--version", action="version", version="Bidebug v1.0")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress command output")
    parser.add_argument("--dry-run", action="store_true", help="simulate command execution without running commands")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")
    parser.add_argument("-g", "--generate-config", action="store_true",
                        help="generate a default configuration template in the current directory")

    args = parser.parse_args()

    cfg_file_name = args.config
    seq = args.sequential
    dry_run = args.dry_run
    verbose = args.verbose

    if args.generate_config:
        generate_config_template()
        sys.exit(0)

    cfg = load_cfg(cfg_file_name)
    if not validate_cfg(cfg):
        sys.exit(1)
    info(str(cfg))

    if dry_run:
        info("Dry-run mode enabled. No commands will be executed.")
    else:
        if not seq:
            info("result:" + str(bidebug(cfg, args.quiet)))
        else:
            info("result:" + str(seqDebug(cfg, args.quiet)))
