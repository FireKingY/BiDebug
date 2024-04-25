# Binary and Sequential Debugging Tool

This Python script facilitates the debugging of applications through environmental variables using both binary and sequential search methodologies.

## Features

- **Binary Debugging**: Quickly locates the transition point where application behavior changes due to configuration.
- **Sequential Debugging**: Iteratively tests each configuration to pinpoint the exact point of failure.
- **Configuration Template Generation**: Automatically generates a default configuration file template.
- **Verbose Logging**: Supports both normal and verbose logging modes to provide detailed tracking of the debugging process.
- **Dry Run Mode**: Simulates the debugging process without executing actual commands, ideal for testing setups.

## Installation

No special installation steps are required—simply download the script and it is ready to use.

## Usage

### Generate Configuration File

Generate a default configuration file using the `-g` option:

```bash
python script.py -g
```

This will create a file named `bidebug_cfg.json` in the current directory.

### Edit Configuration File

Modify `bidebug_cfg.json` as needed. Each field in the configuration file is explained below:

- **cmd**: The shell command to be executed for testing. It should be a command that can be influenced by changing the `env_name` variable.
- **env_name**: The name of the environment variable that the script will modify during the debugging process.
- **start**: The starting value of the environment variable; this should be the lower bound of the range you believe the transition might occur.
- **end**: The ending value of the environment variable; this should be the upper bound of the range. It must be greater than the `start` value.
- **pass_count**: The number of times the command must execute successfully (i.e., exit with a status of 0) before considering the current environment setting as stable.

Here's an example of how to configure these settings:

```json
{
    "cmd": "python3 test.py",
    "env_name": "TEST_ENV",
    "start": 1,
    "end": 100,
    "pass_count": 5
}
```

### Start Debugging

Launch the debugging process using the `-c` option to specify the configuration file:

```bash
python script.py -c bidebug_cfg.json
```

Optional parameters:
- `-s` to use sequential debugging instead of the default binary search.
- `-q` for quiet mode, which reduces log output.
- `-v` for verbose mode, which provides detailed output during the debugging process.
- `--dry-run` to simulate the command execution without actually running the commands.
