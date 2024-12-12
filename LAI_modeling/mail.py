from data_processing import process_lai_modeling, plot_lai_by_plants


"""
Data for the function process_lai_modeling
"""
# Path to the file containing raw vegetation data for the year 2020
vegetation_file_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\img_veg_types\\Zelivka_S1_2020.tif"
#
predicted_vegetation = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\img_veg_types"
#
lai_avg_dir = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\LAI_mean_DOY"

# Path to shapefile containing the boundary of the study area
shapefile_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\shp\\povodi_Zelivky_32633.shp"


"""
Data for the function plot_lai_by_plants
"""
# Path to the file containing vegetation data for the forecast year
vegetation_predict_path = "\\\\hydrospace.local.czechglobe.cz\\hydro\\99_PersonalFolders\\06_IvanS\Result_simulated_LAI_image_by_year_without_gaps_(S1, S2, S3)\\Result_S3\\landuse_2060.tif"
# vegetation_predict_path="D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data_for_plots\\landuse_2040.tif"

# Path to the folder with forecasted LAI data for the projected period
lai_folder_predict_path = "\\\\hydrospace.local.czechglobe.cz\\hydro\\99_PersonalFolders\\06_IvanS\\Result_simulated_LAI_image_by_year_without_gaps_(S1, S2, S3)\\Result_S3\\generate_lai2060"
# lai_folder_predict_path="D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data_for_plots\\predict_LAI"

# Path to the file containing vegetation data for the year 2020
# File after normalization (contains data following the execution of the first function)
# for example: landuse_2020.tif

vegetation_base_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\landuse_2020.tif"
# vegetation_base_path="D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data_for_plots\\landuse_2020.tif"

# Path to the folder with normalized LAI data for the year 2020
lai_folder_base_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\temp_lai_unifited_2020"
# lai_folder_base_path ="D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data_for_plots\\base_LAI"

# Path to shapefile containing the boundary of the study area
shapefile_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\shp\\povodi_Zelivky_32633.shp"


if "__main__" == __name__:
    
    process_lai_modeling(
        vegetation_map_path=vegetation_file_path,
        predicted_vegetation_dir=predicted_vegetation,
        lai_daily_avg_dir=lai_avg_dir,
        study_area_shapefile=shapefile_path
    )


    # plot_lai_by_plants(
    #                 vegetation_predict=vegetation_predict_path,
    #                 lai_folder_predict=lai_folder_predict_path,
    #                 vegetation_base=vegetation_base_path,
    #                 lai_folder_base=lai_folder_base_path,
    #                 study_area_shapefile=shapefile_path
    #                 )
