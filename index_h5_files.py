#!/usr/bin/python3

# # File Indexer
# This script perform the following tasks
# - Read files on designated folder and create an index with its main characteristics, to be used for later data processing

# Import standard libraries
import glob
import pandas as pd
import numpy as np

import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

def _main():

    # List files on folder
    files = [f for f in glob.glob(cn.FOLDER_TO_GET_FILES + cn.FILE_TYPE, recursive=False)]
    index_length = files.__len__()

    file_index = pd.DataFrame(columns=[cn.FILENAME_ATTRIBUTE,
                                       H5.INITIAL_FREQUENCY_ATTRIBUTE,
                                       H5.FINAL_FREQUENCY_ATTRIBUTE,
                                       H5.START_TIME_COARSE_ATTRIBUTE,
                                       H5.STOP_TIME_COARSE_ATTRIBUTE])

    # Create a dataframe with file names and reference information
    file_index[cn.FILENAME_ATTRIBUTE] = files
    file_index[H5.INITIAL_FREQUENCY_ATTRIBUTE] = [0.0]*index_length
    file_index[H5.FINAL_FREQUENCY_ATTRIBUTE] = [0.0]*index_length
    file_index[H5.START_TIME_COARSE_ATTRIBUTE] = [0.0]*index_length
    file_index[H5.STOP_TIME_COARSE_ATTRIBUTE] = [0.0]*index_length

    site_index = pd.DataFrame(columns=[H5.LATITUDE_MEMBER,
                                       H5.LONGITUDE_MEMBER,
                                       H5.CRFS_HOSTNAME])

    channel_index = pd.DataFrame(columns=[cn.CHANNEL_ID,
                                          cn.FILENAME_ATTRIBUTE,
                                          cn.GROUPNAME_ATTRIBUTE,
                                          H5.START_TIME_COARSE_ATTRIBUTE,
                                          H5.STOP_TIME_COARSE_ATTRIBUTE,
                                          H5.AVERAGE_CHANNEL_SAMPLE_RATE,
                                          H5.CHANNEL_EDGE_INITIAL_FREQUENCY,
                                          cn.CHANNEL_INNER_EDGE_INITIAL_FREQUENCY,
                                          H5.CHANNEL_CORE_INITIAL_FREQUENCY,
                                          H5.CHANNEL_CORE_FINAL_FREQUENCY,
                                          cn.CHANNEL_INNER_EDGE_FINAL_FREQUENCY,
                                          H5.CHANNEL_EDGE_FINAL_FREQUENCY])

    channel_row = 0

    # Loop through files collecting the required information
    for row in range(index_length):
        # Open each file
        file_name = file_index[cn.FILENAME_ATTRIBUTE][row]
        cl.log_message("Processing file {}".format(file_name))

        file_object = h5py.File(file_name, 'r')
        # TODO: Include test if the file follows the standard

        # Get the site coordinates. Work only for single site set of files.
        if H5.SITE_GEOLOCATION_DATASET in file_object:
            site_dataset = file_object[H5.SITE_GEOLOCATION_DATASET]
            site_index.loc[row] = [cl.Normal(), cl.Normal(), "unknown"]
            site_index.loc[row, H5.LATITUDE_MEMBER].np_set(site_dataset.attrs[H5.LATITUDE_STATISTICS_ATTRIBUTE][0])
            site_index.loc[row, H5.LONGITUDE_MEMBER].np_set(site_dataset.attrs[H5.LONGITUDE_STATISTICS_ATTRIBUTE][0])

        # Get the unit information from the logbook. Only the first equipment ID is retrived
        if H5.LOGBOOK_DATASET in file_object:
            logbook_dataset = file_object[H5.LOGBOOK_DATASET]
            for log_entry in logbook_dataset:
                if log_entry[H5.ENTRY_TYPE_MEMBER].decode("ascii") == H5.CRFS_HOSTNAME:
                    site_index.loc[row, H5.CRFS_HOSTNAME] = log_entry[H5.ENTRY_VALUE_MEMBER].decode("ascii")
                    break

        # Test if there is a noise group. The noise group contains all traces and thus reference to the time and frequency scope of the file content
        if H5.NOISE_DATA_GROUP in file_object:
            # Get a handle on the noise group
            noise_group = file_object[H5.NOISE_DATA_GROUP]

            # get all sub groups group names within the noise group
            for sub_group in noise_group:

                # if sub group corresponds to em spectrum group. Noise group also include the level profile group
                if H5.SPECTROGRAM_CLASS in str(noise_group[sub_group].attrs[H5.CLASS_ATTRIBUTE][0]):

                    # Get the frequency reference data from the frequency axis dataset
                    frequency_dataset = noise_group[sub_group+'/'+H5.FREQUENCY_DATASET]
                    file_index.loc[row, H5.INITIAL_FREQUENCY_ATTRIBUTE] = frequency_dataset.attrs[H5.INITIAL_FREQUENCY_ATTRIBUTE][0]
                    file_index.loc[row, H5.FINAL_FREQUENCY_ATTRIBUTE] = frequency_dataset.attrs[H5.FINAL_FREQUENCY_ATTRIBUTE][0]

                    # Get the time reference data from the timestamp coarse dataset
                    timestamp_coarse_dataset = noise_group[sub_group+'/'+H5.TIMESTAMP_COARSE_DATASET]
                    file_index.loc[row, H5.START_TIME_COARSE_ATTRIBUTE] = timestamp_coarse_dataset.attrs[H5.START_TIME_COARSE_ATTRIBUTE][0]
                    file_index.loc[row, H5.STOP_TIME_COARSE_ATTRIBUTE] = timestamp_coarse_dataset.attrs[H5.STOP_TIME_COARSE_ATTRIBUTE][0]

        if H5.CHANNEL_DATA_GROUP in file_object:
            # Get a handle on the activity profile group
            channel_group = file_object[H5.CHANNEL_DATA_GROUP]

            # get all sub groups group names within the noise group
            for sub_group in channel_group:

                # if sub group corresponds to activity profile group.
                if H5.ACTIVITY_PROFILE_CLASS in str(channel_group[sub_group].attrs[H5.CLASS_ATTRIBUTE][0]):

                    data = ["",
                            file_index.loc[row, cn.FILENAME_ATTRIBUTE],
                            sub_group,
                            file_index.loc[row, H5.START_TIME_COARSE_ATTRIBUTE],
                            file_index.loc[row, H5.STOP_TIME_COARSE_ATTRIBUTE],
                            channel_group[sub_group].attrs[H5.AVERAGE_CHANNEL_SAMPLE_RATE][0],
                            channel_group[sub_group].attrs[H5.CHANNEL_EDGE_INITIAL_FREQUENCY][0],
                            channel_group[sub_group].attrs[H5.CHANNEL_EDGE_INITIAL_FREQUENCY][0], # channel edge inner frequency is equal to edge frequency for a single file
                            channel_group[sub_group].attrs[H5.CHANNEL_CORE_INITIAL_FREQUENCY][0],
                            channel_group[sub_group].attrs[H5.CHANNEL_CORE_FINAL_FREQUENCY][0],
                            channel_group[sub_group].attrs[H5.CHANNEL_EDGE_FINAL_FREQUENCY][0], # channel edge inner frequency is equal to edge frequency for a single file
                            channel_group[sub_group].attrs[H5.CHANNEL_EDGE_FINAL_FREQUENCY][0]]

                    channel_index.loc[channel_row] = data
                    channel_row += 1

        # If there is no noise group
        else:
            # Issue error message and proceed to next file
            cl.log_message("File {} does not include reference noise data and will be ignored".format(file_name))

    # sort files by timestamp
    file_index.sort_values(by=[H5.START_TIME_COARSE_ATTRIBUTE], ascending=[True], inplace=True)
    file_index.reset_index(inplace=True, drop = True)
    #file_index.to_csv(cn.FOLDER_TO_STORE_FILES+'/'+'file_index_after.csv', index=None, header=True)

    # sort channels by core initial frequency and timestamp
    channel_index.sort_values(by=[H5.CHANNEL_CORE_INITIAL_FREQUENCY, H5.START_TIME_COARSE_ATTRIBUTE], ascending=[True, True], inplace=True)
    channel_index.reset_index(inplace=True, drop = True)
    #channel_index.to_csv(cn.FOLDER_TO_STORE_FILES+'/'+'channel_index_after.csv', index=None, header=True)

    # store the index tables created
    index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.INDEX_FILENAME)
    index_store[cn.FILE_INDEX] = file_index
    index_store[cn.SITE_INDEX] = site_index
    index_store[cn.CHANNEL_INDEX] = channel_index
    index_store.close()
    
    # output message
    cl.log_message("Finish indexing {} files".format(index_length))

if __name__ == '__main__':
    _main()
