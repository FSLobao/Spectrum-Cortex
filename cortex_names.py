#!/usr/bin/python3

# # constants that control the script

FOLDER_TO_GET_FILES = "/home/lobao/TFM_Code/OutBox/"
FILE_TYPE = "*.h5"
FOLDER_TO_STORE_FILES = "/home/lobao/TFM_Code/Repository"

# constants used as label for harmonization with the HDF5 ontology used
FILENAME_ATTRIBUTE = "File Name"
GROUPNAME_ATTRIBUTE = "Group Name"
CHANNEL_ID = "Channel ID"

INDEX_FILENAME = "index.h5"
DATA_FILENAME = "data.h5"

FILE_INDEX = "File_Index"
CHANNEL_INDEX = "Channel_Index"
SITE_INDEX = "Site_Index"

CHANNEL_DATA_TABLE = "Channel_Data"
SITE_DATA_TABLE = "Site_Data"
NOISE_PROFILE = "Noise_Profile"
CHANNEL_MEAN_LEVEL_CATALOG = "Channel_Mean_Level_Catalog"
CHANNEL_FREQUENCY_CATALOG = "Channel_Frequency_Catalog"

CHANNEL_INNER_EDGE_INITIAL_FREQUENCY = "Channel inner edge initial frequency"
CHANNEL_INNER_EDGE_FINAL_FREQUENCY = "Channel inner edge final frequency"

NANOSECONDS_IN_SECOND = 1000000000.0

# Contants used on 
FREQUENCY_RESOLUTION = 25 # in Hz


# Constants used for inner distance analysis
CHANNEL_DISTANCES_DATA_GROUP = 'Channel_Distances'
MPROFILE_NOISE_THRESHOLD = 3.1 # sensitivity adjust
INNER_DISTANCE_MAX = 'Inner_Distance_Maximum'
INNER_DISTANCE_MEAN = 'Inner_Distance_Mean'
PEAK_SAMPLE_RATIO = 0.05
MINIMUM_NUMBER_SAMPLES_FOR_INNER_ANALYSIS = 10
MAXIMUM_NUMBER_DATAPOINTS_FOR_INNER_ANALYSIS = 500*50 # 500 traces with length of 50 points each.

# Constants used for outer distance processing
MINIMUM_CHANNEL_WIDTH = 10
INTER_CHANNEL_DISTANCES = 'Inter Channel Distances'
INTER_CHANNEL_DISTANCES_CONDENSED_MATRIX = "Inter Channel Distances Condensed"
