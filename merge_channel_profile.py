#!/usr/bin/python3

# # Channel profile merger
# This script sweeps the detected channels and merge the level profile.

# Import standard libraries
import pandas as pd
import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

def _main():

    index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.INDEX_FILENAME)

    channel_data = index_store[cn.CHANNEL_DATA_TABLE]
    index_length = len(channel_data.index)-1

    channel_index = index_store[cn.CHANNEL_INDEX]
    channel_index.set_index(cn.CHANNEL_ID, inplace=True)

    # Loop through channels grouped collecting the required information
    for row in range(index_length):

        # create empty dataframe to store the resulting profile
        profile_array_result = pd.DataFrame()
        number_of_traces = 0

        # Get the channel ID
        channel_id = channel_data.loc[row, cn.CHANNEL_ID]

        # Select files that contain the designated channel
        files_with_channel = channel_index[channel_index.index == channel_id]

        # Get the number of files to be processed
        channel_index_length = len(files_with_channel.index)

        # initialize bolean variable responsible to signaling the existance of at least one profile
        shall_remove_channel_reference = True

        # initialize variable to store the total number of profiles and avoid scope limitations due to conditional initialization
        number_of_traces_sum = 0

        # loop through files that are marked with the indicated channel
        for channel_row in range(channel_index_length):

            # get the file and group for the channel data
            input_file_name = files_with_channel.iloc[channel_row, 0]

            input_group_name = files_with_channel.iloc[channel_row, 1]
            input_group_name = input_group_name.replace(H5.ACTIVITY_PROFILE_DATA_GROUP, H5.LEVEL_PROFILE_DATA_GROUP)

            # open the file
            input_file_object = h5py.File(input_file_name, 'r')
            # TODO: Include test if the file follows the standard

            # Get a handle on the group
            input_profile_group = input_file_object[H5.CHANNEL_DATA_GROUP+"/"+input_group_name]

            # recover the dataset reference handle
            profile_dataset = input_profile_group[H5.LEVEL_PROFILE_DATASET]
            # Todo: test if level units are compatible

            # update the counter for the number of traces on the profile
            number_of_traces = profile_dataset.attrs[H5.NUMBER_OF_PROFILE_TRACES_ATTRIBUTE][0]
            if number_of_traces > 0:
                number_of_traces_sum += number_of_traces

                # Get the level profile
                profile_array_new = pd.DataFrame(profile_dataset[:])
                profile_array_new.columns = input_profile_group[H5.FREQUENCY_DATASET][:]
                profile_array_new.index = input_profile_group[H5.LEVEL_DATASET][:]

                # Merge the new profile into the result
                profile_array_result = profile_array_result.add(profile_array_new, fill_value=0.0)

                profile_array_result.fillna(0, inplace=True)

                shall_remove_channel_reference = False
            else:
                cl.log_message("File {} has no profile data".format(input_file_name))
                #TODO: Delete from index

            cl.log_message("Processed {}/{}. Profile shape: {}".format(input_file_name, input_group_name, str(profile_array_result.shape)))

        # If no profile is really stored for the channel. May happen if channel was created due to database reference
        if shall_remove_channel_reference:
            cl.log_message("No profile for channel {}/{}".format(input_file_name, input_group_name))
        
        else:
            # store the dataframe with the merged level profile
            output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
            index_store = pd.HDFStore(output_file_name)
            output_group_name = H5.CHANNEL_DATA_GROUP+"/"+H5.LEVEL_PROFILE_DATA_GROUP+channel_id 
            index_store[output_group_name] = profile_array_result
            index_store.close()
            
            # store the attributes to the group where the dataframe is stored
            output_file_object = h5py.File(output_file_name)
            output_file_object[output_group_name].attrs[H5.NUMBER_OF_PROFILE_TRACES_ATTRIBUTE] = number_of_traces_sum
            output_file_object.close()

    # output message
    cl.log_message("Finish indexing {} files".format(index_length))

if __name__ == '__main__':
    _main()
