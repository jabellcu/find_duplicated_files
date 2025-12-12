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
    This notebook relates files produced by find_dups.py. This allows to find matching content (files' hashes) across multiple drives, avoiding duplicates.
    """)
    return


@app.cell
def _():
    terms_excluded_from_folders = ['.Trash', 'RECYCLE', '.Spotlight', '.fnmt']
    terms_excluded_from_files = ['.dll', '.dat', '.db', '.indexArrays', '.DS_Store', 'setup.exe', 'olyalbum.inf', 'Thumbnail.info', '.apple.timemachine']
    return terms_excluded_from_files, terms_excluded_from_folders


@app.cell
def _():
    TARGET_EXTENSION = '.txt'  # Focus on these files, filter out everything else
    return (TARGET_EXTENSION,)


@app.cell
def _():
    source_file_1 = Path(r'./Outputs/Folder_1.csv')  # Reference folder
    source_file_2 = Path(r'./Outputs/Folder_2.csv')

    output_folder = Path('Outputs')
    if not output_folder.exists(): output_folder.mkdir(parents=True)
    return output_folder, source_file_1, source_file_2


@app.cell
def _(source_file_1, source_file_2):
    file1_data = pd.read_csv(source_file_1)
    file2_data = pd.read_csv(source_file_2)
    return file1_data, file2_data


@app.cell
def _(
    file1_data,
    file2_data,
    terms_excluded_from_files,
    terms_excluded_from_folders,
):
    file1_data_grouped = group_hashes(file1_data, terms_excluded_from_folders, terms_excluded_from_files, minimum_duplicates=0).reset_index()
    file2_data_grouped = group_hashes(file2_data, terms_excluded_from_folders, terms_excluded_from_files, minimum_duplicates=0).reset_index()
    return file1_data_grouped, file2_data_grouped


@app.cell
def _(file1_data_grouped, file2_data_grouped, source_file_1, source_file_2):
    file_data_merged = file1_data_grouped.merge(file2_data_grouped, how='outer', left_on='hash', right_on='hash', suffixes=[f' {source_file_1.stem}', f'{source_file_2.stem}'], indicator=True)
    #file_data_merged
    return (file_data_merged,)


@app.cell
def _(TARGET_EXTENSION, file_data_merged, source_file_1):
    target_files_mask = file_data_merged[f'unique_file_names {source_file_1.stem}'].astype(str).str.contains(TARGET_EXTENSION, case=False)
    file_data_merged_filtered = file_data_merged.loc[target_files_mask]
    file_data_merged_filtered
    return (file_data_merged_filtered,)


@app.cell
def _(file_data_merged_filtered, source_file_1):
    # Folders in source_file_1 missing in source_file_2
    missing_folders = file_data_merged_filtered.copy()
    missing_folders[f'unique_folders {source_file_1.stem}'] = missing_folders[f'unique_folders {source_file_1.stem}'].map('\n'.join)  # Allows using it for grouping
    missing_folders = missing_folders.loc[file_data_merged_filtered['_merge']=='left_only'].groupby(f'unique_folders {source_file_1.stem}').agg({f'unique_file_names {source_file_1.stem}': lambda S: set.union(*S.values)})
    missing_folders[f'unique_file_names {source_file_1.stem} count'] = missing_folders[f'unique_file_names {source_file_1.stem}'].map(len)
    missing_folders
    return (missing_folders,)


@app.cell
def _(file_data_merged_filtered, source_file_1):
    common_folders = file_data_merged_filtered.copy()
    common_folders[f'unique_folders {source_file_1.stem}'] = common_folders[f'unique_folders {source_file_1.stem}'].map('\n'.join)  # Allows using it for grouping
    common_folders = common_folders.loc[file_data_merged_filtered['_merge']=='both'].groupby(f'unique_folders {source_file_1.stem}').agg({f'unique_file_names {source_file_1.stem}': lambda S: set.union(*S.values)})
    common_folders[f'unique_file_names {source_file_1.stem} count'] = common_folders[f'unique_file_names {source_file_1.stem}'].map(len)
    common_folders
    return (common_folders,)


@app.cell
def _(
    common_folders,
    file_data_merged_filtered,
    missing_folders,
    output_folder,
    source_file_1,
    source_file_2,
):
    # Output
    file_data_merged_filtered_ofp = output_folder / f'{source_file_1.stem} - {source_file_2.stem} merged filtered.csv'
    file_data_merged_filtered.to_csv(file_data_merged_filtered_ofp)

    missing_folders_ofp = output_folder / f'{source_file_1.stem} - {source_file_2.stem} missing folders.csv'
    missing_folders.to_csv(missing_folders_ofp)

    common_folders_ofp = output_folder / f'{source_file_1.stem} - {source_file_2.stem} common folders.csv'
    common_folders.to_csv(common_folders_ofp)
    return


if __name__ == "__main__":
    app.run()
