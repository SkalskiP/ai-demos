from __future__ import annotations

import argparse

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

NOTEBOOKS_ROOT_PATH = "https://github.com/SkalskiP/ai-demos/blob/main/notebooks"
NOTEBOOKS_COLAB_ROOT_PATH = "github/SkalskiP/ai-demos/blob/main/notebooks"

WARNING_HEADER = [
    "<!---",
    "   WARNING: DO NOT EDIT THIS TABLE MANUALLY. IT IS AUTOMATICALLY GENERATED.",
    "   HEAD OVER TO CONTRIBUTING.MD FOR MORE DETAILS ON HOW TO MAKE CHANGES PROPERLY.",
    "-->"
]

TABLE_HEADER = [
    "| **project** | **open in colab** |",
    "|:------------:|:----------------:|"
]

NOTEBOOK_LINK_PATTERN = "[{}]({}/{})"
OPEN_IN_COLAB_BADGE_PATTERN = "[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/{}/{})"

AUTOGENERATED_NOTEBOOKS_TABLE_TOKEN = "<!--- AUTOGENERATED-NOTEBOOKS-TABLE -->"


@dataclass(frozen=True)
class TableEntry:
    display_name: str
    notebook_name: str

    @classmethod
    def from_csv_line(cls, csv_line: str) -> TableEntry:
        csv_fields = [
            field.strip()
            for field
            in csv_line.split(",")
        ]
        if len(csv_fields) != 2:
            raise Exception("Every csv line must contain 2 fields")
        return TableEntry(
            display_name=csv_fields[0],
            notebook_name=csv_fields[1]
        )

    def format(self) -> str:
        notebook_link = NOTEBOOK_LINK_PATTERN.format(self.display_name, NOTEBOOKS_ROOT_PATH, self.notebook_name)
        open_in_colab_badge = OPEN_IN_COLAB_BADGE_PATTERN.format(NOTEBOOKS_COLAB_ROOT_PATH, self.notebook_name)
        return f"| {notebook_link} | {open_in_colab_badge} |"


def read_lines_from_file(path: str) -> List[str]:
    with open(path) as file:
        return [line.rstrip() for line in file]


def parse_csv_lines(csv_lines: List[str]) -> List[TableEntry]:
    return [
        TableEntry.from_csv_line(csv_line=csv_line)
        for csv_line
        in csv_lines
    ]


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def inject_markdown_table_into_readme(readme_lines: List[str], table_lines: List[str]) -> List[str]:
    lines_with_token_indexes = search_lines_with_token(lines=readme_lines, token=AUTOGENERATED_NOTEBOOKS_TABLE_TOKEN)
    if len(lines_with_token_indexes) != 2:
        raise Exception(f"Please inject two {AUTOGENERATED_NOTEBOOKS_TABLE_TOKEN} "
                        f"tokens to signal start and end of autogenerated table.")

    [table_start_line_index, table_end_line_index] = lines_with_token_indexes
    return readme_lines[:table_start_line_index + 1] + table_lines + readme_lines[table_end_line_index:]


def save_lines_to_file(path: str, lines: List[str]) -> None:
    with open(path, "w") as f:
        for line in lines:
            f.write("%s\n" % line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', default='automation/notebooks-table-data.csv')
    parser.add_argument('-r', '--readme_path', default='README.md')
    args = parser.parse_args()

    csv_lines = read_lines_from_file(path=args.data_path)[1:]
    readme_lines = read_lines_from_file(path=args.readme_path)
    table_entries = parse_csv_lines(csv_lines=csv_lines)
    notebook_lines = [
        entry.format()
        for entry
        in table_entries
    ]

    table_lines = WARNING_HEADER + TABLE_HEADER + notebook_lines
    readme_lines = inject_markdown_table_into_readme(readme_lines=readme_lines, table_lines=table_lines)
    save_lines_to_file(path=args.readme_path, lines=readme_lines)
