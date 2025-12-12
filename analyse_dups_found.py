import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from pathlib import Path
    import pandas as pd
    from find_dups import find_duplicates, group_hashes, duplicates_per_folder, files_in_multiple_locations, files_in_multiple_locations_grouped


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    This notebook applies analysis functions to a file_data file produced by find_dups.py. This is useful because hashing data in find_dups.py is computationally expensive. Analyses are updated more frequently, or tailored for different projects. This notebooks allows to run these funcitons without running the whole find_dups.py again.
    """)
    return


@app.cell
def _():
    terms_excluded_from_folders = ['.Trash', 'RECYCLE', '.Spotlight', '.fnmt']
    terms_excluded_from_files = ['.dll', '.dat', '.db', '.indexArrays', '.DS_Store', 'setup.exe', 'olyalbum.inf', 'Thumbnail.info', '.apple.timemachine']
    return terms_excluded_from_files, terms_excluded_from_folders


@app.cell
def _():
    source_file = Path(r'./Outputs/Folder_1.csv')
    return (source_file,)


@app.cell
def _(source_file):
    file_data = pd.read_csv(source_file)
    return (file_data,)


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    file_data_grouped = group_hashes(file_data, terms_excluded_from_folders, terms_excluded_from_files, minimum_duplicates=1)
    file_data_grouped
    return (file_data_grouped,)


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    dups_per_folder = duplicates_per_folder(file_data, terms_excluded_from_folders, terms_excluded_from_files)
    dups_per_folder
    return


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    file_data_multiple_loc = files_in_multiple_locations(file_data, terms_excluded_from_folders, terms_excluded_from_files)
    #file_data_multiple_loc
    return


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    file_data_multiple_loc_grouped = files_in_multiple_locations_grouped(file_data, terms_excluded_from_folders, terms_excluded_from_files)
    file_data_multiple_loc_grouped
    return (file_data_multiple_loc_grouped,)


@app.cell
def _():
    # Files with the same name (not necesarily duplicated)
    #file_data.loc[file_data['file_name_count'] > 1].sort_values('file_name_count', ascending=False)
    return


@app.cell
def _(file_data_grouped, file_data_multiple_loc_grouped, source_file):
    file_data_grouped_ofp = source_file.with_name(f'{source_file.stem} grouped.csv')
    file_data_grouped.to_csv(file_data_grouped_ofp)

    file_data_grouped_ofp = source_file.with_name(f'{source_file.stem} dups per folder.csv')
    file_data_grouped.to_csv(file_data_grouped_ofp)

    file_data_multiple_loc_grouped_ofp = source_file.with_name(f'{source_file.stem} duplicated folders grouped.csv')
    file_data_multiple_loc_grouped.to_csv(file_data_multiple_loc_grouped_ofp)
    return


if __name__ == "__main__":
    app.run()
