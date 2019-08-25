#!/usr/bin/python3

#%% [markdown]
# # Data Indexer
# This script sweeps the file index and consolidate site information into data tables

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

    # TODO: Improve to handle multiple sites
    # merge site information into a single site
    index_length = len(site_index.index)-1
    for row in range(index_length, 0, -1):
        # TODO: Test if distance between average of the two sets are within the variance before adding. If not, more sites should be created
        # TODO: Test if the equipment ID matches and consolidate information only for the same equipment or better, process equipment information separatly
        site_index.loc[row-1, H5.LATITUDE_MEMBER].add_set(site_index.loc[row, H5.LATITUDE_MEMBER])
        site_index.loc[row-1, H5.LONGITUDE_MEMBER].add_set(site_index.loc[row, H5.LONGITUDE_MEMBER])
        # site_index.loc[row-1, H5.LATITUDE_MEMBER].print("site row {}: ".format(row-1))
        # site_index.loc[row-1, H5.LONGITUDE_MEMBER].print("site row {}: ".format(row-1))
        site_index.drop(row, inplace=True)

    # create a data table that will be used for plotting
    site_data = pd.DataFrame(columns=[H5.CRFS_HOSTNAME,
                                      H5.LATITUDE_MEMBER,
                                      H5.LONGITUDE_MEMBER,
                                      H5.START_TIME_COARSE_ATTRIBUTE,
                                      H5.STOP_TIME_COARSE_ATTRIBUTE])

    # store the site data on the table
    # TODO: Add variance to allow ellipse plotting of the site
    site_data.loc[0, H5.CRFS_HOSTNAME] = site_index.loc[0, H5.CRFS_HOSTNAME]
    site_data.loc[0, H5.LATITUDE_MEMBER] = site_index.loc[0, H5.LATITUDE_MEMBER].mean_value
    site_data.loc[0, H5.LONGITUDE_MEMBER] = site_index.loc[0, H5.LONGITUDE_MEMBER].mean_value
    site_data.loc[0, H5.START_TIME_COARSE_ATTRIBUTE] = file_index.loc[0, H5.START_TIME_COARSE_ATTRIBUTE]
    site_data.loc[0, H5.STOP_TIME_COARSE_ATTRIBUTE] = file_index.loc[len(file_index.index)-1, H5.START_TIME_COARSE_ATTRIBUTE]

    # store the table on the index file
    index_store[cn.SITE_DATA_TABLE] = site_data

    output_file_name = cn.FOLDER_TO_STORE_FILES+'/'+cn.DATA_FILENAME
    file_data_store = pd.HDFStore(output_file_name)
    file_data_store[cn.SITE_DATA_TABLE] = site_data
    file_data_store.close()
    
    index_store.close()

    cl.log_message("Finish site data processing")
    #print("site_index: "+str(site_index.shape))

if __name__ == '__main__':
    _main()
