from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Optional, List

import pandas as pd
import numpy as np
import rasterio

TEMP_LAI_DIR = "temp\\temp_lai_processing"
DEFAULT_HDR_DRIVER = "ENVI"

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
      If not provided, all files are returned regardless of their extantion.

    Returns:
    - List[Path]: List of file paths matching the given criteria.
    """
    file_paths = []

    # Ensure that the directory exists and is a directory
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"{CYAN}{directory}{RED} is \
                         not a valid directory.{RESET}")

    # Iterate over all files and subdirectories recursively
    for element in directory.rglob('*'):
        if element.is_file():
            if extension:
                # Filter by file extension if provided
                if element.suffix.lower() == extension.lower():
                    file_paths.append(element)
            elif element.is_file() and element.suffix == "":
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

    # Ensure that the directory exists, if not create it
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def extract_date_from_filename_YYYY(filename: Path) -> int:
    """
    Extracts the year (YYYY) from the fik=lename. The filename is assumed to be
    structured such that the year is the last part after the last underscore.

    Parameters:
        filename (Path): The path object representing the filename

    Returns:
        int: The extracted year as an integer.
    """
    # Extract the date string (YYYY) from the filename
    date_str = filename.stem.split("_")[-1]

    # Ensure that the date string can be converted to an integer
    try:
        date_int = int(date_str)
    except:
        date_str = filename.stem.split("_")[-1]
        date_int = int(date_str)
    
    return date_int


def extract_date_from_filename(filename: Path) -> datetime:
    """
    Extract date from a filename assuming the pattern
    '<prefix>_<YYYYDDD>_suffix'.

    Parameters:
        filename (Path): Path object representing the filename contain the date

    Returns:
        datetime: The date object corresponding to the extracted date.
    """
    # Extract the date string (YYYYDDD) from the filename
    try:

        date_str = filename.stem.split("_")[1]

        # Validate the format of the extracted date string
        if len(date_str) != 7 or not date_str.isdigit():
            raise ValueError(f"Invalid date format in filename: {filename}")

        # Extract the year and day of year from the date string
        year = int(date_str[:4])
        day_of_year = int(date_str[4:7])

        # Calculate the date based on the year and day of year
        date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)

    except Exception as err:
        raise ValueError(f"Could not extract a valid date from filename \
                         {filename}. Error: {err}")

    return date


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
    filepath = os.path.join(results_folder, filename)

    try:

        # Save the DataFrame to a CSV file
        dataframe.to_csv(filepath, index=False)
    except Exception as err:
        raise IOError(f"An error occurred while saving the file: {err}")


def convert_hdr_to_tif(
    data_file_path: Path,
    temp_lai_folder_path: str = TEMP_LAI_DIR,
    driver: str = DEFAULT_HDR_DRIVER,
    ) -> Path:
    """
    Convert a HDR format raster file to TIFF format and save it in a specified
    temporary folder.

    Parameters:
       data_file_path (Path): Path to the HDR format raster file.
       temp_lai_folder_path (str, optional): Path to the temporary folder where
                the TIFF file will be saved.
                Defaults to 'temp\\temp_lai_processing'.
       driver (str, optional): Rasterio driver to open the HDR file.
                Defaults is 'ENVI'.

    Returns:
       Path: Full path to the converted TIF file saved in the temporary folder.

    Notes:
        - The function reads data from the HDR file, updates its profile for
          TIF format, and saves it in the specified temporary folder.
        - If the specified temporary folder does not exist, it will be created
          before saving the TIFF file.
    """
    try:
        with rasterio.open(data_file_path, "r", driver=driver) as src:
            # Read data from HDR file
            data = src.read(1)
            profile = src.profile

            # Replace values less than 0 with NaN
            data[data < 0] = np.nan

        # Update profile for saving in GTiff format
        profile.update(
                        driver="GTiff",
                        dtype=rasterio.float32,
                        count=1,
                        nodata=np.nan,
                        compress="lzw"
                    )

        # Formulate path to tif file based on HDR filename in the folder
        tiff_file_name = f"{Path(data_file_path).stem}.tif"
        out_tif_file = os.path.join(temp_lai_folder_path, tiff_file_name)

        # Save data in TIFF format
        with rasterio.open(out_tif_file, "w", **profile) as dst:
            dst.write(data.astype(rasterio.float32), 1)

        return out_tif_file
    
    except Exception as err:
        raise RuntimeError(f"Error occurred while converting {data_file_path}\
                           to tif: {err}")
