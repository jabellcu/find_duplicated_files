import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")

with app.setup:
    # Setup
    from pathlib import Path
    import pandas as pd
    import marimo as mo

    import hashlib
    import xxhash
    from tqdm import tqdm


@app.cell
def _():
    source_folder = Path(r'./Examples/Folder_1/')
    #source_folder = Path(r'./Examples/Folder_2/')
    output_folder = Path('Outputs')
    if not output_folder.exists(): output_folder.mkdir(parents=True)
    return output_folder, source_folder


@app.cell
def terms_excluded():
    terms_excluded_from_folders = ['.Trash', 'RECYCLE', '.Spotlight', '.fnmt']
    terms_excluded_from_files = ['.dll', '.dat', '.db', '.indexArrays', '.DS_Store', 'setup.exe', 'olyalbum.inf', 'Thumbnail.info', '.apple.timemachine']
    return terms_excluded_from_files, terms_excluded_from_folders


@app.cell
def _():
    hash_algorithm = 'md5'
    #hash_algorithm = 'xxh128'  # xxh128 is very fast, but has collisions with similar pictures
    # Actually, xxh128 might be useful to identify similar pictures.
    return (hash_algorithm,)


@app.cell
def _():
    #source_files = source_folder.glob('*.*')
    #source_files = [fp for fp in source_files if fp.is_file()]
    return


@app.function
def hash_file(path, digest='sha256'):
    # md5 is much faster, and probably enough
    try:
        with open(path, "rb") as f:
            return hashlib.file_digest(f, digest).hexdigest()
    except:
        return None


@app.cell
def _():
    ## Debug
    #list(map(lambda f: hash_file(f, 'md5'), source_files))
    return


@app.cell
def _():
    ## Debug
    #digest = getattr(xxhash, 'xxh128')  # xxh128 has collisions with similar pictures
    #source_files_hashes = list(map(lambda f: hash_file(f, digest), source_files))
    return


@app.function
def find_duplicates(folder_path, hash_digest='md5'):
    source_files = folder_path.rglob('*.*')
    #source_files = [fp for fp in source_files if fp.is_file()]

    print('Finding files')
    source_files = [fp for fp in tqdm(source_files) if fp.is_file()]

    #source_files = []
    #for fp in mo.status.progress_bar(
    #    source_files, 
    #    title="Finding files",
    #    show_eta=True,
    #    show_rate=True,
    #):
    #    if fp.is_file(): source_files.append(fp)

    try:
        digest = getattr(xxhash, hash_digest)  # xxh128 has collisions with similar pictures
    except AttributeError:
        digest = hash_digest
    #source_files_hashes = list(map(lambda f: hash_file(f, digest), source_files))

    print('Hashing')
    source_files_hashes = [hash_file(fp, digest) for fp in tqdm(source_files)]

    #source_files_hashes = []
    #for fp in mo.status.progress_bar(
    #    source_files, 
    #    title="Hashing",
    #    show_eta=True,
    #    show_rate=True,
    #):
    #    source_files_hashes.append(hash_file(fp, digest))

    df = pd.DataFrame({'file': source_files, 'hash': source_files_hashes})
    df['hash_count'] = df.groupby('hash')['file'].transform('count')
    df['folder'] = df['file'].map(lambda fp: str(fp.parent))
    df['file_name'] = df['file'].map(lambda fp: fp.name)
    df['file_name_count'] = df.groupby('file_name')['hash'].transform('count')

    return df


@app.cell
def _(hash_algorithm, source_folder):
    file_data = find_duplicates(source_folder, hash_algorithm)
    #file_data
    return (file_data,)


@app.cell
def _(file_data):
    file_data[['hash_count', 'file_name_count']].describe().T
    return


@app.cell
def _():
    ## Debug
    # Duplicated files (same hash, probably same content)
    #file_data.loc[file_data['hash_count'] > 1].sort_values(['hash_count', 'hash', 'file_name'], ascending=False)
    return


@app.function
def group_hashes(file_data: pd.DataFrame,
                 terms_excluded_from_folders: list = None,
                 terms_excluded_from_files: list = None,
                 minimum_duplicates = 0):
    '''Groups file data (file paths and hashes) by hash to identify where each unique content (i.e. hash) is stored.
    terms_excluded_from_folders - filter out folders including any of these terms.
    terms_excluded_from_files - filter out files including any of these terms.
    minimum_duplicates - filter out files with less duplicates. e.g. 0 will include al files, even if they are not duplicated. 1 will filter out files without duplicates.
    '''

    filtered = file_data.loc[file_data['hash_count'] > minimum_duplicates]

    if terms_excluded_from_folders:
        terms_excluded_from_folders_mask = ~filtered['folder'].astype(str).str.contains('|'.join(terms_excluded_from_folders), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_folders_mask]

    if terms_excluded_from_files:
        terms_excluded_from_files_mask = ~filtered['file_name'].astype(str).str.contains('|'.join(terms_excluded_from_files), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_files_mask]

    grouped = filtered.groupby(['hash', 'hash_count']).agg({'folder': set, 'file_name': set})
    grouped = grouped.rename(columns={'folder': 'unique_folders', 'file_name': 'unique_file_names'})
    grouped['unique_folders_count'] = grouped['unique_folders'].map(len)
    grouped['unique_file_names_count'] = grouped['unique_file_names'].map(len)

    grouped = grouped.sort_values(['unique_file_names', 'unique_folders'], key=lambda S: S.astype(str))

    return grouped


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    file_data_grouped = group_hashes(file_data, terms_excluded_from_folders, terms_excluded_from_files, minimum_duplicates=1)
    file_data_grouped
    return (file_data_grouped,)


@app.function
def duplicates_per_folder(file_data: pd.DataFrame,
                 terms_excluded_from_folders: list = None,
                 terms_excluded_from_files: list = None):
    '''Groups file_data by hash, and then by unique_folders. This makes it easy to identify folders sharing duplicated files. Each row is a list of folders sharing a list of files.'''
    file_data_grouped = group_hashes(file_data, terms_excluded_from_folders, terms_excluded_from_files, minimum_duplicates=1)
    file_data_grouped['unique_folders'] = file_data_grouped['unique_folders'].map('\n'.join)  # Allows using it for grouping
    dups_per_folder = file_data_grouped.groupby('unique_folders').agg({'unique_file_names': lambda S: set.union(*S.values) })
    dups_per_folder = dups_per_folder.rename(columns={'unique_file_names': 'shared_duplicates'})
    dups_per_folder['shared_duplicates_count'] = dups_per_folder['shared_duplicates'].map(len)
    return dups_per_folder


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    dups_per_folder = duplicates_per_folder(file_data, terms_excluded_from_folders, terms_excluded_from_files)
    dups_per_folder
    return


@app.function
def files_in_multiple_locations(file_data: pd.DataFrame,
                 terms_excluded_from_folders: list = None,
                 terms_excluded_from_files: list = None):
    '''Groups file data (file paths and hashes) by file name to identify folders containing files with the same name.'''

    filtered = file_data.loc[file_data['file_name_count'] > 1]

    if terms_excluded_from_folders:
        terms_excluded_from_folders_mask = ~filtered['folder'].astype(str).str.contains('|'.join(terms_excluded_from_folders), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_folders_mask]

    if terms_excluded_from_files:
        terms_excluded_from_files_mask = ~filtered['file_name'].astype(str).str.contains('|'.join(terms_excluded_from_files), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_files_mask]

    grouped = filtered.groupby(['file_name']).agg({'folder': set, 'hash': 'nunique'})
    grouped = grouped.rename(columns={'folder': 'unique_folders', 'hash': 'unique_hashes'})
    grouped['unique_folders_count'] = grouped['unique_folders'].map(len)
    return grouped


@app.cell
def _(file_data, terms_excluded_from_files, terms_excluded_from_folders):
    file_data_multiple_loc = files_in_multiple_locations(file_data, terms_excluded_from_folders, terms_excluded_from_files)
    #file_data_multiple_loc
    return


@app.function
def files_in_multiple_locations_grouped(file_data: pd.DataFrame,
                 terms_excluded_from_folders: list = None,
                 terms_excluded_from_files: list = None):
    '''Groups file data (file paths and hashes) by folders containing files with the same name.
    This makes it easy to spot duplicated folders (different folders with the same contents).'''

    filtered = file_data

    if terms_excluded_from_folders:
        terms_excluded_from_folders_mask = ~filtered['folder'].astype(str).str.contains('|'.join(terms_excluded_from_folders), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_folders_mask]

    if terms_excluded_from_files:
        terms_excluded_from_files_mask = ~filtered['file_name'].astype(str).str.contains('|'.join(terms_excluded_from_files), case=False, na=False)
        filtered = filtered.loc[terms_excluded_from_files_mask]

    file_data_multiple_loc = files_in_multiple_locations(filtered)
    file_data_multiple_loc['unique_folders'] = file_data_multiple_loc['unique_folders'].map(tuple)
    grp_cols = ['unique_folders', 'unique_folders_count']
    agg_cols = {'file_name': list, 'unique_hashes': 'sum'}
    grouped = file_data_multiple_loc.reset_index().groupby(grp_cols).agg(agg_cols)
    grouped = grouped.rename(columns={'file_name': 'file_names', 'unique_hashes': 'unique_hashes_sum'})
    return grouped


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
def _(
    file_data,
    file_data_grouped,
    file_data_multiple_loc_grouped,
    hash_algorithm,
    output_folder,
    source_folder,
):
    # Output
    file_data_ofp = output_folder / f'{source_folder.stem} {hash_algorithm}.csv'
    file_data.to_csv(file_data_ofp)

    file_data_grouped_ofp = output_folder / f'{source_folder.stem} {hash_algorithm} grouped.csv'
    file_data_grouped.to_csv(file_data_grouped_ofp)

    file_data_grouped_ofp = output_folder / f'{source_folder.stem} {hash_algorithm} dups per folder.csv'
    file_data_grouped.to_csv(file_data_grouped_ofp)

    file_data_multiple_loc_grouped_ofp = output_folder / f'{source_folder.stem} {hash_algorithm} duplicated folders grouped.csv'
    file_data_multiple_loc_grouped.to_csv(file_data_multiple_loc_grouped_ofp)
    return


if __name__ == "__main__":
    app.run()
