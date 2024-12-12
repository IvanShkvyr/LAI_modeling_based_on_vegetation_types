from setuptools import setup, find_packages


setup(
    name='LAI_modeling_based_on_vegetation_types',
    version='0.1.0',
    packeges=find_packages(),
    install_requires=[
        'numpy==1.26.4',
        'pandas== 2.2.3',
        'rasterio==1.3.10',
        'geopandas==0.13.2',
        'matplotlib==3.9.1',
    ],
    entry_point={
        'console_scriots':[
            # TODO: Add console scripts
        ],
    },
    author='Ivan Shkvyr',
    author_email='shkvyr.i@czechglobe.cz',
    description=(
                 'This module processes raw Leaf Area Index (LAI) data for a '
                 'base period, converting it into a more accessible format. '
                 'It then generates new LAI rasters for the forecasted period '
                 'using base period vegetation data and predicted data. '
                 'The processed data is saved in tif files, and visualized in '
                 'graphs.'
                 ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/IvanShkvyr/LAI_modeling_based_on_vegetation_types',
)