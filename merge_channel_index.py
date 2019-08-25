#!/usr/bin/python3

#%% [markdown]
# # Data Indexer
# This script sweeps the file index and consolidate channel information into a channel index

# Import standard libraries
import pandas as pd

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

def _main():

    index_store = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.INDEX_FILENAME)
    file_index = index_store[cn.FILE_INDEX]
    site_index = index_store[cn.SITE_INDEX]
    channel_index = index_store[cn.CHANNEL_INDEX]

    # update the store with the sorted file_index
    index_store[cn.FILE_INDEX]=file_index

    # create new dataframe that will store the consolidated data for the detected channels
    channel_data = pd.DataFrame(columns=[cn.CHANNEL_ID,
                                         H5.CHANNEL_EDGE_INITIAL_FREQUENCY,
                                         cn.CHANNEL_INNER_EDGE_INITIAL_FREQUENCY,
                                         H5.CHANNEL_CORE_INITIAL_FREQUENCY,
                                         H5.CHANNEL_CORE_FINAL_FREQUENCY,
                                         cn.CHANNEL_INNER_EDGE_FINAL_FREQUENCY,
                                         H5.CHANNEL_EDGE_FINAL_FREQUENCY])

    # initialize the consolidated channel dataframe
    channel_row = 0
    input_file_name = channel_index.loc[channel_row, cn.FILENAME_ATTRIBUTE]
    center_frequency = round((channel_index.loc[channel_row, H5.CHANNEL_CORE_FINAL_FREQUENCY] + channel_index.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY])/2000)
    cl.log_message("Starting channel {} at {}kHz with file {}".format(channel_row, center_frequency, input_file_name))

    current_channel_id = "Channel {}".format(channel_row)
    data = [current_channel_id,
            channel_index.iloc[channel_row, 6], # edge initial frequency
            channel_index.iloc[channel_row, 7], # edge inner initial frequency
            channel_index.iloc[channel_row, 8], # core initial frequency
            channel_index.iloc[channel_row, 9], # core final frequency
            channel_index.iloc[channel_row, 10], # edge inner final frequency
            channel_index.iloc[channel_row, 11]] # edge final frequency

    channel_data.loc[channel_row] = data
    channel_index.loc[channel_row, cn.CHANNEL_ID] = current_channel_id

    # loop through all channel information from different files
    index_length = len(channel_index.index)
    for row in range(1, index_length, 1):
        # test if channel core on the consolidated list 'd' (channel_Data at channel_row) intersect the channel on the index file 'i' (channel_Index at row) or the other way around
        index_core_first = channel_index.loc[row, H5.CHANNEL_CORE_INITIAL_FREQUENCY] <= channel_data.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY]
        data_core_first = channel_data.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY] <= channel_index.loc[row, H5.CHANNEL_CORE_INITIAL_FREQUENCY]
        i_inside_d = index_core_first and (channel_data.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY] <= channel_index.loc[row, H5.CHANNEL_CORE_FINAL_FREQUENCY])
        d_inside_i = data_core_first and (channel_index.loc[row, H5.CHANNEL_CORE_INITIAL_FREQUENCY] <= channel_data.loc[channel_row, H5.CHANNEL_CORE_FINAL_FREQUENCY])

        # if they do intercept, merge the channel information
        if i_inside_d or d_inside_i:
            # link channel index with the channel data
            channel_index.loc[row, cn.CHANNEL_ID] = current_channel_id

            # update the channel data boundaries. Core is the intersection, edge is the union
            # if stored edge begin is larger than the new edge
            if channel_data.iloc[channel_row, 1] > channel_index.iloc[row, 6]:
                # update edge begin. (move edge to the left, expand)
                channel_data.iloc[channel_row, 1] = channel_index.iloc[row, 6]

            # if stored edge begin is smaller than the new edge
            if channel_data.iloc[channel_row, 2] < channel_index.iloc[row, 7]:
                # update edge begin. (moved edge to the right, contract) There is no risk of crossing of edges since the core is in between, a condition guaranteed by the detection algorithm
                channel_data.iloc[channel_row, 2] = channel_index.iloc[row, 7]

            # if stored core begin is lower than the new core
            if channel_data.iloc[channel_row, 3] < channel_index.iloc[row, 8]:
                # if new core begin still smaller than the core end. Necessary to avoid core equal or smaler than zero
                if channel_index.iloc[row, 8] < channel_data.iloc[channel_row, 4]:
                    # update core begin (move core to the right, contract)
                    channel_data.iloc[channel_row, 3] = channel_index.iloc[row, 8]

            # if stored core end is higher than the new core
            if channel_data.iloc[channel_row, 4] > channel_index.iloc[row, 9]:
                # if new core end still larger than the core begin
                if channel_index.iloc[row, 9] > channel_data.iloc[channel_row, 3]:
                    # update core end (move core to the left, contract)
                    channel_data.iloc[channel_row, 4] = channel_index.iloc[row, 9]

            # if stored edge end is larger than the new edge
            if channel_data.iloc[channel_row, 5] > channel_index.iloc[row, 10]:
                # update edge end (move edge to the left, contract)
                channel_data.iloc[channel_row, 5] = channel_index.iloc[row, 10]

            # if stored edge end is smaller than the new edge
            if channel_data.iloc[channel_row, 6] < channel_index.iloc[row, 11]:
                # update edge end (move edge to the right, expand)
                channel_data.iloc[channel_row, 6] = channel_index.iloc[row, 11]

            input_file_name = channel_index.loc[row, cn.FILENAME_ATTRIBUTE]
            center_frequency = round((channel_data.loc[channel_row, H5.CHANNEL_CORE_FINAL_FREQUENCY] + channel_data.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY])/2000)
            cl.log_message("   | Merged channel {} at {}kHz with file {}".format(row, center_frequency, input_file_name))

        # if they do not intercept
        else:
            # a new channel needs to be assigned
            channel_row += 1
            current_channel_id = "Channel {}".format(channel_row)
            data = [current_channel_id,
                    channel_index.iloc[row, 6],
                    channel_index.iloc[row, 7],
                    channel_index.iloc[row, 8],
                    channel_index.iloc[row, 9],
                    channel_index.iloc[row, 10],
                    channel_index.iloc[row, 11]]

            channel_data.loc[channel_row] = data
            channel_index.loc[row, cn.CHANNEL_ID] = current_channel_id

            input_file_name = channel_index.loc[row, cn.FILENAME_ATTRIBUTE]
            center_frequency = round((channel_data.loc[channel_row, H5.CHANNEL_CORE_FINAL_FREQUENCY] + channel_data.loc[channel_row, H5.CHANNEL_CORE_INITIAL_FREQUENCY])/2000)
            cl.log_message("Starting channel {} at {}kHz with file {}".format(channel_row, center_frequency, input_file_name))

    # loop through channel data and reasign names to the new center frequency in kHz rounded to integer
    cl.log_message("Starting channel renaming")
    
    index_length = len(channel_data.index)
    for row in range(0, index_length, 1):
        center_frequency = round((channel_data.loc[row, H5.CHANNEL_CORE_FINAL_FREQUENCY] + channel_data.loc[row, H5.CHANNEL_CORE_INITIAL_FREQUENCY])/2000)

        current_channel_id = "{:.0f}".format(center_frequency)

        channel_index.replace(to_replace=channel_data.loc[row, cn.CHANNEL_ID], value=current_channel_id, inplace=True)
        channel_data.loc[row, cn.CHANNEL_ID] = current_channel_id
        cl.log_message("Channel {} renamed at {}kHz".format(row, center_frequency))
        """
        print("{} - {}: {:.0f}, {:.0f}, {:.0f}, {:.0f}".format(row,
                                                               channel_data.loc[row, cn.CHANNEL_ID],
                                                               channel_data.loc[row, H5.CHANNEL_EDGE_INITIAL_FREQUENCY],
                                                               channel_data.loc[row, H5.CHANNEL_CORE_INITIAL_FREQUENCY],
                                                               channel_data.loc[row, H5.CHANNEL_CORE_FINAL_FREQUENCY],
                                                               channel_data.loc[row, H5.CHANNEL_EDGE_FINAL_FREQUENCY]))
        """
    #channel_data.to_csv(cn.FOLDER_TO_STORE_FILES+'/'+'channel_data.csv', index=None, header=True)

    index_store[cn.CHANNEL_DATA_TABLE] = channel_data
    index_store[cn.CHANNEL_INDEX] = channel_index

    index_store.close()

    cl.log_message("Finish data indexing")
    #print("site_index: "+str(site_index.shape))
    #print("file_index: "+str(file_index.shape))

if __name__ == '__main__':
    _main()
