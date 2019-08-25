#!/usr/bin/python3

# # Merge spectrograms for each trace and compute the mean value for each spectrogram

# Import standard libraries
import pandas as pd
import numpy as np
import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

# TODO: This could be improved by testing the similarity before merging and so allow for separation of co channel emissions

def _main():

    file_index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.INDEX_FILENAME)

    channel_data = file_index_store[cn.CHANNEL_DATA_TABLE]
    index_length = len(channel_data.index)-1

    channel_index = file_index_store[cn.CHANNEL_INDEX]
    channel_index.set_index(cn.CHANNEL_ID, inplace=True)

    #channel_data_mean_level = pd.DataFrame()
    #channel_data_frequency = pd.DataFrame()

    # Loop through channels grouped collecting the required information
    for row in range(index_length):

        # create empty dataframe to store the resulting profile
        spectrogram_result = pd.DataFrame()

        # Get the channel ID
        channel_id = channel_data.loc[row, cn.CHANNEL_ID]

        # get the cut frequency as the inner edge, to enable to cut all traces to the same size as the minimum.
        initial_cut_frequency = channel_data.loc[row, cn.CHANNEL_INNER_EDGE_INITIAL_FREQUENCY]
        final_cut_frequency = channel_data.loc[row, cn.CHANNEL_INNER_EDGE_FINAL_FREQUENCY]

        # Select files that contain the designated channel
        files_with_channel = channel_index[channel_index.index == channel_id]

        # Get the number of files to be processed
        channel_index_length = len(files_with_channel.index)

        # loop through files that are marked with the indicated channel
        for channel_row in range(channel_index_length):

            # get the file and group for the channel data
            input_file_name = files_with_channel.iloc[channel_row, 0]

            input_group_name = files_with_channel.iloc[channel_row, 1]
            input_group_name = input_group_name.replace(H5.ACTIVITY_PROFILE_DATA_GROUP, H5.EM_SPECTRUM_DATA_GROUP)

            # open the file
            input_file_object = h5py.File(input_file_name, 'r')
            # TODO: Include test if the file follows the standard

            # Get a handle on the group
            input_group = input_file_object[H5.CHANNEL_DATA_GROUP+"/"+input_group_name]

            # recover the dataset reference handle
            spectrogram_dataset = input_group[H5.SPECTROGRAM_DATASET]

            # Get the spectrogram into a new dataset
            spectrogram_new = pd.DataFrame(spectrogram_dataset[:])

            # set the dataset columns as frequency 
            frequency_axis = np.array(input_group[H5.FREQUENCY_DATASET][:]/cn.FREQUENCY_RESOLUTION)
            frequency_axis = cn.FREQUENCY_RESOLUTION*frequency_axis.round(0)
            spectrogram_new.columns = frequency_axis

            # set the dataset index as timestamp
            timestamp_coarse = input_group[H5.TIMESTAMP_COARSE_DATASET][:]
            timestamp_fine = input_group[H5.TIMESTAMP_FINE_DATASET][:] / cn.NANOSECONDS_IN_SECOND
            spectrogram_new.index = timestamp_coarse + timestamp_fine

            # build a reduced frequency axis containing only the needed frequencies
            axis_has_been_cut = False
            if frequency_axis[0] < initial_cut_frequency:
                frequency_axis = frequency_axis[frequency_axis > initial_cut_frequency]
                axis_has_been_cut = True
            if frequency_axis[-1] > final_cut_frequency:
                frequency_axis = frequency_axis[frequency_axis < final_cut_frequency]
                axis_has_been_cut = True

            # if the frequency axis has been reduced
            if axis_has_been_cut:
                # cut the spectrogram dataset using the reduced frequency axis
                spectrogram_new = spectrogram_new.filter(items=frequency_axis)

            # Merge the new profile into the result
            # Missing frequency bins are left as np.NaN
            spectrogram_result = spectrogram_result.append(spectrogram_new)

            cl.log_message("Processed {}/{}. Spectrogram shape: {}".format(channel_row+1, channel_index_length, str(spectrogram_result.shape)))

        # Compute the mean level for all traces on the channel, for each frequency bin
        bin_mean_level = spectrogram_result.mean(axis='rows')
        mean_level_data = bin_mean_level.index.to_numpy(dtype='float64')
        mean_level_data = np.append([mean_level_data], [bin_mean_level.to_numpy(dtype='float64')], axis=0)

        # fill NaN values resulting from incorrect channel splicing with the average channel level over each bin
        spectrogram_result.fillna(value=bin_mean_level, inplace=True)

        #bin_mean_level = pd.DataFrame(bin_mean_level, columns=[channel_id])
        #bin_frequency = pd.DataFrame(bin_mean_level.index, columns=[channel_id])
        #bin_mean_level.reset_index(inplace=True, drop=True)

        # Store mean level on a channel catalog dataframe using the channel ID as index
        #channel_data_mean_level = channel_data_mean_level.join(bin_mean_level, how='outer')
        #channel_data_frequency = channel_data_frequency.join(bin_frequency, how='outer')

        cl.log_message("PROCESSED CHANNEL: {}".format(channel_id))

        # store the dataframe with the merged spectrogram
        output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
        file_data_store = pd.HDFStore(output_file_name)
        output_group_name = H5.CHANNEL_DATA_GROUP+"/"+H5.EM_SPECTRUM_DATA_GROUP+channel_id
        file_data_store[output_group_name] = spectrogram_result
        file_data_store.close()

        # reopen file with h5Py method
        file_data_store = h5py.File(output_file_name)

        # Test if the datagroup exist and create it if not
        output_group_store = file_data_store[H5.CHANNEL_DATA_GROUP]
        if cn.CHANNEL_MEAN_LEVEL_CATALOG in output_group_store:
            output_group_store = output_group_store[cn.CHANNEL_MEAN_LEVEL_CATALOG]
            
            # test if channel_id already exist and delete it in so. 
            if channel_id in output_group_store:
                del output_group_store[channel_id]
            
            # store the channel data
            output_group_store.create_dataset(channel_id, data=mean_level_data)
        else:
            output_group_store.create_group(cn.CHANNEL_MEAN_LEVEL_CATALOG)
            output_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.CHANNEL_MEAN_LEVEL_CATALOG
            file_data_store[output_group_name].create_dataset(channel_id, data=mean_level_data)

        file_data_store.close()

        #cl.table_dataframe(spectrogram_result)

    #cl.table_dataframe(channel_data_mean_level)
    #cl.plot_dataframe(channel_data_mean_level.reset_index())

    # output message
    cl.log_message("Finish indexing {} channels".format(index_length))

if __name__ == '__main__':
    _main()
