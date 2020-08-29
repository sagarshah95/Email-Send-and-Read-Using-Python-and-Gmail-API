# This is a sample script to test that it sends emails notification of success and failure of job on exit
import sys
from exit_hooks import exit_hook


def main():
    print("Test")
    sys.exit(0)


if __name__ == "__main__":
    exit_hook("sample_script")
    main()
