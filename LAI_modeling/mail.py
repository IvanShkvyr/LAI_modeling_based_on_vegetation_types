from data_processing import process_lai_modeling

vegetation_file = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\img_veg_types\\Zelivka_S1_2020.tif"
predicted_vegetation = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\img_veg_types\\Zelivka_S1_2030.tif"
lai_avg_dir = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\LAI_mean_DOY"
shapefile_path = "D:\\CzechGlobe\\Task\\task_9_20241114_(LAI_Modeling_based_on_Vegetation_Types)\\data\\shp\\povodi_Zelivky_32633.shp"


if "__main__" == __name__:
    process_lai_modeling(
            vegetation_map_path=vegetation_file,
            predicted_vegetation_path=predicted_vegetation,
            lai_daily_avg_dir=lai_avg_dir,
            study_area_shapefile=shapefile_path
    ) 