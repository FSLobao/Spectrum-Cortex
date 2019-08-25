#!/usr/bin/python3

# # Compute the distance between traces for classification

# Import standard libraries
import pandas as pd
import numpy as np
from scipy import signal
from scipy.cluster.hierarchy import dendrogram, linkage

import matplotlib.pyplot as plt
import h5py

# Import specific libraries used by the cortex system
import h5_spectrum as H5
import cortex_names as cn
import cortex_lib as cl

# TODO: This could be improved by testing the similarity before merging and so allow for separation of co channel emissions

def _main():

    cl.log_message("Starting channel distance processing")

    # open file with h5Py method
    input_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
    input_file = h5py.File(input_file_name)

    input_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.CHANNEL_MEAN_LEVEL_CATALOG
    input_group = input_file[input_group_name]

    # create dictionary to store channel traces
    channel_traces = {}
    channel_frequency = {}

    # create dataframe to store chanel info
    channel_info = pd.DataFrame()

    # loop through all channels, load data into the traces dictionary and extract reference information into the channel info dataframe
    for channel_id in input_group:

        # TODO: Channels should have attributes and those should be verified to confirm the proper funcyion
        one_channel = input_group[channel_id][1]

        channel_width = len(one_channel)

        # ignore channels that are too small
        if channel_width > cn.MINIMUM_CHANNEL_WIDTH:

            # find maximum
            maximum_level = np.max(one_channel)

            # locate the index for the maximum
            index_of_maximum = np.argmax(one_channel)
            # handle multiple maximum case
            if isinstance(index_of_maximum, np.ndarray):
                index_of_maximum = np.mean(index_of_maximum)

            frequency_at_peak = input_group[channel_id][0][index_of_maximum]

            # transform level to relative a scale where the maximum equals to 1
            channel_traces[channel_id] = np.array(one_channel/maximum_level, dtype='float64')
            channel_frequency[channel_id] = (np.array(input_group[channel_id][0], dtype='float64')-frequency_at_peak)/1000

            channel_info.loc[channel_id, 'Max Index'] = index_of_maximum
            channel_info.loc[channel_id, 'Bin Width'] = channel_width
            channel_info.loc[channel_id, 'Min Value'] = np.min(channel_traces[channel_id])
            channel_info.loc[channel_id, 'Max Value'] = maximum_level
            channel_info.loc[channel_id, 'Frequency Max Value'] = frequency_at_peak
    # close file since all data has been loaded into memory
    input_file.close()

    # create a list of keys used for the channels trace designation on the corresponding dictionary
    channel_list = list(channel_traces.keys())

    # create array to store the condensed distance matrix
    number_of_channels = len(channel_list)
    condensed_distance = np.empty(int(round(((number_of_channels**2)-number_of_channels)/2, 0)))
    c_d_index = 0

    # loop though channels to compute distance between then
    for ref_channel_index in range(0, number_of_channels):

        # get key and trace from index
        ref_channel_id = channel_list[ref_channel_index]

        cl.log_message("Starting channel {}".format(ref_channel_id))

        # defines the lower limit to the reference channel level range
        min_ref_level = channel_info.loc[ref_channel_id, 'Min Value']

        #PLOT_THRESHOLD = 0.3
        #plot_this = (min_ref_level < PLOT_THRESHOLD)

        # loop through all channels and compute the distance
        for target_channel_index in range(ref_channel_index+1, number_of_channels):

            # get key and trace from index
            target_channel_id = channel_list[target_channel_index]
            target_channel_trace = channel_traces[target_channel_id]

            # defines the lower limit to the reference channel level range
            min_target_level = channel_info.loc[target_channel_id, 'Min Value']

            #plot_that = (min_target_level < PLOT_THRESHOLD)
            #plot_all = plot_this and plot_that

            #if (target_channel_id == '462574') and (ref_channel_id == '451011'):
            #    print('gotcha')

            # Cut the channels in the level axis such as that both have the same range. Equivalent to raise noise
            # If the reference channel has larger minimum reference level
            if min_ref_level > min_target_level:
                # Means that the peak value of the reference channel is lower, closer to the noise level
                # cut the target channel to the same range as the reference channel and copy the reference to the work variable
                target_channel_trace = target_channel_trace[target_channel_trace[:] >= min_ref_level]
                work_ref_channel_trace = channel_traces[ref_channel_id]

            elif min_ref_level < min_target_level:
                # else, if the reference channel has smaller minimum referecence level
                # cut the reference channel to the same range as the target channel and leave the target channel as it is
                work_ref_channel_trace = channel_traces[ref_channel_id][channel_traces[ref_channel_id][:] >= min_target_level]

            else:
                # else, both are the same, and just update the work variable reference
                work_ref_channel_trace = channel_traces[ref_channel_id]

            # After level cut, assign first trace on the correlation process to be the longest.
            # The correlation values are not affected by the order but their relative indexing to the result is.
            # For the implemented method of alignment, the first trace should be the largest
        
            """
            figure1_name = "Comparison_{}-{} ".format(ref_channel_id, target_channel_id)
            plt.figure(figure1_name)
            plt.subplot(312)
            plt.xticks([])
            plt.subplot(311)
            plt.xticks([])
            """

            if work_ref_channel_trace.size > target_channel_trace.size:
                smaller_trace = target_channel_trace.view()
                larger_trace = work_ref_channel_trace.view()

                """
                plt.title('Longer Trace [{}]'.format(ref_channel_id))
                plt.plot(channel_traces[ref_channel_id], 'r-')
                plt.subplot(312)
                plt.title('Shorter Trace [{}]'.format(target_channel_id))
                plt.plot(channel_traces[target_channel_id], 'b-')
                """

            else:
                smaller_trace = work_ref_channel_trace.view()
                larger_trace = target_channel_trace.view()

            """
                plt.title('Longer Trace [{}]'.format(target_channel_id))
                plt.plot(channel_traces[target_channel_id], 'r-')
                plt.subplot(312)
                plt.title('Shorter Trace [{}]'.format(ref_channel_id))
                plt.plot(channel_traces[ref_channel_id], 'b-')
            """

            """
            larger_trace = work_ref_channel_trace.view()
            smaller_trace = target_channel_trace.view()
            """

            # computes the cross correlation between channels
            correlation = signal.correlate(larger_trace, smaller_trace, mode='full', method='fft')
            peak_correlation_index = np.argmax(correlation)

            # compute the length of distance to be cutted out from the beginning of one of the traces such as to align it both at maximum correlation
            total_trace_shift = peak_correlation_index-(smaller_trace.size-1)
            size_difference = larger_trace.size - smaller_trace.size

            # if the total shift is negative
            if total_trace_shift < 0:
                # smaller trace needs to be moved to the left,
                # cut the begin of the smaller trace by the total shift
                smaller_trace = smaller_trace[-total_trace_shift:]
                # cut the larger trace to the same size as the second
                larger_trace = larger_trace[0:(larger_trace.size-size_difference+total_trace_shift)]
            # else, smaller trace needs to be moved to the right
            else:
                end_offset = size_difference-total_trace_shift
                # if shift is equal or smaller than the difference in size of the traces
                if end_offset >= 0:
                    # cut the begin of the larger trace by the required shift
                    # cut the end of the larger trace to match the sizes
                    larger_trace = larger_trace[total_trace_shift:larger_trace.size-end_offset]
                # else, smaller trace needs to be moved to the right but will overflow the larger trace
                else:
                    # cut the smaller trace by the difference from the shift and size difference
                    smaller_trace = smaller_trace[0:smaller_trace.size+end_offset]
                    # cut the begin of the first trace by to match the second trace
                    larger_trace = larger_trace[size_difference-end_offset:]

            # Compute the error. Uses RMSE as an normalized approximation of the euclidian distance (RSSE)
            # The use of mean is necessary due to the variable number of bins

            rms_distance = np.sqrt(np.mean((smaller_trace-larger_trace)**2))

            channel_info.loc[ref_channel_id, target_channel_id] = rms_distance

            condensed_distance[c_d_index] = rms_distance
            c_d_index += 1

            """
            plt.subplot(313)
            plt.title('Adjusted Traces')
            plt.plot(larger_trace, 'r-', smaller_trace, 'b-')
            
            figure_file_name = "./Images/"+figure1_name+".png"
            plt.savefig(figure_file_name)
            plt.close(figure1_name)
            """
            #plt.show()

            """
            if ref_channel_id == '450188': # '466862':

                half_trace_length = int(work_ref_channel_trace.size/2)
                if 2*half_trace_length < work_ref_channel_trace.size:
                    ref_index = np.arange(-half_trace_length, half_trace_length+1, 1)
                else:
                    ref_index = np.arange(-half_trace_length, half_trace_length, 1)

                half_trace_length = int(target_channel_trace.size/2)
                if 2*half_trace_length < target_channel_trace.size:
                    target_index = np.arange(-half_trace_length, half_trace_length+1, 1)
                else:
                    target_index = np.arange(-half_trace_length, half_trace_length, 1)

                half_trace_length = int(correlation.size/2)
                if 2*half_trace_length < correlation.size:
                    cor_index = np.arange(-half_trace_length, half_trace_length+1, 1)
                else:
                    cor_index = np.arange(-half_trace_length, half_trace_length, 1)

                ref_index = np.arange(0, larger_trace.size, 1)
                target_index = np.arange(0, target_channel_trace.size, 1)
                cor_index = np.arange(0, correlation.size, 1)

                plt.figure(1)
                plt.subplot(211)
                plt.plot(larger_trace, 'r-', smaller_trace, 'b-')

                plt.subplot(212)
                plt.plot(correlation, 'g-')
                plt.show()

                plt.plot(larger_trace, 'r-', smaller_trace, 'b-',correlation/np.max(correlation), 'g-')
                plt.show()

            if is_it_autocorrelation:
                autocorrelation = np.max(correlation)-np.min(correlation)
                is_it_autocorrelation = False
                channel_info.loc[ref_channel_id, target_channel_id] = 1.0
            else:
                # store the relative correlation peak as reference for the channel similarity
                channel_info.loc[ref_channel_id, target_channel_id] = (np.max(correlation)-np.min(correlation))/autocorrelation
            """

    # perform grouping by the distance and plot dendograms
    NUMBER_OF_GROUPS = 6
    figure2_name = "Dendogram cut p={}".format(NUMBER_OF_GROUPS)
    plt.figure(figure2_name, figsize=(8, 6), dpi=80, frameon=False)
    linkage_matrix = linkage(condensed_distance, method="complete", optimal_ordering=True)
    cut_dendo = dendrogram(linkage_matrix,
                           labels=channel_list,
                           truncate_mode='lastp',
                           p=NUMBER_OF_GROUPS,
                           leaf_rotation=90.,
                           leaf_font_size=9.,
                           show_contracted=True)

    figure_file_name = "./Images/"+figure2_name+".png"
    plt.savefig(figure_file_name)

    figure3_name = "Dendogram Complete"
    plt.figure(figure3_name, figsize=(8, 6), dpi=80, frameon=False)
    complete_dendo = dendrogram(linkage_matrix,
                                labels=channel_list,
                                leaf_rotation=90.,
                                leaf_font_size=8.)

    # figure_file_name = "./Images/"+figure3_name+".png"
    # plt.savefig(figure_file_name)

    # creata a description of the channels on each group that compose a specific branch
    leaves = complete_dendo['ivl']
    branch_id = 0
    branch_dict = {branch_id:[]}
    number_of_leaves_in_branche = int(cut_dendo['ivl'][branch_id][1:-1])-1
    number_of_leaves_already_considered = 0

    for leave_index, channel_id in enumerate(leaves):
        if leave_index > number_of_leaves_in_branche+number_of_leaves_already_considered:
            branch_id += 1
            number_of_leaves_in_branche = int(cut_dendo['ivl'][branch_id][1:-1])-1
            number_of_leaves_already_considered = leave_index
            branch_dict[branch_id] = []

        branch_dict[branch_id] = branch_dict[branch_id]+[channel_id]

    classified_groups = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in branch_dict.items() ]))

    cl.table_dataframe(classified_groups)

    plt.show()

    plt.close(figure2_name)
    plt.close(figure3_name)

    cl.table_dataframe(channel_info)

    channel_ref_index = 0
    group_referece = 1

    """
    # identify channel within each group that has the highest signal to noise ratio to represent the group
    for group_size_string in cut_dendo['ivl']:
        group_size = int(group_size_string[1:-1])
        channel_id = complete_dendo['ivl'][channel_ref_index]
        minimum_channel_level = channel_info.loc[channel_id, 'Min Value']
        channel_group_reference = channel_id
        for channel_index in range(1,group_size):
            channel_ref_index += 1
            channel_id = complete_dendo['ivl'][channel_ref_index]
            current_channel_level = channel_info.loc[channel_id, 'Min Value']
            if minimum_channel_level > current_channel_level:
                minimum_channel_level = current_channel_level
                channel_group_reference = channel_id
        channel_ref_index += 1

        plt.figure("Channel {}. Reference to group {}".format(channel_group_reference, group_referece))
        plt.plot(channel_frequency[channel_group_reference],
                 channel_traces[channel_group_reference]*channel_info.loc[channel_group_reference, 'Max Value'])
        plt.ylabel("Level [dB\u03BCV/m]")
        plt.xlabel("Frequency[kHz]")

        group_referece += 1

    #dendrogram(linkage_matrix, labels=channel_list, leaf_rotation=90., leaf_font_size=12.)

    
    """

    # store the dataframe with the data.
    output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
    file_data_store = pd.HDFStore(output_file_name)
    output_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.INTER_CHANNEL_DISTANCES
    file_data_store[output_group_name] = channel_info
    output_group_name = H5.CHANNEL_DATA_GROUP+"/"+cn.INTER_CHANNEL_DISTANCES_CONDENSED_MATRIX
    file_data_store[output_group_name] = pd.DataFrame(condensed_distance)
    file_data_store.close()

    cl.log_message("Finish processing")

if __name__ == '__main__':
    _main()
