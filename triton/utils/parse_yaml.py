import sys

import yaml


def parse_yaml(file_path):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            if isinstance(value, list):
                value = " ".join(value)
            elif isinstance(value, bool):
                value = "true" if value else "false"
            print(f"{key.upper()}={value}")


if __name__ == "__main__":
    parse_yaml(sys.argv[1])
