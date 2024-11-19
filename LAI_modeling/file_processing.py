from pathlib import Path
from typing import Optional, List

import pandas as pd


CYAN = "\u001b[36m"
RED = "\u001b[31m"
RESET = "\033[0m"


def grab_files(directory: Path, extension: Optional[str] = None) -> List[Path]:
    """
    Recursively grabs files from the given directory and returns a list of
    file paths that match the given extension (if provided).
    
    Parameters:
    - directory (Path): Path to the directory to search.
    - extension (Optional[str]): Optional file extension filter (e.g., '.txt').

    Returns:
    - List[Path]: List of file paths matching the given criteria.
    """
    file_paths = []

    # Ensure that the directory exists and is a directory
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{CYAN}{directory}{RED} is not a valid directory.{RESET}")

    # Iterate over all files and subdirectories recursively
    for element in directory.rglob('*'):
        if element.is_file():
            if extension:
                # Filter by file extension if provided
                if element.suffix.lower() == extension.lower():
                    file_paths.append(element)
            else:
                file_paths.append(element)

    return file_paths


def ensure_directory_exists(directory_path: str) -> Path:
    """
    Ensure that the specified exists. If not, create it.

    Parameters:
       directory_path (str or Path): The path to the folder to check or create.

    Returns:
        Path: The Path object of the ensured directory.
    """
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def extract_date_from_filename(filename: Path) -> int:
    """
    TODO
    """
    # Extract the date string (YYYYDDD) from the filename
    date_str = filename.stem.split("_")[0]

    return date_str


def save_data_to_csv(
    dataframe: pd.DataFrame,
    filename: str,
    results_folder: str,
    ) -> None: 
    """
    Save the data from the provided DataFrame to a CSV file.

    This function saves the entire DataFrame as a CSV file. The user can
    specify the name of the file and the folder where the CSV will be stored.
    If no custom filename or folder is provided, the function will use the
    default settings. The DataFrame is saved without the index column.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing LAI data to be saved
        filename (str): The name of the CSV file.
        results_folder (str): Path to the folder where the CSV file 
                                        will be saved. 

    Returns:
        None

    Notes:
        - The function ensures that the specified results folder exists before
          attempting to save the file
        - The DataFrame is saved without the index column to keep the CSV clean
    """
    # Ensure the results folder exists
    directory_path = ensure_directory_exists(results_folder)

    # Formulate the full path to the output CSV file
    filepath = results_folder + "/" + filename

    # Save the DataFrame to a CSV file
    dataframe.to_csv(filepath, index=False)
