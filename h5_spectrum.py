# Constants to be used for the creation of the HDF5 file
RANK_2D = 2
RANK_1D = 1

HDF5_COMPRESSION_LEVEL = 6

# Constants that define labels on the HDF5 format

# Groups for different levels of analysis stored on the HDF5 file
FREQUENCY_SWEEP_DATA_GROUP = "Frequency Sweep"
EM_SPECTRUM_DATA_GROUP = "EM Spectrum."

NOISE_DATA_GROUP = "Noise"
LEVEL_PROFILE_DATA_GROUP = "Level Profile."

CHANNEL_DATA_GROUP = "Channel"
ACTIVITY_PROFILE_DATA_GROUP = "Activity Profile."

# Common group attributes
STANDARD_ATTRIBUTE = "Standard"
CLASS_ATTRIBUTE = "Class"
RESPONSIBLE_ATTRIBUTE = "Responsible"
CREATION_TIMESTAMP_ATTRIBUTE = "Creation Timestamp"

# Spectrogram dataset and associated attributes
SPECTROGRAM_DATASET = "Spectrogram"
MEASUREMENT_UNIT_ATTRIBUTE = "Measurement unit"
MAXIMUM_DETECTED_LEVEL_ATTRIBUTE = "Maximum observed level"
MINIMUM_DETECTED_LEVEL_ATTRIBUTE = "Minimum observed level"

# Frequency axis dataset and associated attributes
FREQUENCY_DATASET = "Frequency"
FILTER_BANDWIDTH_ATTRIBUTE = "Filter bandwidth"
INITIAL_FREQUENCY_ATTRIBUTE = "Initial frequency"
FINAL_FREQUENCY_ATTRIBUTE = "Final frequency"

# Coarse timestamp axis dataset and associated attributes
TIMESTAMP_COARSE_DATASET = "Timestamp coarse"
START_TIME_COARSE_ATTRIBUTE = "Start time coarse"
STOP_TIME_COARSE_ATTRIBUTE = "Stop time coarse"

# Fine timestamp axis dataset and associated attributes
TIMESTAMP_FINE_DATASET = "Timestamp fine"
START_TIME_FINE_ATTRIBUTE = "Start time fine"
STOP_TIME_FINE_ATTRIBUTE = "Stop time fine"

# Level Profile dataset and associated attributes
LEVEL_PROFILE_DATASET = "Level profile"
NUMBER_OF_PROFILE_TRACES_ATTRIBUTE = "Number of profile traces"

# Level axis dataset and associated attributes
LEVEL_DATASET = "Level"
LEVEL_STEP_ATTRIBUTE = "Level step"

# Level statistics dataset and associated attributes
LEVEL_STATISTICS_DATASET = "Level statistics"

# Level density time series dataset and associated attributes
LEVEL_DENSITY_DATASET = "Level density"

# Activation and deactivation datasets
ACTIVATION_EVENT_COARSE_TIMESTAMP_DATASET = "Activation event coarse timestamp"
ACTIVATION_EVENT_FINE_TIMESTAMP_DATASET = "Activation event fine timestamp"
ACTIVATED_STATE_DURATION_DATASET = "Activated state duration"
DEACTIVATION_EVENT_COARSE_TIMESTAMP_DATASET = "Deactivation event coarse timestamp"
DEACTIVATION_EVENT_FINE_TIMESTAMP_DATASET = "Deactivation event fine timestamp"
DEACTIVATED_STATE_DURATION_DATASET = "Deactivated state duration"

FIRST_TIMESTAMP_COARSE = "First timestamp coarse"
FIRST_TIMESTAMP_FINE = "First timestamp fine"
DURATION_UNTIL_FIRST = "Duration until first"
CHANNEL_ACTIVE_AT_START_ATTRIBUTE = "Is channel active at start?"

LAST_TIMESTAMP_COARSE = "Last timestamp coarse"
LAST_TIMESTAMP_FINE = "Last timestamp fine"
DURATION_UNTIL_END = "Duration until end"
CHANNEL_ACTIVE_AT_STOP_ATTRIBUTE = "Is channel active at stop?"
CHANNEL_SAMPLE_RATE_STATISTICS = "Channel sample rate statistics"

CHANNEL_EDGE_INITIAL_FREQUENCY = "Channel edge initial frequency"
CHANNEL_CORE_INITIAL_FREQUENCY = "Channel core initial frequency"
CHANNEL_CORE_FINAL_FREQUENCY = "Channel core final frequency"
CHANNEL_EDGE_FINAL_FREQUENCY = "Channel edge final frequency"

NOISE_REFERENCE_STATISTICS = "Noise reference statistics"
DETECTION_THRESHOLD = "Detection Threshold"
AVERAGE_CHANNEL_SAMPLE_RATE = "Average Channel sample rate"

# Raw measurement data attributes
NUMBER_OF_LOOPS_ATTRIBUTE = "Number of measurement samples"
SAMPLE_DURATION_ATTRIBUTE = "Measurement sample duration"

# Members to compound type for statistical information
# To be used with data that presents values distributed with a normal PDF
MEAN_MEMBER = "Mean"
STANDARD_DEVIATION_MEMBER = "Standard deviation"
NUMBER_OF_SAMPLES_MEMBER = "Number of samples"
SUM_MEMBER = "Sum"
SUM_OF_SQUARES_MEMBER = "Sum of squares"

# Members to compound type for geolocation information
LATITUDE_MEMBER = "Latitude"
LONGITUDE_MEMBER = "Longitude"
ALTITUDE_MEMBER = "Altitude"
TIMESTAMP_COARSE_MEMBER = "Timestamp coarse"
TIMESTAMP_FINE_MEMBER = "Timestamp fine"

# Site location dataset an attributes
SITE_GEOLOCATION_DATASET = "Site Geolocation"
GEODETIC_DATUM_ATTRIBUTE = "Geodetic Datum"
LATITUDE_STATISTICS_ATTRIBUTE = "Latitude statistics"
LONGITUDE_STATISTICS_ATTRIBUTE = "Longitude statistics"
ALTITUDE_STATISTICS_ATTRIBUTE = "Altitude statistics"

# Members to compound type for measurement log data
ENTRY_TYPE_MEMBER = "Entry type"
ENTRY_VALUE_MEMBER = "Entry value"

LOGBOOK_DATASET = "logbook"

# Reference to the present standard
STANDARD = "Draft:fslobao.github.io"
FILETYPE_CLASS = "Spectrum monitoring digital exchange format"
GEOLOCATION_CLASS = "Location"
TIME_CAPTURE_CLASS = "I/Q"
SPECTROGRAM_CLASS = "Spectrogram"
LEVEL_PROFILE_CLASS = "Level profile"
ACTIVITY_PROFILE_CLASS = "Activity profile"

# Reference to logbook entries
CRFS_HOSTNAME = "Equipment ID"
CRFS_UNIT_INFO = "Measurement Script"
METHOD = "Measurement Method"
