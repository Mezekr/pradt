from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from venv import main

project_dir = Path.cwd()


def create_dir(proj_dir: Path) -> None:
    data_dir = Path(proj_dir, "data")
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_data_dir = Path(data_dir, "raw").mkdir(parents=True, exist_ok=True)
    processed_data_dir = Path(data_dir, "processed").mkdir(parents=True, exist_ok=True)
    final_data_dir = Path(data_dir, "final").mkdir(parents=True, exist_ok=True)
    notebooks_dir = Path(proj_dir, "notebooks").mkdir(parents=True, exist_ok=True)

    print("Directories created successfully")


def main():
    project_dir = Path.cwd()
    create_dir(project_dir)


if __name__ == "__main__":
    main()
