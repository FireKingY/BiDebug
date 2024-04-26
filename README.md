# Bidebug

`Bidebug` is a Python-based debugging tool designed to help developers identify the exact point at which the behavior of a shell command changes due to modifications in environment variable settings. It supports both binary and sequential search methods.

## Features

- **Binary Search Debugging**: Quickly narrows down the range of values to find the precise change point.
- **Sequential Search Debugging**: Sequentially tests each value to identify when the output changes.
- **Configurable**: Allows users to define custom configurations through a JSON file.

## Installation

Clone this repository or download the script:

```bash
git clone https://github.com/FireKingY/BiDebug
```

Ensure Python 3 is installed on your system.

## Usage

### Generating Configuration File

To generate a default configuration template, run:

```bash
python bidebug.py --generate-config
```

This command creates a `bidebug_cfg.json` file with default values in your current directory, which you can modify according to your needs.


### Running the Tool

To start debugging, use the following command:

```bash
python bidebug.py --config your_config_file.json
```

Additional options:

- **--sequential**: Use sequential debugging instead of binary search.
- **-q, --quiet**: Suppress command output.
- **-v, --verbose**: Enable verbose output.
- **--dry-run**: Simulate command execution without running the actual commands.

## Configuration Details

The configuration file (`bidebug_cfg.json`) is a JSON-formatted file that specifies how `Bidebug` should operate. Below are the fields that can be set in the configuration file:

- **cmd**: The shell command that `Bidebug` will execute during debugging. This should be a command whose output or behavior changes based on environment variables.
- **env_name**: The name of the environment variable that will be modified during the debugging process.
- **start**: The starting value of the environment variable. This is the initial point from which the debugging process will either start incrementing (sequential) or use as a baseline for binary search.
- **end** (optional): The ending value of the environment variable for sequential debugging. If not specified for binary search, the script will exponentially find a range where the behavior of the command changes.
- **pass_count** (optional): The number of times the command must execute successfully (exit code 0) before considering the test at a specific environment variable setting as passed. Defaults to 1 if not specified.

### Example Configuration

Here is an example of a configuration file that sets the environment variable `TEST_ENV` for the command `python3 test.py`, starting from 1 and ending at 100, requiring each test to pass 5 times before moving on:

```json
{
    "cmd": "python3 test.py",
    "env_name": "TEST_ENV",
    "start": 1,
    "end": 100,
    "pass_count": 5
}
```

This configuration will help `Bidebug` to systematically test how changes in `TEST_ENV` from 1 to 100 affect the behavior of `python3 test.py`, ensuring robustness in the testing phase by requiring multiple successful executions.

### Examples

Run binary search debugging:

```bash
python bidebug.py --config bidebug_cfg.json
```

Run sequential search debugging:

```bash
python bidebug.py --config bidebug_cfg.json --sequential
```

Enable verbose mode:

```bash
python bidebug.py --config bidebug_cfg.json --verbose
```