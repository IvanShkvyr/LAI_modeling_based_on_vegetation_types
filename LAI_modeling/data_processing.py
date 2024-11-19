from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from file_processing import (
                             grab_files,
                             ensure_directory_exists,
                             extract_date_from_filename,
                             save_data_to_csv,
                             )
from raster_processing import (
                               clip_raster_by_shapefile,
                               create_template_raster,
                               copy_data_to_template,
                               read_raster,
                               generate_lai_raster,
                              )

TEMP_DIR = "Temp"
OUTPUT_DIR = "Result"
DEFAULT_TEMP_RASTER_NAME = "template_raster.tif"
DEFAULT_TEMP_LAI_DIR ="temp\\temp_lai_unifited"
DEFAULT_LAI_FILENAME = "stat_lai.csv"
DEFAULT_OUTPUT_LAI_DIR ="result\\generate_lai"



def calculate_lai_statistic(
        lai_data ,
        landuse ,
        landuse_class: int
        ) -> dict:
    """
    TODO
    """
    mask = (landuse == landuse_class)
    if np.any(mask):
        filtered_lai_data = lai_data[mask]
        mean_lai = np.mean(filtered_lai_data)
        Q1 = np.percentile(filtered_lai_data, 25)
        Q2 = np.percentile(filtered_lai_data, 50)
        Q3 = np.percentile(filtered_lai_data, 75)
        min_val = np.min(filtered_lai_data)
        max_val = np.max(filtered_lai_data)

        return {"Mean": mean_lai, 
                "Min": min_val,
                "Q1": Q1,
                "Median": Q2,
                "Q3": Q3,
                "Max": max_val,
            }


def process_lai_files_and_extract_data(
    unified_lai_list: List[Path],
    land_use_file_path: str,
):# -> List[LAIRecord]:
    """
    TODO
    """
    # Read the land use data from the specified raster file
    landuse = read_raster(Path(land_use_file_path))
    # Get unique land use classes present in the raster
    unique_landuse_classes = np.unique(landuse)

    data = []
    for lai_file in unified_lai_list:
        # Extract date information from the LAI file name

        date = extract_date_from_filename(lai_file)

        # Read LAI data from the current file
        lai_data = read_raster(lai_file)

        # Loop through each unique land use class
        for landuse_class in unique_landuse_classes:

            # Calculate mean LAI and boxplot statistics for the current
            # land use and elevation class
            stats = calculate_lai_statistic(
                lai_data, landuse, landuse_class
            )

            if stats is not None:
                data.append(
                    [
                        date,
                        landuse_class,
                        stats["Mean"],
                        stats["Min"],
                        stats["Q1"],
                        stats["Median"],
                        stats["Q3"],
                        stats["Max"],
                    ]
                )

    # Create a DataFrame from the provided data with specified columns
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
        ],
    )



    return data_frame


def process_lai_modeling(
    vegetation_map_path: str,
    predicted_vegetation_path: str,
    lai_daily_avg_dir: str,
    study_area_shapefile: str
) -> None:
    """
    Performs LAI modeling based on the provided parameters.

    Parameters:
    - vegetation_map_path (str): Path to the raster file with defined vegetation types.
    - predicted_vegetation_dir (str): Path to the directory containing predicted vegetation data.
    - lai_daily_avg_dir (str): Path to the directory containing daily average LAI values.
    - study_area_shapefile (str): Path to the shapefile representing the study area boundary.

    Returns:
    - None: The process outputs results to files.
    """

    # Obtain a list of LAI files from the specified folder
    files_in_lai_dir = grab_files(Path(lai_daily_avg_dir), ".tif")

    ensure_directory_exists(TEMP_DIR)

    clipped_vegetation_ras_path = clip_raster_by_shapefile(
            file_path=vegetation_map_path,
            aoi_path=study_area_shapefile,
            output_folder=TEMP_DIR,
        )
    
    clipped_vegetation_pred_path = clip_raster_by_shapefile(
            file_path=predicted_vegetation_path,
            aoi_path=study_area_shapefile,
            output_folder=TEMP_DIR,
        )
    
    temp_raster = create_template_raster(
        base_raster=Path(clipped_vegetation_ras_path),
        output_folder=TEMP_DIR,
        filename=DEFAULT_TEMP_RASTER_NAME
        )

    # Resample the LAI rasters to match the template raster   
    unified_lai_list = []
    for tiff_file in files_in_lai_dir:
        unified_lai_list.append(
            copy_data_to_template(
                template_raster=temp_raster,
                source_file=tiff_file,
                output_folder=DEFAULT_TEMP_LAI_DIR,
                filename=None,
            )
        )

    lai_stat_by_class_and_day = process_lai_files_and_extract_data(
        unified_lai_list,
        clipped_vegetation_ras_path,
    )

    save_data_to_csv(
                    dataframe=lai_stat_by_class_and_day,
                    filename=DEFAULT_LAI_FILENAME,
                    results_folder=TEMP_DIR,
                    )
    

    ensure_directory_exists(DEFAULT_OUTPUT_LAI_DIR)

    generate_lai_raster(
                        dataframe=lai_stat_by_class_and_day,
                        files_vegetation=clipped_vegetation_pred_path,
                        results_folder=DEFAULT_OUTPUT_LAI_DIR,
                        )
    



    # return lai_stat_by_class_and_day


    
