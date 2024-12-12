from typing import List

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_DISPLAY_DATAS = ["Min", "Q1", "Median", "Q3", "Max",]


DEFAULT_COLOR_SCHEME = {
    "diagram1": {
                    "color_min_max": "black",
                    "color_q1_q3": "lightgreen",
                    "color_median": "green"
                },
    "diagram2": {
                    "color_min_max": "red",
                    "color_q1_q3": "lightblue",
                    "color_median": "blue"
                }
}



def plot_comparison_of_two_lai_datasets(
    base_data_frame: pd.DataFrame,
    predict_data_frame: pd.DataFrame,
    results_folder: str,
    predict_year=str,
    ) -> None:
    """
    Plot a comparison of two LAI (Leaf Area Index) datasets and save the 
    result as a PNG file.

    The function reads two CSV files, each containing LAI data, and then plots 
    both datasets on the same graph for comparison. It also extracts land use 
    and elevation information from the filenames of the datasets and includes 
    these in the graph's title and output filename.

    Parameters:
        data_frame_first_path (str): Path to the first CSV file containing LAI 
            data.
        data_frame_second_path (str): Path to the second CSV file containing
            LAI data.
        results_folder_png (str, optional): Directory path where the resulting 
            PNG plot will be saved. Defaults to DEFAULT_PLOT_COMPARE_OUTPUT_DIR

    Returns:
        None: This function does not return any value, but it saves a PNG file
            with the comparison plot.
    """
    landuse_list = predict_data_frame["Landuse"].unique()
    
    for landuse_class in landuse_list:

        predict_data_frame_by_landuse = (
            predict_data_frame[predict_data_frame["Landuse"] == landuse_class]
            )
        base_data_frame_by_landuse = (
            base_data_frame[base_data_frame["Landuse"] == landuse_class]
            )

        # Set up the figure size for the plot
        plt.figure(figsize=(18, 6))
        plt.suptitle(
            f"Comparison of LAI for Land Use Class {landuse_class}:\
                  2020 vs {predict_year}"
        )

        # Plot the base dataset
        plt.subplot(1,2,1)
        plot_single_lai_graph(
            base_data_frame_by_landuse,
            color_scheme=DEFAULT_COLOR_SCHEME["diagram1"],
            label_prefix=landuse_class,
        )
        plt.title("Average LAI by Day in 2020")

        num_days = len(base_data_frame_by_landuse)
        xticks = range(1, num_days+1, 30)
        plt.xticks(xticks, [str(i) for i in xticks])
        plt.xlabel("Day of Year")
        plt.ylabel("LAI Value")
        plt.ylim(0, 7)
        plt.legend()

        # Plot the predict dataset
        plt.subplot(1,2,2)
        plot_single_lai_graph(
            predict_data_frame_by_landuse,
            color_scheme=DEFAULT_COLOR_SCHEME["diagram2"],
            label_prefix=landuse_class,
        )
        plt.title(f"Forecasted Average LAI by Day in {predict_year}")

        num_days = len(predict_data_frame_by_landuse)
        xticks = range(1, num_days+1, 30)
        plt.xticks(xticks, [str(i) for i in xticks])
        plt.xlabel("Day of Year")
        plt.ylabel("LAI Value")
        plt.ylim(0, 7)
        plt.legend()

        # Define the path for saving the comparison plot
        plot_path = results_folder + f"\\lai_comparison_{landuse_class}_.png"

        # Save the plot as a PNG file
        plt.savefig(plot_path)
        plt.close()


def plot_single_lai_graph(
    group_data: pd.DataFrame,
    color_scheme: dict,
    label_prefix: str = None,
    display_datas: List[str] = DEFAULT_DISPLAY_DATAS,
    ) -> None:
    """
    Plot LAI (Leaf Area Index) data for a specific time period with various 
    statistical measures such as Q1, Q3, Min, Max, and Median.

    The function visualizes the LAI statistics for different time periods and 
    fills the area between Q1 and Q3 as a shaded region. It also plots the 
    specific statistical measures (Min, Max, and Median) over the date.

    Parameters:
        group_data (pd.DataFrame): DataFrame containing LAI statistics with 
          columns like 'Date', 'Q1', 'Q3', 'Min', 'Max', 'Median', etc.
        color_scheme (dict): A dictionary containing color specifications for 
          different plot elements like 'color_q1_q3', 'color_min_max', and 
          'color_median'.
        display_datas (List[str], optional): A list of statistical measures 
          (e.g., 'Q1', 'Q3', 'Min', 'Max', 'Median') to display on the plot. 
          Defaults to DEFAULT_DISPLAY_DATAS.

    Returns:
        None: The function generates the plot but does not return any value.
    """
    # Plot the shaded area between Q1 and Q3 if both are in display_datas
    if "Q1" in display_datas and "Q3" in display_datas:
        plt.fill_between(
            group_data["Date"], #.dt.dayofyear,
            group_data["Q1"],
            group_data["Q3"],
            color=color_scheme["color_q1_q3"],
            alpha=0.5,
            label=f"{label_prefix} Q1 - Q3",
        )

    # Iterate through each specified statistical measure in display_datas
    for display_data in display_datas:
        if display_data == "Min" or display_data == "Max":
            # Plot Min and Max with a specific color and style
            plt.plot(
                group_data["Date"], #.dt.dayofyear,
                group_data[display_data],
                color=color_scheme["color_min_max"],
                linestyle="-",
                linewidth=0.5,
                label=f"{label_prefix} {display_data}",
            )

        elif display_data == "Median":
            # Plot Median with a thicker line and different color
            plt.plot(
                group_data["Date"], #.dt.dayofyear,
                group_data[display_data],
                color=color_scheme["color_median"],
                linestyle="-",
                linewidth=2,
                label=f"{label_prefix} {display_data}",
            )

        elif display_data not in ["Q1", "Q3"]:
            # Plot other specified data measures as usual
            plt.plot(
                group_data["Date"], #.dt.dayofyear,
                group_data[display_data],
                label=f"{label_prefix} {display_data}",
            )
