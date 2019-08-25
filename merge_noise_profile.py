#!/usr/bin/python3

# # Data Indexer
# This script sweeps the file index and consolidate channel and site information.
# - Read files on designated folder

# Import standard libraries
import pandas as pd

import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

def _main():

    index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.INDEX_FILENAME)
    file_index = index_store[cn.FILE_INDEX]
    index_length = len(file_index.index)-1

    # create empty dataframe to store the resulting profile
    profile_array_result = pd.DataFrame()
    number_of_traces = 0

    # Loop through files collecting the required information
    for row in range(index_length):
        # Open each file
        file_name = file_index[cn.FILENAME_ATTRIBUTE][row]

        file_object = h5py.File(file_name, 'r')
        # TODO: Include test if the file follows the standard

        # Test if there is a noise group. The noise group contains all traces and thus reference to the time and frequency scope of the file content
        if H5.NOISE_DATA_GROUP in file_object:
            # Get a handle on the noise group
            noise_group = file_object[H5.NOISE_DATA_GROUP]

            # get all sub groups group names within the noise group
            for sub_group in noise_group:

                # if sub group corresponds to level profile group. Noise group also include the level profile group
                if H5.LEVEL_PROFILE_CLASS in str(noise_group[sub_group].attrs[H5.CLASS_ATTRIBUTE][0]):

                    # recover the dataset reference handle
                    profile_dataset = noise_group[sub_group+'/'+H5.LEVEL_PROFILE_DATASET]
                    # Todo: test if level units are compatible

                    # update the counter for the number of traces on the profile
                    number_of_traces += profile_dataset.attrs[H5.NUMBER_OF_PROFILE_TRACES_ATTRIBUTE][0]

                    # Get the level profile
                    profile_array_new = pd.DataFrame(profile_dataset[:])
                    profile_array_new.columns = noise_group[sub_group+'/'+H5.FREQUENCY_DATASET][:]
                    profile_array_new.index = noise_group[sub_group+'/'+H5.LEVEL_DATASET][:]

                    # Merge the new profile into the result
                    profile_array_result = profile_array_result.add(profile_array_new, fill_value=0)

                    cl.log_message("File {} processed. Profile shape: {}".format(file_name, str(profile_array_result.shape)))

    # store the index tables created
    index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME)
    index_store[H5.NOISE_DATA_GROUP+"/"+H5.LEVEL_PROFILE_DATASET] = profile_array_result
    index_store.close()

    # output message
    cl.log_message("Finish indexing {} files".format(index_length))

if __name__ == '__main__':
    _main()
