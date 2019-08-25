#include <stdint.h>
#include <string>
#include <H5Cpp.h>

using namespace std;

// Constants to be used for the creation of the HDF5 file
    const int	 RANK_2D = 2;
    const int	 RANK_1D = 1;
    const hsize_t chunk_dims_2D[RANK_2D] = { 1024, 633 };	// chunk dimensions using golden ratio for fun
    const hsize_t chunk_dims_1D[RANK_2D] = { 1657 };	

    const hsize_t maxdims_2D[2] = {H5S_UNLIMITED, H5S_UNLIMITED};
    const hsize_t maxdims_1D[1] = {H5S_UNLIMITED};

    const int HDF5_COMPRESSION_LEVEL = 6;
    
// Constants that define labels on the HDF5 format

// Groups for different levels of analysis stored on the HDF5 file
    const H5std_string	FREQUENCY_SWEEP_DATA_GROUP("Frequency Sweep");
    const H5std_string	EM_SPECTRUM_DATA_GROUP("EM Spectrum.");

    const H5std_string	NOISE_DATA_GROUP("Noise");
    const H5std_string	LEVEL_PROFILE_DATA_GROUP("Level Profile.");

    const H5std_string	CHANNEL_DATA_GROUP("Channel");
    const H5std_string	ACTIVITY_PROFILE_DATA_GROUP("Activity Profile.");

// Common group attributes
    const H5std_string	STANDARD_ATTRIBUTE("Standard");
    const H5std_string	CLASS_ATTRIBUTE("Class");
    const H5std_string	RESPONSIBLE_ATTRIBUTE("Responsible");
    const H5std_string	CREATION_TIMESTAMP_ATTRIBUTE("Creation Timestamp");
    const H5std_string	TAG_ATTRIBUTE("Tag");

// Spectrogram dataset and associated attributes
    const H5std_string	SPECTROGRAM_DATASET("Spectrogram");
    const H5std_string	MEASUREMENT_UNIT_ATTRIBUTE("Measurement unit");
    const H5std_string	MAXIMUM_DETECTED_LEVEL_ATTRIBUTE("Maximum observed level");
    const H5std_string	MINIMUM_DETECTED_LEVEL_ATTRIBUTE("Minimum observed level");

// Frequency axis dataset and associated attributes
    const H5std_string	FREQUENCY_DATASET("Frequency");
    const H5std_string	FILTER_BANDWIDTH_ATTRIBUTE("Filter bandwidth");
    const H5std_string	INITIAL_FREQUENCY_ATTRIBUTE("Initial frequency");
    const H5std_string	FINAL_FREQUENCY_ATTRIBUTE("Final frequency");

// Coarse timestamp axis dataset and associated attributes
    const H5std_string	TIMESTAMP_COARSE_DATASET("Timestamp coarse");
    const H5std_string	START_TIME_COARSE_ATTRIBUTE("Start time coarse");
    const H5std_string	STOP_TIME_COARSE_ATTRIBUTE("Stop time coarse");

// Fine timestamp axis dataset and associated attributes
    const H5std_string	TIMESTAMP_FINE_DATASET("Timestamp fine");
    const H5std_string	START_TIME_FINE_ATTRIBUTE("Start time fine");
    const H5std_string	STOP_TIME_FINE_ATTRIBUTE("Stop time fine");

// Level Profile dataset and associated attributes
    const H5std_string	LEVEL_PROFILE_DATASET("Level profile");
    const H5std_string	NUMBER_OF_PROFILE_TRACES_ATTRIBUTE("Number of profile traces");

// Level axis dataset and associated attributes
    const H5std_string	LEVEL_DATASET("Level");
    const H5std_string	LEVEL_STEP_ATTRIBUTE("Level step");

// Level statistics dataset and associated attributes
    const H5std_string	LEVEL_STATISTICS_DATASET("Level statistics");

// Level density time series dataset and associated attributes
    const H5std_string	LEVEL_DENSITY_DATASET("Level density");

// Activation and deactivation datasets
    const H5std_string	ACTIVATION_EVENT_COARSE_TIMESTAMP_DATASET("Activation event coarse timestamp");
    const H5std_string	ACTIVATION_EVENT_FINE_TIMESTAMP_DATASET("Activation event fine timestamp");
    const H5std_string	ACTIVATED_STATE_DURATION_DATASET("Activated state duration");
    const H5std_string	DEACTIVATION_EVENT_COARSE_TIMESTAMP_DATASET("Deactivation event coarse timestamp");
    const H5std_string	DEACTIVATION_EVENT_FINE_TIMESTAMP_DATASET("Deactivation event fine timestamp");
    const H5std_string	DEACTIVATED_STATE_DURATION_DATASET("Deactivated state duration");

    const H5std_string	FIRST_TIMESTAMP_COARSE("First timestamp coarse");
    const H5std_string	FIRST_TIMESTAMP_FINE("First timestamp fine");
    const H5std_string	DURATION_UNTIL_FIRST("Duration until first");
    const H5std_string	CHANNEL_ACTIVE_AT_START_ATTRIBUTE("Is channel active at start?");

    const H5std_string	LAST_TIMESTAMP_COARSE("Last timestamp coarse");
    const H5std_string	LAST_TIMESTAMP_FINE("Last timestamp fine");
    const H5std_string	DURATION_UNTIL_END("Duration until end");
    const H5std_string	CHANNEL_ACTIVE_AT_STOP_ATTRIBUTE("Is channel active at stop?");
    const H5std_string	CHANNEL_SAMPLE_RATE_STATISTICS("Channel sample rate statistics");

    const H5std_string  CHANNEL_EDGE_INITIAL_FREQUENCY("Channel edge initial frequency");
    const H5std_string  CHANNEL_CORE_INITIAL_FREQUENCY("Channel core initial frequency");
    const H5std_string  CHANNEL_CORE_FINAL_FREQUENCY("Channel core final frequency");
    const H5std_string  CHANNEL_EDGE_FINAL_FREQUENCY("Channel edge final frequency");

    const H5std_string	NOISE_REFERENCE_STATISTICS("Noise reference statistics");
    const H5std_string	DETECTION_THRESHOLD("Detection Threshold");
    const H5std_string	AVERAGE_CHANNEL_SAMPLE_RATE("Average Channel sample rate");

// Raw measurement data attributes 
    const H5std_string	NUMBER_OF_LOOPS_ATTRIBUTE("Number of measurement samples");
    const H5std_string	SAMPLE_DURATION_ATTRIBUTE("Measurement sample duration");

// Members to compound type for statistical information associated with data that presents values distributed with a normal PDF
    const H5std_string  MEAN_MEMBER("Mean");
    const H5std_string  STANDARD_DEVIATION_MEMBER("Standard deviation");
    const H5std_string  NUMBER_OF_SAMPLES_MEMBER("Number of samples");    
    const H5std_string  SUM_MEMBER("Sum");
    const H5std_string  SUM_OF_SQUARES_MEMBER("Sum of squares");

// Members to compound type for geolocation information    
    const H5std_string	LATITUDE_MEMBER("Latitude");
    const H5std_string	LONGITUDE_MEMBER("Longitude");
    const H5std_string	ALTITUDE_MEMBER("Altitude");
    const H5std_string	TIMESTAMP_COARSE_MEMBER("Timestamp coarse");
    const H5std_string	TIMESTAMP_FINE_MEMBER("Timestamp fine");

// Site location dataset an attributes
    const H5std_string	SITE_GEOLOCATION_DATASET("Site Geolocation");
    const H5std_string	GEODETIC_DATUM_ATTRIBUTE("Geodetic Datum");
    const H5std_string	LATITUDE_STATISTICS_ATTRIBUTE("Latitude statistics");
    const H5std_string	LONGITUDE_STATISTICS_ATTRIBUTE("Longitude statistics");
    const H5std_string	ALTITUDE_STATISTICS_ATTRIBUTE("Altitude statistics");

// Members to compound type for measurement log data
    const H5std_string	ENTRY_TYPE_MEMBER("Entry type");
    const H5std_string	ENTRY_VALUE_MEMBER("Entry value");
    
    const H5std_string	LOGBOOK_DATASET("logbook");

// Reference to the present standard
    const H5std_string	STANDARD("Draft:fslobao.github.io");
    const H5std_string	FILETYPE_CLASS("Spectrum monitoring digital exchange format");
    const H5std_string	GEOLOCATION_CLASS("Location");
    const H5std_string	TIME_CAPTURE_CLASS("I/Q");
    const H5std_string	SPECTROGRAM_CLASS("Spectrogram");
    const H5std_string	LEVEL_PROFILE_CLASS("Level profile");
    const H5std_string	ACTIVITY_PROFILE_CLASS("Activity profile");

// Reference to logbook entries
    const H5std_string	CRFS_HOSTNAME("Equipment ID");
    const H5std_string	CRFS_UNIT_INFO("Measurement Script");
    const H5std_string	METHOD("Measurement Method");