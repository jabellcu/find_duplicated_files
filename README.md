# Find duplicated files

Just some `marimo` notebooks to find duplicated files and analyse the results:

- `find_dups.py` is the main file. It will find files in a folder and hash their contents. It will then output a csv file with the files' data (locations and their hashes). It will also output other csv files with useful statistics to find duplicated files or files with the same name in different locations.
- `analyse_dups_found.py` is an auxiliary file to re-run analyses on files' data.
- `relate_hashes_found.py` is an auxiliary file to compare files across different folders and find matches (common files and folders) and missing files and folders.

There are other libraries and programs. `find_duplicated_files` has the advantage of being free, use files'content and not just their names, and be simple enough to tinker with it: feel free to adapt it to your needs.

This has been useful to me to explore and sort out my hard drives with copies of pictures.


## Installation

None needed. Just download the code or clone the repo.


## How to run

The .py files are just `marimo` notebooks. Open them with `marimo`:

    $ marimo edit find_dups.py

I recommend using `uv` to get all dependencies:

    $ uv run marimo edit find_dups.py

Inside the notebook just set the variables as you need. They are all on top, at the beginning. By default, the notebook will use one of the examples provided:

    source_folder = Path(r'./Examples/Folder_1/')

You can then do the same with the rest of the notebooks. Results will be stored on folder 'Outputs' by default.
