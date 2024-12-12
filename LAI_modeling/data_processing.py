from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from file_processing import (
                             grab_files,
                             ensure_directory_exists,
                             extract_date_from_filename,
                             extract_date_from_filename_YYYY,
                             save_data_to_csv,
                             convert_hdr_to_tif
                             )
from plotting import plot_comparison_of_two_lai_datasets
from raster_processing import (
                               clip_raster_by_shapefile,
                               create_template_raster,
                               copy_data_to_template,
                               read_raster,
                               generate_lai_raster,
                               save_data_to_raster,
                              )

TEMP_DIR = "Temp"
OUTPUT_DIR = "Result"
DEFAULT_TEMP_RASTER_NAME = "template_raster.tif"
DEFAULT_TEMP_LAI_DIR ="temp\\temp_lai_unifited"
DEFAULT_TEMP_LANDUSE_2 ="temp\\new_landuse_2.tif"
TEMP_LAI_DIR = "temp\\temp_lai_processing"


DEFAULT_LAI_FILENAME = "stat_lai_2020.csv"
DEFAULT_LAI_FILENAME_new = "stat_lai_predicted.csv"

DEFAULT_LAI_FILENAME_new_by_class = "stat_lai_new_by_class.csv"
DEFAULT_PLOT_OUTPUT_DIR = "Result\\plot"
CLASS_REPLACEMENT_DICT = {
    611: 610,
    612: 610,
    613: 610
}


def calculate_lai_statistic(
        lai_data: np.array,
        landuse_data: np.array,
        landuse_class: int
        ) -> dict:
    """
    Calculates LAI statistics for a specific land use class.

    Parameters:
    - lai_data (numpy.ndarray): Array containing LAI values.
    - landuse_data (numpy.ndarray):
      Array containing land use class identifiers for each pixel.
    - landuse_class (int):
      The specific land use class for which statistics are calculated.

    Returns:
    - dict: A dictionary containing the following statistics:
        - 'mean_lai' (float): Mean LAI value for the specified class.
        - 'Q1' (float): First quartile of the LAI values.
        - 'Q2' (float): Median (second quartile) of the LAI values.
        - 'Q3' (float): Third quartile of the LAI values.
        - 'min' (float): Minimum LAI value.
        - 'max' (float): Maximum LAI value.
        - 'pixel_count' (int):
          Number of pixels belonging to the specified class.
    """
    mask = (landuse_data == landuse_class)

    if np.any(mask):
        filtered_lai_data = lai_data[mask]

        mean_lai = np.mean(filtered_lai_data)
        Q1 = np.percentile(filtered_lai_data, 25)
        Q2 = np.percentile(filtered_lai_data, 50)
        Q3 = np.percentile(filtered_lai_data, 75)
        min_val = np.min(filtered_lai_data)
        max_val = np.max(filtered_lai_data)
        pixel_count = np.sum(mask)

        return {
            'Mean': mean_lai,
            'Q1': Q1,
            'Median': Q2,
            'Q3': Q3,
            'Min': min_val,
            'Max': max_val,
            'Pixel_count': pixel_count
        }


def process_lai_files_and_extract_data(
    unified_lai_list: List[Path],
    land_use_file_path: str,
) -> pd.DataFrame:
    """
    Processes LAI raster files and extracts statistical data for each land use class.

    Parameters:
    - unified_lai_list (List[Path]):
      A list of paths to LAI raster files to be processed.
    - land_use_file_path (str):
      The path to the raster file containing land use class ifications.

    Returns:
    - pd.DataFrame: A pandas DataFrame containing the following columns for
      each LAI file:
        - 'Date' (str): The date extracted from the LAI file name.
        - 'Landuse' (int): The unique land use class identifier for each land
          use class in the raster.
        - 'Mean' (float): Mean LAI value for the land use class.
        - 'Min' (float): Minimum LAI value for the land use class.
        - 'Q1' (float): First quartile (25th percentile) of the LAI values for
          the land use class.
        - 'Median' (float): Median (50th percentile) of the LAI values for the
          land use class.
        - 'Q3' (float): Third quartile (75th percentile) of the LAI values for
          the land use class.
        - 'Max' (float): Maximum LAI value for the land use class.
        - 'Pixel_count' (int): Number of pixels belonging to the specified
          land use class.
    """
    # Read the land use data from the specified raster file
    landuse = read_raster(Path(land_use_file_path))
    
    # Get unique land use classes present in the raster, excluding the class '0'
    unique_classes_raw = np.unique(landuse)
    unique_landuse_classes = unique_classes_raw[unique_classes_raw != 0]

    # Initializade a list to store the extracted statistics for each LAI file
    data = []

    # Iterate over each LAI file in the provided list
    for lai_file in unified_lai_list:

        # Extract date information from the LAI file name
        date = str(extract_date_from_filename(lai_file)) 

        # Read LAI data from the current file
        lai_data = read_raster(lai_file)

        # Loop through each unique land use class
        for landuse_class in unique_landuse_classes:

            # Calculate mean LAI and boxplot statistics for the current
            # land use and elevation class
            stats = calculate_lai_statistic(
                lai_data, landuse, landuse_class
            )

            # If valid statistics were returned, add them to the data list
            if stats is not None:
                data.append(
                    [
                        date,
                        int(landuse_class),
                        stats["Mean"],
                        stats["Min"],
                        stats["Q1"],
                        stats["Median"],
                        stats["Q3"],
                        stats["Max"],
                        stats["Pixel_count"]
                    ]
                )

    # Create a DataFrame from the collected data with specified columns names
    data_frame = pd.DataFrame(
        data,
        columns=[
            "Date",
            "Landuse",
            "Mean",
            "Min",
            "Q1",
            "Median",
            "Q3",
            "Max",
            "Pixel_count",
        ],
    )

    return data_frame


def reclassify_raster_by_digit_indices(
        raster: np.ndarray,
        significant_indices: list[int],
        class_replacement: dict = None
        ) -> np.ndarray:
    """
    Reclassify raster based on specific digits defined by their indices,
    with an option to replace specified classes with new ones.

    Parameters:
    - raster (np.ndarray):
        Input raster array with integer or float pixel values.
    - significant_indices (list[int]):
        List of digit indices to extract (1-based indexing).
    - class_replacement_dict (dict, optional):
        Dictionary where keys are old classes (to be replaced) and values are
        new classes.

    Returns:
    - np.ndarray: The reclassified raster array 
    """
    # Initialize a new array for reclassified value
    reclassified_raster = np.zeros(raster.shape, dtype=int)

    # Loop through each pixel
    for i in range(raster.shape[0]):
        for j in range(raster.shape[1]):
            pixel_value = raster[i, j]

            # Check if the pixel value is a valid number (not NaN)
            if np.isfinite(pixel_value):
                pixel_str = str(int(pixel_value))
                try:
                    # Select the desired digits based on indices
                    new_value = ''.join(
                    pixel_str[idx - 1] for idx in significant_indices if idx <= len(pixel_str)
                                        )
                    new_value = int(new_value) if new_value else 0
                    
                    # If class replacement is needed, apply the replacement
                    if class_replacement and new_value in class_replacement:
                        new_value = class_replacement[new_value]
                    
                    reclassified_raster[i, j] = new_value
                except IndexError:
                    # If the index is out of range, assign 0
                    reclassified_raster[i, j] = 0
            else:
                # If the value is NaN or invalid, assign 0
                reclassified_raster[i, j] = 0

    return reclassified_raster


def reclassify_and_process_lai_statistics(
    raster_with_classes: str,
    lai_folder: str,
    study_area_shapefile: str,
) -> pd.DataFrame:
    """
    Reclassifies the vegetation raster based on the second digit of class
    codes, processes the LAI data for the given study area, and extracts
    statistics by class and day. The results are saved to a CSV file containing
    average LAI values for each class.

    Parameters:
    - raster_with_classes (str):
      Path to the vegetation raster file with class codes.
    - lai_folder (str):
      Path to the folder containing the LAI raster files.
    - study_area_shapefile (str):
      Path to the shapefile representing the study area boundary.

    Returns:
    - pd.DataFrame: 
      DataFrame containing the extracted LAI statistics by class and day.
    """
    
    # Extract the year from the vegetation raster filename
    year = extract_date_from_filename_YYYY(Path(raster_with_classes))

    # Read the vegetation raster data
    vegetation_data = read_raster(raster_with_classes)

    # Reclassify the vegetation raster based on the second digit of class codes
    predict_veg_map_rec = reclassify_raster_by_digit_indices(
        raster=vegetation_data,
        significant_indices=[1, 2]
    )

    # Define the output path for the reclassified vegetation raster
    DEFAULT_REC = OUTPUT_DIR + "\\landuse_" + str(year) + "_by_2_classes.tif"

    # Save the reclassified vegetation raster for further processing
    save_data_to_raster(
        data=predict_veg_map_rec,
        reference_raster_path=raster_with_classes,
        output_path=DEFAULT_REC,
    )

    # Obtain a list of raw LAI files from the specified folder
    predict_files_raw = grab_files(
        directory=Path(lai_folder),
        extension=".tif"
    )
    
    # Define the output directory for clipped LAI rasters
    OUTPUT_DIR_PREDICT = "temp\\cutted_raster_" + str(year)

    # Ensure the output directory exists
    ensure_directory_exists(OUTPUT_DIR_PREDICT)
    
    # Clip the LAI rasters by the study area shapefile
    for raster in predict_files_raw:
        clip_raster_by_shapefile(
            file_path=raster,
            aoi_path=study_area_shapefile,
            output_folder=OUTPUT_DIR_PREDICT,
        )
        
    # Obtain a list of clipped LAI raster files
    predict_files = grab_files(
        directory=Path(OUTPUT_DIR_PREDICT),
        extension=".tif"
    )

    # Process the LAI files and extract statistics by class and day
    lai_stat_by_class_and_day = process_lai_files_and_extract_data(
        predict_files,
        DEFAULT_REC,
    )

    # Define the output CSV file name for the LAI statistics
    CSV_STAT_PREDICT = "stat_lai_" + str(year) + ".csv"

    # Save the extracted LAI statistics to a CSV file
    save_data_to_csv(
        dataframe=lai_stat_by_class_and_day,
        filename=CSV_STAT_PREDICT,
        results_folder=OUTPUT_DIR,
    )
    
    return lai_stat_by_class_and_day


def process_lai_modeling(
    vegetation_map_path: str,
    predicted_vegetation_dir: str,
    lai_daily_avg_dir: str,
    study_area_shapefile: str
) -> None:
    """
    Performs LAI modeling based on the provided parameters. This function
    processes vegetation and LAI raster data, reclassifies them, and generates
    LAI statistics for different vegetation classes. The results are saved to
    files, including reclassified rasters and CSV files with average LAI values

    Parameters:
    - vegetation_map_path (str):
    Path to the raster file with defined vegetation types.
    - predicted_vegetation_dir (str):
      Path to the directory containing predicted vegetation data.
    - lai_daily_avg_dir (str):
      Path to the directory containing daily average LAI values.
    - study_area_shapefile (str):
      Path to the shapefile representing the study area boundary.

    Returns:
    - None: The process outputs results to files.
    """
  
    # Obtain a list of raw LAI files from the specified folder
    files_in_veg_folder = grab_files(
                                    directory=Path(predicted_vegetation_dir),
                                    extension=".tif"
                                     )

    # Extract the base year from the vegetation map filename
    base_year = extract_date_from_filename_YYYY(Path(vegetation_map_path))

    # Obtain a list of raw LAI files from the specified folder
    files_in_lai_folder = grab_files(Path(lai_daily_avg_dir))

    # Ensure the directory exists
    temp_lai_folder_path = ensure_directory_exists(TEMP_LAI_DIR)

    # Convert raw LAI files from HDR to TIF format
    converted_tiff_files_paths = [
        convert_hdr_to_tif(file_lai) for file_lai in files_in_lai_folder
    ]

    # Ensure necessary directories exist
    ensure_directory_exists(TEMP_DIR)
    ensure_directory_exists(OUTPUT_DIR)

    # Clip the vegetation raster by the study area shepefile
    clipped_vegetation_ras_path = clip_raster_by_shapefile( 
            file_path=vegetation_map_path,
            aoi_path=study_area_shapefile,
            output_folder=TEMP_DIR,
        )

    # Read the clipped vegetation raster into a numpy array
    veg_map = read_raster(clipped_vegetation_ras_path)

    # Reclassify the vegetation raster based on significant indices of class
    veg_map_rec = reclassify_raster_by_digit_indices(
        raster=veg_map,
        significant_indices=[1, 2, 3],
        class_replacement_dict = CLASS_REPLACEMENT_DICT
    )
    
    # define the output path for the reclassified vegetation raster
    DEFAULT_TEMP_LANDUSE_123 = "result\\landuse_" + str(base_year) + ".tif"

    # Save the reclassified vegetation raster
    save_data_to_raster(
        data=veg_map_rec,
        reference_raster_path=vegetation_map_path,
        output_path=DEFAULT_TEMP_LANDUSE_123,
    )
        
    # Create a tamplate raster based on the reclassified vegetation raster
    temp_raster = create_template_raster(
        base_raster=Path(DEFAULT_TEMP_LANDUSE_123),
        output_folder=TEMP_DIR,
        filename=DEFAULT_TEMP_RASTER_NAME
        )

    # Standardize the LAI rasters by aligning them to the template raster size
    unified_lai_list = []
    for tiff_file in converted_tiff_files_paths:
        unified_lai_list.append(
            copy_data_to_template(
                template_raster=temp_raster,
                source_file=tiff_file,
                output_folder=DEFAULT_TEMP_LAI_DIR,
                filename=None,
                aoi_path=study_area_shapefile,
            )
        )

    # Process the LAI files and extract statistics by class and day
    lai_stat_by_class_and_day = process_lai_files_and_extract_data(
        unified_lai_list,
        DEFAULT_TEMP_LANDUSE_123,
    )

    # Save the extracted LAI statistics to a CSV file
    save_data_to_csv(
                    dataframe=lai_stat_by_class_and_day,
                    filename=DEFAULT_LAI_FILENAME,
                    results_folder=OUTPUT_DIR,
                    )
    
    # Process each predicted vegetation raster
    for predicted_vegetation_path in files_in_veg_folder:
        # Extract the year from the predicted vegetation file name
        predict_year = extract_date_from_filename_YYYY(
                                                Path(predicted_vegetation_path)
                                                       )

        # Clip the predicted vegetation raster by the study area shapefile
        clipped_vegetation_pred_path = clip_raster_by_shapefile(
                file_path=predicted_vegetation_path,
                aoi_path=study_area_shapefile,
                output_folder=TEMP_DIR,
            )
        
        # Read the clipped vegetation raster into a numpy array
        veg_map_perd = read_raster(clipped_vegetation_pred_path)

        # Reclassify the vegetation raster based on significant indices
        veg_pred_rec = reclassify_raster_by_digit_indices(
            raster=veg_map_perd,
            significant_indices=[1, 2, 3],
            class_replacement_dict = CLASS_REPLACEMENT_DICT
        )

        # Define the output path for the reclassified predicted raster
        DEFAULT_TEMP_pred_123 = "result\\landuse_" + str(predict_year) + ".tif"

        # Save the reclassified predicted vegetation raster
        save_data_to_raster(
            data=veg_pred_rec,
            reference_raster_path=vegetation_map_path,
            output_path=DEFAULT_TEMP_pred_123,
        )
    
        # Define the output folder for the generated LAI rasters
        DEFAULT_OUTPUT_LAI_DIR = "result\\generate_lai_" + str(predict_year)
        ensure_directory_exists(DEFAULT_OUTPUT_LAI_DIR)

        # Generate the LAI raster for the vegetation based on the statistics
        lai_new_stat_by_class_and_day = generate_lai_raster(
                            dataframe=lai_stat_by_class_and_day,
                            files_vegetation_base=DEFAULT_TEMP_LANDUSE_123,
                            files_vegetation_predict=DEFAULT_TEMP_pred_123,
                            lai_rasters_folder=DEFAULT_TEMP_LAI_DIR,
                            results_folder=DEFAULT_OUTPUT_LAI_DIR,
                            predict_year=predict_year,
                            base_year=base_year)


def plot_lai_by_plants(
    vegetation_predict: str,
    lai_folder_predict: str,
    vegetation_base: str,
    lai_folder_base: str,
    study_area_shapefile: str,
) -> None:
    """
    Processes vegetation and LAI (Leaf Area Index) data to generate statistical
    outputs and visualizations comparing LAI metrics for two different
    vegetation datasets (base and predicted).

    Parameters:
    - vegetation_predict (str): 
        Path to the raster file containing the predicted vegetation class data.
    - lai_folder_predict (str): 
        Path to the folder containing LAI raster files for the predicted
        vegetation.
    - vegetation_base (str): 
        Path to the raster file containing the base vegetation class data.
    - lai_folder_base (str): 
        Path to the folder containing LAI raster files for the base vegetation.
    - study_area_shapefile (str): 
        Path to the shapefile defining the boundary of the study area.

    Outputs:
    - Reclassified vegetation rasters (for both predicted and base vegetation)
      saved temporarily for LAI processing.
    - Aggregated LAI statistics for both datasets saved as CSV files in the
      output directory.
    - Visualizations comparing LAI metrics across vegetation classes saved as
      PNG files in the plot output folder.

    Returns:
    - None
    """
    
    # Ensure the output directory for results exists
    ensure_directory_exists(OUTPUT_DIR)

    # Extract the year from the vegetation predict filename
    predict_year = extract_date_from_filename_YYYY(Path(vegetation_predict))

    # Process LAI statistics for the predicted vegetation dataset
    predict_lai_stat_by_class_and_day = reclassify_and_process_lai_statistics(
        raster_with_classes=vegetation_predict,
        lai_folder=lai_folder_predict,
        study_area_shapefile=study_area_shapefile,
    )

    # Process LAI statistics for the base vegetation dataset
    base_lai_stat_by_class_and_day = reclassify_and_process_lai_statistics(
        raster_with_classes=vegetation_base,
        lai_folder=lai_folder_base,
        study_area_shapefile=study_area_shapefile,
    )

    # Ensure the output directory for plots exists
    ensure_directory_exists(DEFAULT_PLOT_OUTPUT_DIR)

    # Generate and save comparison plots of LAI distribution
    plot_comparison_of_two_lai_datasets(
        base_data_frame=base_lai_stat_by_class_and_day,
        predict_data_frame=predict_lai_stat_by_class_and_day,
        results_folder_png=DEFAULT_PLOT_OUTPUT_DIR,
        predict_year=predict_year
    )
