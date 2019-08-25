#!/usr/bin/python3

# # Compute the distance between traces of capturered on the same channel. Large difference signs probable changes on the channel usage, e.g channel sharing by different emitters

# Import standard libraries
import pandas as pd
import numpy as np
import math
import h5py

from matrixprofile import *
from matrixprofile.discords import discords

import matplotlib.pyplot as plt

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

# TODO: This could be improved by testing the similarity before merging and so allow for separation of co channel emissions

def _main():

    # open file and get a list of the channel spectrogram groups. Uses H5py for better efficiency
    data_store_file = h5py.File(cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME)
    channel_spectrogram_list = list(data_store_file[H5.CHANNEL_DATA_GROUP].keys())
    data_store_file.close()

    # create array with bin edges to be used on the histogram
    profile_histogram_bins = np.arange(1, 8, 0.05)
    numpy_histogram_bins = np.r_[-np.inf, profile_histogram_bins, np.inf]

    # create empty dataframe to store results
    channel_distances = pd.DataFrame()

    for spectrogram_group_name in channel_spectrogram_list:

        # reopen the file with pandas HDF
        data_store_file = pd.HDFStore(cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME)

        # Test if dataset is of the spectrogram type
        if H5.EM_SPECTRUM_DATA_GROUP in spectrogram_group_name:
        
            # get the channel ID
            channel_id = spectrogram_group_name.split(H5.EM_SPECTRUM_DATA_GROUP)[1]

            # get the dataframe
            channel_traces = data_store_file[H5.CHANNEL_DATA_GROUP+'/'+spectrogram_group_name]
            frequency_at_peak = channel_traces.idxmax(axis=1).mean()

            number_of_time_samples = channel_traces.shape[0]

            if number_of_time_samples > cn.MINIMUM_NUMBER_SAMPLES_FOR_INNER_ANALYSIS:

                # reduce the number of traces to make computation viable
                if number_of_time_samples*channel_traces.shape[1] > cn.MAXIMUM_NUMBER_DATAPOINTS_FOR_INNER_ANALYSIS:
                    number_of_time_samples = int(round(cn.MAXIMUM_NUMBER_DATAPOINTS_FOR_INNER_ANALYSIS/channel_traces.shape[1],0))
                    channel_traces = channel_traces.iloc[0:number_of_time_samples, :]

                figure_name = "Spectrogram channel {}".format(channel_id)
                plt.figure(figure_name)
                plt.subplot(121)
                plt.title("Spectrogram for channel {}".format(channel_id))
                xy_array = channel_traces.to_numpy(dtype='float32')
                frequency_axis = channel_traces.columns.to_numpy(dtype='float64')
                x_axis = (frequency_axis-frequency_at_peak)/1000.0
                y_axis = channel_traces.index.to_numpy(dtype='float64')
                y_axis = y_axis-y_axis.min()

                plt.pcolormesh(x_axis, np.arange(0, xy_array.shape[0]), xy_array, cmap='CMRmap_r')
                plt.xlabel("Frequency[kHz]")
                plt.ylabel("Index")

                # flatten the dataframe to a series
                flatten_trace = channel_traces.to_numpy(dtype='float32').flatten()
                trace_bin_width = channel_traces.shape[1]

                profile, profile_index = matrixProfile.stomp(flatten_trace, trace_bin_width)

                plt.subplot(122)
                plt.title("Matrix Profile".format(channel_id))
                plt.ylim((0, profile.size))
                plt.yticks(ticks=np.arange(0, profile.size, profile.size/number_of_time_samples), labels='')
                plt.grid(which='major', axis='y')
                plt.plot(profile, np.arange(0, profile.size))

                combined_dataframe = pd.Series(flatten_trace).to_frame()
                combined_dataframe['profile'] = np.append(profile, np.zeros(trace_bin_width-1)+np.nan)

                # no exclusion zone
                ex_zone = trace_bin_width

                # TODO: instead of using fixed number, should use a measure above noise
                number_of_modes = math.ceil(number_of_time_samples*cn.PEAK_SAMPLE_RATIO)

                # get a maximum of one anomaly for each trace
                profile_peak = discords(combined_dataframe['profile'], ex_zone, k=number_of_modes+1)

                # get the peaks into a dataframe with corresponding matrix profile values
                profile_peak_df = combined_dataframe.loc[profile_peak, 'profile']

                # select peaks that have large profile values considering defined thershold
                # profile_peak_df=profile_peak_df[profile_peak_df.loc[:]>cn.MPROFILE_NOISE_THRESHOLD]

                profile_peak_df = profile_peak_df.reset_index()

                # compute the corresponding trace index based on the flatten index
                profile_peak_df['trace_index'] = round(profile_peak_df['index']/trace_bin_width, 0)
                order = 1

                for one_peak_index in profile_peak_df['trace_index']:
                    plt.subplot(121)
                    plot_name = "{}".format(order)
                    x_pos = x_axis.max()
                    y_pos = int(one_peak_index)
                    arrow_end_pos = x_pos+((x_pos-x_axis.min())/25)
                    plt.annotate(plot_name,
                                 xy=(x_pos, y_pos), xycoords="data",
                                 xytext=(arrow_end_pos, y_pos), textcoords='data',
                                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
                    order += 1

                figure_file_name = "./Images/"+figure_name+".png"
                plt.savefig(figure_file_name)
                plt.close(figure_name)

                # TODO: Use profile_peak_df to split spectrogram into two subchannels. Compute new Profile Density

                # store the distance information as reference to the channel
                channel_distance_descriptor = pd.DataFrame()
                channel_distance_descriptor.loc[channel_id, cn.INNER_DISTANCE_MAX] = profile_peak_df.loc[0, 'profile']
                channel_distance_descriptor.loc[channel_id, cn.INNER_DISTANCE_MEAN] = profile_peak_df.mean(axis='rows')['profile']

                # compute histogram
                profile_histogram, discarted_bins = np.histogram(profile, bins=numpy_histogram_bins, density=False)

                # add overflow to last bin 
                profile_histogram[-2] += profile_histogram[-1]
                profile_histogram = profile_histogram[0:-1]

                # plot histogram
                histogram_maximum = profile_histogram.max()
                figure_name = "Matrix Profile histogram for channel {}".format(channel_id)
                plt.figure(figure_name)
                plt.ylim(0,histogram_maximum*1.05)
                plt.bar(profile_histogram_bins, height=profile_histogram, width=1)
                plt.plot(profile_histogram_bins, profile_histogram)
                figure_file_name = "./Images/"+figure_name+".png"
                plt.savefig(figure_file_name)
                plt.close(figure_name)

                # convert np array with the histogram to a dataframe, using the bin values as column names
                profile_histogram_df = pd.DataFrame([profile_histogram], index=[channel_id], columns=profile_histogram_bins)

                # merge dataframes to get the complete channel inner distance profile information into the same row
                channel_distance_descriptor = channel_distance_descriptor.join(profile_histogram_df)

                channel_distances = channel_distances.append(channel_distance_descriptor)

                #close file used to read the data
                data_store_file.close()

                # store the dataframe with the data. Since this is a slow process, it is stored each update for safe interruption
                output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
                file_data_store = pd.HDFStore(output_file_name)
                output_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.CHANNEL_DISTANCES_DATA_GROUP
                file_data_store[output_group_name] = channel_distances
                file_data_store.close()

                cl.log_message("Processed channel {}. Inner distance of {}".format(channel_id, channel_distances.loc[channel_id, cn.INNER_DISTANCE_MAX]))

                #plt.show()

            else:

                #close file used to read the data
                data_store_file.close()

                channel_distances.loc[channel_id,:] = np.NaN

                output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
                file_data_store = pd.HDFStore(output_file_name)
                output_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.CHANNEL_DISTANCES_DATA_GROUP
                file_data_store[output_group_name] = channel_distances
                file_data_store.close()

                cl.log_message("Processed channel {}. Too few traces to evaluate inner distance. # traces: ".format(channel_id, number_of_time_samples))

if __name__ == '__main__':
    _main()
