#include <stdint.h>
#include <string>
#include <H5Cpp.h>

using namespace std;

// Global constants to block types
  // Individual block types for easier referencing to an specific block type
    const int32_t V2_16_BIT_IQ_DATA = 6;
    const int32_t V5_16_BIT_IQ_DATA = 66;
    const int32_t V2_8_BIT_SPECTRAL_DATA = 4;
    const int32_t V3_8_BIT_SPECTRAL_DATA = 60;
    const int32_t V5_CLASSIFIER_DATA = 51;
    const int32_t V2_DATA_THREAD_INFORMATION = 3;
    const int32_t V3_DATA_THREAD_INFORMATION = 22;
    const int32_t V4_DATA_THREAD_INFORMATION = 24;
    const int32_t V2_FREE_TEXT_INFORMATION = 5;
    const int32_t V3_FREE_TEXT_INFORMATION = 23;
    const int32_t V2_FREQUENCY_CHANNEL_OCCUPANCY_SM1793 = 8;
    const int32_t V3_FREQUENCY_CHANNEL_OCCUPANCY_SM1880 = 62;
    const int32_t V4_FREQUENCY_CHANNEL_OCCUPANCY_SM1880 = 65;
    const int32_t V5_FREQUENCY_CHANNEL_OCCUPANCY_SM1880 = 69;
    const int32_t V2_GPS_DATA = 2;
    const int32_t V3_GPS_DATA = 40;
    const int32_t V4_SPECTRAL_DATA = 63;
    const int32_t V5_SPECTRAL_DATA = 67;
    const int32_t V2_THRESHOLD_COMPRESSED_DATA = 7;
    const int32_t V3_THRESHOLD_COMPRESSED_DATA = 61;
    const int32_t V4_THRESHOLD_COMPRESSED_DATA = 64;
    const int32_t V5_THRESHOLD_COMPRESSED_DATA = 68;
    const int32_t V3_TIMED_FREE_TEXT_INFORMATION = 41;
    const int32_t V5_TIMED_FREE_TEXT_INFORMATION = 42;
    const int32_t V3_UNIT_AND_JOB_INFORMATION = 21;
    const int32_t V2_UNIT_INFORMATION = 1;
    const int32_t FILE_FOOTER = 20;
    const int32_t UNKNOWN_BLOCKS = 0;

  // For interact running through all block types accessing reference codes (order must be the same as BLOCK_NAME constant array)
    const int BLOCK_CODE[] = {
      6,    
      66,
      4,
      60,
      51,
      3,
      22,
      24,
      5,
      23,
      8,
      62,
      65,
      69,
      2,
      40,
      63,
      67,
      7,
      61,
      64,
      68,
      41,
      42,
      21,
      1,
      0,
      20};

  // For interect running through all block types accessing reference names (order must be the same as BLOCK_CODE)
    const string BLOCK_NAME[] = {
      "V2_16_BIT_IQ_DATA",
      "V5_16_BIT_IQ_DATA",
      "V2_8_BIT_SPECTRAL_DATA",
      "V3_8_BIT_SPECTRAL_DATA",
      "V5_CLASSIFIER_DATA",
      "V2_DATA_THREAD_INFORMATION",
      "V3_DATA_THREAD_INFORMATION",
      "V4_DATA_THREAD_INFORMATION",
      "V2_FREE_TEXT_INFORMATION",
      "V3_FREE_TEXT_INFORMATION",
      "V2_FREQUENCY_CHANNEL_OCCUPANCY_SM1793",
      "V3_FREQUENCY_CHANNEL_OCCUPANCY_SM1880",
      "V4_FREQUENCY_CHANNEL_OCCUPANCY_SM1880",
      "V5_FREQUENCY_CHANNEL_OCCUPANCY_SM1880",
      "V2_GPS_DATA",
      "V3_GPS_DATA",
      "V4_SPECTRAL_DATA",
      "V5_SPECTRAL_DATA",
      "V2_THRESHOLD_COMPRESSED_DATA",
      "V3_THRESHOLD_COMPRESSED_DATA",
      "V4_THRESHOLD_COMPRESSED_DATA",
      "V5_THRESHOLD_COMPRESSED_DATA",
      "V3_TIMED_FREE_TEXT_INFORMATION",
      "V5_TIMED_FREE_TEXT_INFORMATION",
      "V3_UNIT_AND_JOB_INFORMATION",
      "V2_UNIT_INFORMATION",
      "UNKNOWN_BLOCKS",
      "FILE_FOOTER"};

  const int NUMBER_OF_BLOCK_TYPES = 28;
  const int MAXIMUM_BLOCK_NUMBER = V5_FREQUENCY_CHANNEL_OCCUPANCY_SM1880;

// Global constants to block structure
  const char PADDING = 0x00;
  const int BLOCK_HEADER_SIZE = 12;
  const int BLOCK_TRAILER_SIZE = 8;
  const int BLOCK_END_MARKER_SIZE = 4;
  const int BLOCK_CHECKSUM_SIZE = 4;
  const int32_t BLOCK_END_MARKER = 0x55555555;
  const int DATE_SIZE = 8;
  const int INT32T_NUMBER_SIZE = 4;
  const int INT16T_NUMBER_SIZE = 2;
  const int INT8T_NUMBER_SIZE = 1;
  const int HOSTNAME_SIZE = 16;
  const int MINIMUM_HOSTNAME_SIZE = 8;
  const int FREE_TEXT_ID_SIZE = 32;
  const int MINIMUM_FREE_TEXT_ID_SIZE = 8;
  const int TUNING_BLOCK_SIZE = 4;
  const int MINIMUM_TIMED_TEXT_SIZE = 3;
  const int TIMED_TEXT_SIZE = 32;

// Constants associated with the format data representation  
  const double STANDARD_LEVEL_OFFSET = 127.5;
  const double STEP_PER_LEVEL_UNIT = 2.0;

// CRFS Bin entry names to be used on HDF5 Log
  const H5std_string	LOG_TYPE_HOSTNAME("Hostname");
  const H5std_string	LOG_TYPE_UNIT_INFO("Unit info");
  const H5std_string	LOG_TYPE_METHOD("Method");

  const H5std_string	CRFS_BIN_DEFAULT_GEODETIC_DATUM("WGS84");

// CRFS BIN Error codes 

  #define CMP_OK                          0x0000
  #define CMP_ERR                         0x0100

  #define ERR_RADIO_ERROR                 0x02
  #define ERR_GPRS_TRANSMISSION           0x03
  #define ERR_ADC_OVERFLOW                0x04
  #define ERR_INSUFFICIENT_MEMORY         0x05
  #define ERR_UNCALIBRATED_SWEEP          0x06
  #define ERR_BAD_PARAMETER               0x07
  #define ERR_PATH_TIMEOUT                0x08
  #define ERR_SYNC_TIME_PASSED            0x09
  #define ERR_MULTITRIG_DELAY             0x0A
  #define ERR_UART10M_BIT                 0x0B
  #define ERR_SYNCLINC_NO_RTC_UPDATE      0x0C
  #define ERR_DDS_OVERFLOW                0x0D
  #define ERR_SYNCLINC_TIMEOUT            0x0E
  #define ERR_SYNCLINC_CHECKSUM           0x0F
  #define ERR_SYNCLINC_BIT                0x10
  #define ERR_PROM_BUF_VERIFY             0x11
  #define ERR_PROM_BUSY_TIMEOUT           0x12
  #define ERR_COMMAND_CANCELLED           0x13
  #define ERR_INSUFFICIENT_AGC_TABLES     0x14
  #define ERR_WATSON_WATT_POWER           0x15
  #define ERR_OVER_TEMPERATURE            0x16
  #define ERR_MAIN_SYNTH_LOCK_FAIL        0x17
  #define ERR_ONEPPS_TIMEOUT              0x18
  #define ERR_SW18_MAP_VERIFY             0x19
  #define ERR_INVALID_COMMAND             0x1A

  #define ERR_NONE                        0xAA

