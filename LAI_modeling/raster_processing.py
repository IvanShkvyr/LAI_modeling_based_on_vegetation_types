import geopandas as gpd
import numpy as np
import os
import pandas as pd
from pathlib import Path
import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling

from file_processing import ensure_directory_exists


GREEN = "\u001b[32m"
CYAN = "\u001b[36m"
RESET = "\033[0m"


def clip_raster_by_shapefile(
    file_path: str,
    aoi_path: str,
    output_folder: str,
) -> str:
    """
    Crops a raster file to the boundaries defined by an area of
    interest (AOI) shapefile.

    This function reads the AOI shapefile to obtain the boundaries, then uses
    these boundaries to crop the provided land use raster file. The cropped
    raster is saved to the specified output folder, and the path to the newly
    created raster file is returned.

    Parameters:
       file_path (str): The path to the land use raster file that needs
        to be cropped.
       aoi_path (str): The path to the shapefile defining the area of
       interest (AOI) used for cropping.
       output_folder (str): The folder where the cropped raster file
        will be saved.

    Returns:
        str: The path to the cropped raster file.

    Notes:
        - The output raster file will be saved in GeoTIFF format.
    """
    # Loading the area of interest boundaries
    aoi_file = gpd.read_file(aoi_path)

    with rasterio.open(file_path) as src:
        raster_crs = src.crs

        # Reproject AOI if necessary
        if aoi_file.crs != raster_crs:
            aoi_file = aoi_file.to_crs(raster_crs)

        geoms = aoi_file.geometry.values
        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

    # Get the file name without the extension
    name_file = Path(file_path).name
    out_raster = f"{output_folder}/{name_file}"

    # Write the cropped image
    with rasterio.open(out_raster, "w", **out_meta) as dest:
        dest.write(out_image)

    return out_raster


def create_template_raster(
    base_raster: Path,
    output_folder: str,
    filename: str,
) -> Path:
    """
    Create a template raster file based on another raster, filled with zeros.

    Parameters:
        base_raster (Path): Path to the base raster file from which metadata
          will be read.
        output_folder (str): Path to the output folder where the template
          raster file will be created.
        filename (str): Name of the output template raster file to be created.

    Returns:
        Path: Path to the created template raster file.

    Notes:
        - This function reads the metadata (profile) from the base raster,
          removes unnecessary parameters, updates the profile for saving in
          GTiff format, and creates a new raster file filled with zeros.
        - The output raster file will have the same dimensions and coordinate
          system as the base raster, but all pixel values will be set to 0.
    """
    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Formulate the path to the output file
    template_raster_path = os.path.join(output_folder_path, filename)

    try:
        # Open the base raster and read its profile
        with rasterio.open(base_raster, "r") as src:
            profile = src.profile

            # Remove nodata parameter if it exists
            profile.pop("nodata", None)

            # Update profile for saving in GTiff format
            profile.update(
                        driver="GTiff",
                        dtype=rasterio.float32,
                        count=1,
                        compress="lzw"
                        )

            # Create a new TIFF file with all pixels set to 0
            with rasterio.open(template_raster_path, "w", **profile) as dst:
                # Create an array filled with zeros
                zeros_arr = np.zeros((src.height, src.width), dtype=np.float32)

                # Write the zeros array to the output file
                dst.write(zeros_arr, 1)
    except Exception as err:
        raise RuntimeError(f"An error occurred while creating the template\
                             raster: {err}")
    return template_raster_path


def copy_data_to_template( ## CNFHF AEYRWSZ
    template_raster: Path,
    source_file: Path,
    output_folder: str,
    filename: str | None = None,
) -> Path:
    """
    Resamples data from source_file to match the extent and resolution of
    template_raster, and copies non-zero values to output_file.

    Parameters:
        template_raster (Path): Path to the template raster file used for the
          extent and resolution.
        source_file (Path): Path to the input raster file containing data to be
          resampled.
        output_folder (str): Path to the folder where the output file will
          be saved.
        filename (str, optional): Name of the output file. If not provided,
          '_unifited' will be appended to the template file's name.

    Returns:
         Path: Path to the output raster file.
    """
    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Determine the output filename
    if filename is None:
        # Extract the base name without extension and add the suffix
        base_name = Path(source_file).stem
        filename = f"{base_name}.tif"
    else:
        # Ensure the filename has a .tif extension
        filename = f"{filename}.tif"

    # Define the full path to the output file
    unifited_file = output_folder_path / filename

    with rasterio.open(template_raster) as dst_zeros:
        # Open the raster with zero values (dst_zeros)
        dst_crs = dst_zeros.crs
        dst_transform = dst_zeros.transform
        dst_shape = dst_zeros.shape

        # Open the raster with data (source_file)
        with rasterio.open(source_file) as src:
            src_crs = src.crs
            src_transform = src.transform

            # Create a new raster ('unifited_file') matching the template
            #  raster ('dst_zeros')
            with rasterio.open(
                unifited_file,
                "w",
                driver="GTiff",
                height=dst_shape[0],
                width=dst_shape[1],
                count=src.count,
                dtype=src.dtypes[0],
                crs=dst_crs,
                transform=dst_transform,
            ) as data_resampled:

                # Resample data using nearest neighbor interpolation
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(data_resampled, i),
                        src_transform=src_transform,
                        src_crs=src_crs,
                        dst_transform=dst_transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest,
                    )

        # Copy resampled data to the output raster
        with rasterio.open(unifited_file, "r+") as dst_out:
            with rasterio.open(unifited_file) as data_resampled:
                for i in range(1, data_resampled.count + 1):
                    band_data = data_resampled.read(i)
                    dst_band_data = dst_zeros.read(i)

                    # Copy non-zero values from resampled raster
                    # to output raster
                    dst_band_data[band_data != 0] = band_data[band_data != 0]
                    dst_out.write(dst_band_data, i)

    return unifited_file


def read_raster(raster_path: Path) -> np.ndarray:
    """
    Reads the first band of a raster file and returns it as a numpy array.
    If the raster contain a NODATA value, it will be replaced with NaN

    Parameters:
        raster_path (Path): The path to the raster file to be read.

    Returns:
        numpy.ndarray: The first band of the raster file as a 2D array.
    """
    with rasterio.open(raster_path) as src:
        # Read the first band
        data = src.read(1)

        # Retrieve the NODATA value from the raster metadata
        nodata_value = src.nodata

        if nodata_value is not None:
            # Replace NODATA values with NaN
            data = np.where(data == nodata_value, np.nan, data)

        return data


def save_data_to_raster(
    data: np.ndarray,
    reference_raster_path: str,
    output_path: str,
) -> None:
    """
    Saves the adjusted LAI data to a new raster file using the metadata from
    a reference raster.

    Parameters:
        data (numpy.ndarray): Data to be saved.
        reference_raster_path (str): Path to the reference raster file, used to
          extract metadata. 
        output_path (str): Path where the new raster file will be saved.

    Raises:
        ValueError: If the dimensions of lai_adjusted do not match the
        reference raster.

    Returns:
        None: The function saves the LAI data as a new raster file.
    """
    # Open the reference raster to retrieve metadata
    with rasterio.open(reference_raster_path) as ref_raster:
        # Copy metadata from the reference raster
        meta = ref_raster.meta.copy()

        # Update metadata for single-band and float32 output
        meta.update(dtype="float32", count=1)
        
        # Ensure the data dimensions match the reference raster's dimensions
        if data.shape != (meta['height'], meta['width']):
            raise ValueError("The dimensions of lai_adjusted do not match the \
reference raster dimensions.")
        
        # Write the adjusted LAI data to the new raster file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data.astype("float32"), 1)


def generate_lai_raster(
                        dataframe: pd.DataFrame,
                        files_vegetation_base: str,
                        files_vegetation_predict: str,
                        lai_rasters_folder: str,
                        results_folder: str,
                        predict_year: str,
                        base_year : str,
                        ) -> pd.DataFrame:
    """
    Generates a LAI raster for each day of the year based on the given
    DataFrame and vegetation raster image.

    Parameters:
    - dataframe (pd.DataFrame): A DataFrame containing columns 'Date',
      'Landuse', and 'Mean_LAI'.
    - files_vegetation_base (str): Path to the base vegetation raster used to
      create the 2020 raster image.
    - files_vegetation_predict (str): Path to the predicted vegetation type
      raster.
    - lai_rasters_folder (str): Folder containing the LAI rasters.
    - results_folder (str): Path to the folder where the resulting rasters will
      be saved.
    - predict_year (str): The year of the predicted vegetation raster.
    - base_year (str): The base year for which the original vegetation raster
      was created.

    Returns:
    - pd.DataFrame: A DataFrame containing the statistics of the new rasters
      created.
    """
    data = []

    from data_processing import calculate_lai_statistic

    # Open the base vegetation raster
    with rasterio.open(files_vegetation_base) as base_src:
        base_data = base_src.read(1)

    # Create a mask based on the base vegetation raster (non-zero values)
    mask = (base_data != 0)

    # Open the predicted vegetation raster
    with rasterio.open(files_vegetation_predict) as predict_src:
        predict_data = predict_src.read(1)
        meta = predict_src.meta.copy()

        # Iterate through each unique day in the DataFrame
        for day in dataframe["Date"].unique():
            # Filter the DataFrame for the current day
            day_data = dataframe[dataframe["Date"] == day]

            # Convert day to the day of the year
            day_of_year = pd.Timestamp(day).dayofyear


            # Load the LAI raster for the specific day
            lai_raster_path = (
            Path(lai_rasters_folder) / f"lai_{base_year}{day_of_year:03d}.tif"
                )

            with rasterio.open(lai_raster_path) as lai_src:
                lai_data = lai_src.read(1)

            # Create a mapping of land use classes to the mean LAI value
            class_lai_mean = dict(zip(day_data["Landuse"], day_data["Mean"]))

            # Generate a new LAI raster
            new_lai_data = base_data.copy()
            for i in range(base_data.shape[0]):
                for j in range(base_data.shape[1]):
                    base_class = base_data[i, j]
                    predict_class = predict_data[i, j]
                    if base_class == predict_class:
                        new_lai_data[i, j] = lai_data[i, j]
                    else:
                        lai_value = lai_data[i, j]
                        mean_base_class = class_lai_mean.get(base_class, 1)
                        mean_predict_class = (
                            class_lai_mean.get(predict_class, 1)
                            )
                        new_lai_data[i, j] = (
                            lai_value * (mean_predict_class / mean_base_class)
                            )

            # Update the metadata for the resulting raster
            meta.update(dtype=rasterio.float32)

            # Define the path for the resulting file
            output_filename = (
            Path(results_folder) / f"LAI_{predict_year}{day_of_year:03d}.tif"
            )

            # Write the new LAI raster
            with rasterio.open(output_filename, "w", **meta) as dst:
                dst.write(new_lai_data.astype(rasterio.float32), 1)
   
    print(f"Растри LAI збережено в: {results_folder}")
