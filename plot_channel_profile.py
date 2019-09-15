#!/usr/bin/python3

# # Plot the channel level profile from all channels  

# Import standard libraries
import pandas as pd
import numpy as np
from scipy import signal
from scipy.cluster.hierarchy import dendrogram, linkage

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

# TODO: This could be improved by testing the similarity before merging and so allow for separation of co channel emissions

def _main():

    cl.log_message("Starting plotting level profile with average trace for all channels")

    # open file with h5Py method
    input_file_name = cn.FOLDER_TO_STORE_FILES+'/'+'data (cópia).h5' #cn.DATA_FILENAME
    input_file = h5py.File(input_file_name)

    input_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.CHANNEL_MEAN_LEVEL_CATALOG
    input_group = input_file[input_group_name]

    # create dictionary to store channel traces
    channel_traces = {}
    channel_frequency = {}
    frequency_at_peak = {}
    standard_axis = [-20, 20, 5, 45] # [xmin, xmax, ymin, ymax]

    # loop through all channels, load data into the traces dictionary and extract reference information into the channel info dataframe
    for channel_id in input_group:

        # TODO: Channels should have attributes and those should be verified to confirm the proper funcyion
        one_channel = input_group[channel_id][1]

        channel_width = len(one_channel)

        # ignore channels that are too small
        if channel_width > cn.MINIMUM_CHANNEL_WIDTH:

            # find level range
            maximum_level = np.max(one_channel)
            minimum_level = np.min(one_channel)

            # locate the index for the maximum
            index_of_maximum = np.argmax(one_channel)
            # handle multiple maximum case
            if isinstance(index_of_maximum, np.ndarray):
                index_of_maximum = np.mean(index_of_maximum)

            # store the frequency value for the maximum
            frequency_at_peak[channel_id] = input_group[channel_id][0][index_of_maximum]

            # transform level to relative a scale where the maximum equals to 1
            channel_traces[channel_id] = np.array(one_channel, dtype='float64')
            channel_frequency[channel_id] = (np.array(input_group[channel_id][0], dtype='float64')-frequency_at_peak[channel_id])/1000

            """
            # find frequency range
            maximum_freq = np.max(channel_frequency[channel_id])
            minimum_freq = np.min(channel_frequency[channel_id])

            # set the global limiting axis
            if standard_axis[0] > minimum_freq:
                standard_axis[0] = minimum_freq
            if standard_axis[1] < maximum_freq:
                standard_axis[1] = maximum_freq
            if standard_axis[2] > minimum_level:
                standard_axis[2] = minimum_level
            if standard_axis[3] < maximum_level:
                standard_axis[3] = maximum_level
            """

    # close file since all data has been loaded into memory
    input_file.close()

    # create a list of keys used for the channels trace designation on the corresponding dictionary
    channel_list = list(channel_traces.keys())

    # create array to store the condensed distance matrix
    number_of_channels = len(channel_list)

    # open data file to retrieve channel profile
    profile_file_name = cn.FOLDER_TO_STORE_FILES+'/'+'data (cópia).h5'
    profile_store = pd.HDFStore(profile_file_name)

    # loop though channels to compute distance between then
    for ref_channel_index in range(0, number_of_channels):

        # get key and trace from index
        channel_id = channel_list[ref_channel_index]

        cl.log_message("Starting channel {}".format(channel_id))

        # retrieve level profile for the channel 
        profile_group_name = H5.CHANNEL_DATA_GROUP+"/"+H5.LEVEL_PROFILE_DATA_GROUP+channel_id 
        channel_profile = profile_store[profile_group_name]

        figure_name = "Level profile channel {}".format(channel_id)
        plt.figure(figure_name)
        xy_array = channel_profile.to_numpy(dtype='float32')
        frequency_axis = channel_profile.columns.to_numpy(dtype='float64')
        x_axis = (frequency_axis-frequency_at_peak[channel_id])/1000
        y_axis = channel_profile.index.to_numpy(dtype='float64')

        plt.pcolormesh(x_axis, y_axis, xy_array, cmap='CMRmap_r')
        plt.xlabel("Frequency[kHz]")
        plt.ylabel("Level [dB\u03BCV/m]")
        plt.axis(standard_axis)

        plt.plot(channel_frequency[channel_id], channel_traces[channel_id], color='y', lw=2, path_effects=[pe.Stroke(linewidth=4, foreground='w'), pe.Normal()]) #, scaley=y_axis, 

        # plt.show()

        figure_file_name = "./Images/"+figure_name+".png"
        plt.savefig(figure_file_name)
        plt.close(figure_name)

    profile_store.close()

    cl.log_message("Finish processing")

if __name__ == '__main__':
    _main()
