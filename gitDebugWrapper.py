import subprocess
import os
import argparse

def collect_commits(repo_dir, quiet=False):
    """
    Collect all Git commits in the specified repository and save them to a file named 'commit_logs'
    in the current working directory.
    """
    original_cwd = os.getcwd()
    os.chdir(repo_dir)
    try:
        result = subprocess.run(['git', 'log', '--pretty=format:%H'], 
                                capture_output=True, text=True, check=True)
        os.chdir(original_cwd)
        with open('commit_logs', 'w') as file:
            file.write(result.stdout)
        if not quiet:
            print(f"Commits collected and saved to 'commit_logs'.")
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Failed to collect commits: {e}")
    finally:
        os.chdir(original_cwd)

def set_to_commit(commit, repo_dir, quiet=False):
    """
    Check out to the specified commit in the given repository directory.
    """
    os.chdir(repo_dir)
    subprocess.run(['git', 'checkout', commit], 
                   check=True, 
                   stdout=subprocess.DEVNULL if quiet else None, 
                   stderr=subprocess.DEVNULL if quiet else None)
    if not quiet:
        print(f"Checked out to commit {commit}.")
    os.chdir(os.path.dirname(repo_dir))  # Return to the main directory

def build_project(build_dir, build_cmd='ninja -j10', quiet=False):
    """
    Build the project in the specified build directory using the provided build command.
    """
    os.chdir(build_dir)
    subprocess.run(build_cmd, shell=True, check=True, 
                   stdout=subprocess.DEVNULL if quiet else None, 
                   stderr=subprocess.DEVNULL if quiet else None)
    if not quiet:
        print(f"Project built using command: {build_cmd}")
    os.chdir(os.path.dirname(build_dir))  # Return to the main directory

def test_commit(n, cmd, repo_dir, build_dir, quiet=False):
    """
    Test a specific commit by checking out, compiling, and running a command.
    """
    commit = get_commit(n)
    set_to_commit(commit, repo_dir, quiet)
    build_project(build_dir, 'ninja -j10', quiet)
    return run_cmd(cmd, quiet)

def run_cmd(cmd, quiet):
    """
    Execute a command with optional quiet mode.
    """
    return subprocess.run(cmd, shell=True, 
                          stdout=subprocess.DEVNULL if quiet else None, 
                          stderr=subprocess.DEVNULL if quiet else None).returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Git Debugging Tool")
    parser.add_argument('number', nargs='?', type=int, help="The number of the commit to test")
    parser.add_argument('-r', '--repo', required=True, help="Path to the Git repository")
    parser.add_argument('-d', '--build-dir', required=True, help="Path to the build directory")
    parser.add_argument('-g', '--generate', action='store_true', help="Collect commits and generate cfg template")
    parser.add_argument('-c', '--command', type=str, help="Command to execute on the git commit", default="make test")
    parser.add_argument('-q', '--quiet', action='store_true', help="Enable quiet mode, which suppresses all output")
    parser.add_argument('-b', '--build', type=str, default="ninja -j10", help="Build command to use in the build directory")

    args = parser.parse_args()

    if args.generate:
        collect_commits(args.repo, args.quiet)
    elif args.number:
        result = test_commit(args.number, args.command, args.repo, args.build_dir, args.quiet)
        if not args.quiet:
            print("Test result:", "Success" if result else "Failure")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
