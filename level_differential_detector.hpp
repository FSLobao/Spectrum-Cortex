
// Libraries
    #include <iostream>
    #include <vector>
    #include <cmath>

// used only for debug with "level_differential_detector.h" 
    #include "gnuplot-iostream.h"
    #include <string>
    #include <sstream>

// Namespaces
    using namespace std;

// structure to store trace data relative to one capture 
struct detection_flag {
    // data fields
        // trace number where break was detected
            long    trace;
        // position at the trace 
            long    trace_position;
        // position at the trace at which the segment ending at the flag starts, used to process flag relations for multiple trace consolidation
            long    segment_begin_position;
        // level sum between the current flag and the initial flag
            double  sum_to_flag;
        // type of the break, TRUE for signal starting at the flag and FALSE for noise starting at the flag
            bool    type;
        // power density between the current flag and the next
            double  density;

    // null argument constructor for this structure
        detection_flag() :  trace(0),
                            trace_position(0),
                            segment_begin_position(0),
                            sum_to_flag(0),
                            type(false),
                            density(0.0) {}

    // constructor for an specific set of arguments
        detection_flag(long    trace_data,
                       long    trace_position_data,
                       double  *output_sum,
                       bool    type_data) {
            trace = trace_data;
            trace_position = trace_position_data;
            segment_begin_position = 0;
            sum_to_flag = output_sum[trace_position_data];
            type = type_data;
            density = 0.0;
        }

    // operator to perfor vector sorting
        bool operator < (const detection_flag& str) const
        {
            return (trace_position < str.trace_position);
        }
};

// Object that perfrom threshold detection based on the differential value between moving windows. Result is stored as the boudaries for threshold crossing
struct signal {
    // Class Members
        // array containing the original raw data to be processed
            uint8_t *input_data;
        // array with correction factor to be applied, include format conversion factor and might include antenna factor.
            double *correction_factor; 
        // angular coefficient 
            double beta;
        // intercept coefficient
            double alpha;
        // array containing the resulting data
            float *output_data;
        // length of the input and output arrays
            int array_length;
        // window size used for sum computation
            int window_size;
        // offset between the first and the second window 
            int window_offset;
        // array with the sum of the value for previous n elements of the output array of same index, where n corresponds to the window_size
            double *output_moving_sum;
        // array with the difference between the value of the window sum, with index adjusted to correspond to the current output value, i.e. middle of the offset betweem the considered windows
            double *sum_difference;
        // array with the simple sum of the value for all previous elements of the output array of same index
            double *output_sum;

        // define constants used as reference paramenters
            const int MINIMUM_WINDOW_SIZE = 2; 

    // Null constructor
        signal() {    // main members
            input_data = nullptr;
            correction_factor = nullptr;
            beta = 0.0;
            alpha = 0.0;
            output_data = nullptr;
            array_length = 0;
            output_moving_sum = nullptr;
            output_sum = nullptr;
            read_input_pointer = nullptr;
            correction_factor_pointer = nullptr;
            window_start_output_pointer = nullptr;
            window_end_output_pointer = nullptr;
            window_size = MINIMUM_WINDOW_SIZE;
            window_offset = 0;
            first_window_sum_pointer = nullptr;
            second_window_sum_pointer = nullptr;
            sum_difference = nullptr;
            sum_difference_pointer = nullptr;
        }

    // constructor with array length, input, output and crossing vector pointers
        signal(uint8_t                 *input_data_pointer,
               double                  *correction_factor_data,
               int                      array_length_data,
               double                   beta_data,
               double                   alpha_data,
               float                   *output_data_pointer,
               double                  *output_sum_pointer_data) {

            input_data = input_data_pointer;
            read_input_pointer = input_data_pointer; 

            correction_factor = correction_factor_data;
            correction_factor_pointer = correction_factor_data;
            
            array_length = array_length_data;
            beta = beta_data;
            alpha = alpha_data;
            
            output_data = output_data_pointer;
            window_start_output_pointer = output_data_pointer; 
            window_end_output_pointer = window_start_output_pointer;
            
            output_sum = output_sum_pointer_data;
            output_sum_pointer = output_sum_pointer_data;
            
            output_moving_sum = new double[array_length_data];
            first_window_sum_pointer = output_moving_sum;
            second_window_sum_pointer = output_moving_sum;
            sum_difference = new double[array_length_data];
            sum_difference_pointer = sum_difference;
            // TODO: Perform test to ensure that array length is larger than the sum two windows and the offset, such as to allow any computation, issue error and stop. Issue warning it too small
        }

    // perform the differential trace detaction with transformation
        void run_detector(
            // level above the noise floor that will be considered for carrier detection
                double                    detection_threshold,
            // number of bis on the moving window used for average computation
                int                       window_size_data,
            // number of bins between the two windows used for differential computation
                int                       window_offset_data,
            // minimum number of bins between a negative differential peak and the start of a new peak search
                int                       minimum_ascending_break_separation,
            // minimum number of bins between a positive differential peak and the start of a new peak search
                int                       minimum_descending_break_separation,
            // minimum number of bins for the channel width
                int                       minimum_channel_width,
            // vector that stores the threasholds crossings 
                vector<detection_flag>   *threshold_crossing,
            // vector that stores the noise reference computed for the trace
                vector<double>           *noise_reference_output,
            // trace number, used as reference for the update of the threshold crossing vector
                long                      trace_number)
        {            
            // create vector for storage of the raw crossing data
                vector<detection_flag>   raw_threshold_crossing;

            // update main detection paramenters shared by object methods ensuring minimum functional values
                if (window_size_data > MINIMUM_WINDOW_SIZE ) { 
                    window_size = window_size_data; }
                else {
                    window_size = MINIMUM_WINDOW_SIZE;
                };
                window_offset = window_offset_data;

            // compute the actual detection_threshold to be used on the window sum such as if it was the average.
                double window_detection_threshold = detection_threshold * (double)window_size;
            
            // Create a pointer flag to signal the end of the array for iteration purposes.
                uint8_t * array_end = &input_data[array_length-1];

            // Create a pointer flag that will signal an arbitrary processing point on the array
                double * array_flag; 

            // Create pointer for searching the output previous values taking the initial position as the first valid value for window size 
                double * start_break_search = &output_moving_sum[window_size];
                double * previous_sum;

            // compute the shift between the indexes of the sum array and the input array;
                ptrdiff_t array_shift = (ptrdiff_t)round((double)window_size/2.0); 

                ptrdiff_t sum_minimum_index = 0;
                ptrdiff_t sum_maximum_index = 0;
                ptrdiff_t differential_peak_index = 0;
                ptrdiff_t index_offset = 0;
            
            // loop control flag
                bool inside_the_array = true;

            // Macro function used to test the array end
                #define check_array_end() if ( read_input_pointer == array_end ) inside_the_array = false;

            // compute the sum for length of the first window
                start();

            // TODO: Originally conceived to take into account the maximum, minumum and differential peak of the value in order to further reduce noise effect. Best result achieved using only differential but algorithm not reduced to this effect
            // sweep the remaining length of the input array computing the output array, the sum array and performing detection
                while ( read_input_pointer < array_end ) {
                    // proceed with window computation for one step
                        proceed_one_step();
                        
                    // If the absolute value of the difference between the window sum surpass the threshold, might be a positive or a negative peak
                        if (fabs(*sum_difference_pointer) > window_detection_threshold) {
                            // test if it is a positive peak, i.e. absolute value equals to the actual value
                            if ( fabs(*sum_difference_pointer) == *sum_difference_pointer ) {

                                // Set flag to mark the end of the minimum break separation
                                    array_flag = &first_window_sum_pointer[minimum_ascending_break_separation];

                                // Proceed computation searching for the maximum on the differential value. Peak defined by a sequence of smaller, larger, smaller numbers.
                                    while ( inside_the_array ) {
                                        // detect if the sum_difference reaches a positive peak
                                            if ((*sum_difference_pointer <= sum_difference_pointer[-1]) && (sum_difference_pointer[-1] >= sum_difference_pointer[-2])) {
                                                differential_peak_index = sum_difference_pointer - sum_difference; //  Differential array is aligned due to the initialization
                                                break;
                                            }

                                            proceed_one_step();

                                            check_array_end();
                                    }
/*
                                // search for the last minimum over the sum array, from the position of the differential peak until the last break position.
                                    sum_minimum_index = 0.0;
                                    previous_sum = &output_moving_sum[differential_peak_index];
                                    while ( previous_sum > start_break_search ){                                        
                                        // Minimum defined by a sequence of larger, smaller, larger numbers.
                                            if ((*previous_sum >= previous_sum[-1]) && (previous_sum[-1] <= previous_sum[-2])) {
                                                // compute the index of the peek
                                                    sum_minimum_index = previous_sum - output_moving_sum;
                                                // array shift of half the window size is need to align the output sum with the other array. Differential array os aligned due to the initialization
                                                    sum_minimum_index -= array_shift;
                                                    break;    
                                            }
                                            previous_sum--;
                                    }

                                // Proceed computation searching for the maximum on the sum value. Peak defined by a sequence of smaller, larger, smaller numbers.
                                    while ( inside_the_array ) {
                                        // check for the peak
                                            if ((*first_window_sum_pointer <= first_window_sum_pointer[-1]) && (first_window_sum_pointer[-1] >= first_window_sum_pointer[-2])) {
                                                // compute the index of the peek                                                
                                                    sum_maximum_index = first_window_sum_pointer - output_moving_sum;
                                                // array shift of half the window size is need to align the output sum with the other array. Differential array os aligned due to the initialization
                                                    sum_maximum_index -= array_shift; 
                                                    break;    
                                            }

                                            proceed_one_step();

                                            check_array_end();
                                    }

                                // Mark the current position as the reference to be used as minimum start point for searching a peak on next call
                                    start_break_search = &first_window_sum_pointer[minimum_descending_break_separation];

                                // If the end of the array was not reached at any point, perform the complete computation of the break based on the three measurements performed
                                    if( inside_the_array && (sum_maximum_index < array_length) ) {
*/    
                                        // Mark the break assuming that the differential peak is close to the median between maximum and minimum, i.e. the break will be set close to the minimum
                                            raw_threshold_crossing.push_back(detection_flag(trace_number,
                                                                                            //(long)round( ((2.0*(double)differential_peak_index) - (double)sum_maximum_index + (double)sum_minimum_index)/2.0 ),
                                                                                            (long)differential_peak_index,
                                                                                            // (long)sum_maximum_index,
                                                                                            output_sum,
                                                                                            false));
/*                                    } // If the break occurred while searching for the sum peak or the sum_differential peak, the best estimative of the break will be the sum_minimum_index 
                                    else if ( sum_minimum_index != 0.0 ) raw_threshold_crossing.push_back(detection_flag(trace_number,(long)sum_minimum_index, output_sum, false));

                                // Proceed computation until the end of the minimum break separation in case of this point not already being reached
                                    if ( first_window_sum_pointer < array_flag ) proceed(array_flag-first_window_sum_pointer);
*/                                
                                // keep sweeping the the array until the sum gets bellow the thershold after a minimum beak separation limit is reached
                                    while (*sum_difference_pointer > window_detection_threshold ) {
                                        // break the loop in case the array ends
                                            if ( read_input_pointer >= array_end ) break;
                                            proceed_one_step();
                                    };

                            // If it is a peak, but negative
                            } else {

                                // Set flag to mark the end of the minimum break separation
                                    array_flag = &first_window_sum_pointer[minimum_descending_break_separation];

                                // Proceed computation searching for the minimum on the differential sum array. Minimum defined by a sequence of larger, smaller, larger numbers.
                                    while ( inside_the_array ) {
                                        // detect if the sum_difference reaches a negative peak
                                            if ((*sum_difference_pointer >= sum_difference_pointer[-1]) && (sum_difference_pointer[-1] <= sum_difference_pointer[-2])) {
                                                differential_peak_index = sum_difference_pointer - sum_difference; //  Differential array is aligned due to the initialization
                                                break;
                                            }

                                            proceed_one_step();

                                            check_array_end();
                                    }

/*
                                // search for the last maximum over the sum array, from the current position until the last break position. Maximum defined by a sequence of smaller, larger, smaller numbers.
                                    sum_maximum_index = 0;
                                    previous_sum = first_window_sum_pointer;
                                    while ( previous_sum > start_break_search ){

                                        if ((*previous_sum <= previous_sum[-1]) && (previous_sum[-1] >= previous_sum[-2])) {
                                                sum_maximum_index = previous_sum - output_moving_sum; 
                                            // array shift of half the window size is need to align the output sum with the other array.
                                                 sum_maximum_index -= array_shift;
                                                break;    
                                        }
                                        previous_sum--;
                                    }

                                // search for the minimum over the sum array, from the current position until the last break position. Minimum defined by a sequence of larger, smaller, larger numbers.
                                    while ( inside_the_array ) {
                                        // check for the peak
                                            if ((*first_window_sum_pointer >= first_window_sum_pointer[-1]) && (first_window_sum_pointer[-1] <= first_window_sum_pointer[-2])) {
                                                    sum_minimum_index = first_window_sum_pointer - output_moving_sum;
                                                // array shift of half the window size is needd to align the output sum with the other array. Differential array os aligned due to the initialization
                                                    sum_minimum_index -= array_shift; 
                                                    break;    
                                            }

                                        // compute one more step
                                            proceed_one_step();

                                            check_array_end();
                                    }

                                // Mark the current position as the reference to be used as minimum start point for searching a peak on next call
                                    start_break_search = &first_window_sum_pointer[minimum_ascending_break_separation];

                                // If the end of the array was not reached at any point, perform the complete computation of the break based on the three measurements performed
                                    if( inside_the_array && (sum_minimum_index < array_length) ) {
*/                                        
                                        // Mark the break assuming that the differential peak is close to the median between maximum and minimum, i.e. the break will be set close to the minimum
                                            raw_threshold_crossing.push_back(detection_flag(trace_number,
                                                                                            //(long)round( ((2.0*(double)differential_peak_index) + (double)sum_maximum_index - (double)sum_minimum_index)/2.0 ),
                                                                                            (long)differential_peak_index,
                                                                                            //(long)sum_maximum_index,
                                                                                            output_sum,
                                                                                            true));
/*                                    } // If the break occurred while searching for the sum peak or the sum_differential peak, the best estimative of the break will be the sum_maximum_index 
                                    else if ( sum_maximum_index != 0.0 ) raw_threshold_crossing.push_back(detection_flag(trace_number,(long)sum_maximum_index,output_sum, true));

                                // Proceed computation until the end of the minimum break separation in case of this point not already being reached
                                    if ( first_window_sum_pointer < array_flag ) proceed(array_flag-first_window_sum_pointer);
*/                                
                                // keep sweeping the the array until the sum gets above the thershold after a minimum beak separation limit is reached
                                    while (*sum_difference_pointer < -window_detection_threshold ) {
                                        // break the loop in case the array ends
                                            if ( read_input_pointer >= array_end ) break;
                                            proceed_one_step();
                                    };
                            };
                        };
                };

            // If at least one threshold crossings was detected, perform flags cleansing
                if (raw_threshold_crossing.size() > 0 ) {
                    /* debug */
                        //cout << dec;
                        //cout << "\n Trace: "<< trace_number << " - Debug flag cleansing for " << raw_threshold_crossing.size() << " detected flags\n";

                    // create a flag for the last flag position 
                        raw_threshold_crossing.push_back(detection_flag(trace_number, array_length-1, output_sum, false));

                    // sort the threshold_crossing vector to ensure that all breaks are in order before cleaning. It is conceavable that the previous algorithm results on a vector that is not ordered
                        sort( raw_threshold_crossing.begin(), raw_threshold_crossing.end( ));

                    // initialize the noise reference as the density until the first flag
                        double noise_reference = output_sum[raw_threshold_crossing.at(0).trace_position] / (double) raw_threshold_crossing.at(0).trace_position;
                        raw_threshold_crossing.at(0).density = noise_reference;

                    // initialize the segment begin position for the first segment
                        raw_threshold_crossing.at(0).segment_begin_position = 0;

                    // confirm status of the segment from the begining until the first flag, if noise (false) or signal (true);
                        if ( raw_threshold_crossing.at(0).density < (noise_reference + detection_threshold) ) { 
                            // set the first segment as noise (false)
                                raw_threshold_crossing.at(0).type = false;
                        }
                        else {
                            // set the first segment as signal (true)
                                raw_threshold_crossing.at(0).type = true;
                        }

                    // numeric interator is used. Not used vector interator since multiple elements will be accessed at the same iteration
                        int it = 1;
                    // loop through all detected crossings computing the power density up to the last flag and finding the minimum value, that will be set as the noise reference
                        while ( it < raw_threshold_crossing.size() ) {                     
                                raw_threshold_crossing.at(it).density = (raw_threshold_crossing.at(it).sum_to_flag - raw_threshold_crossing.at(it-1).sum_to_flag) / (raw_threshold_crossing.at(it).trace_position - raw_threshold_crossing.at(it-1).trace_position);
                                it++;
                        }

                    // compute the noise value as the average of the lower part of the density vector
                        noise_reference = find_noise(&raw_threshold_crossing);
                     
                    // control flag to iterate until the maximum merging of segments is achieved
                        bool flag_deletion = false;
                    // perform flag deletion until all equivalent fragments were merged
                        do {
                            // reset flag deletion flag
                                flag_deletion = false;

                            // numeric interator is used. Not used vector interator since multiple elements will be accessed at the same iteration
                                it = 1;

                            // loop through all detected crossings updating the type and deleting flags if density before and after the flag are equivalent
                                while ( it < raw_threshold_crossing.size() ) {
                                    // if the density of the segment before the flag is close to the minimum density, classify as noise (false)
                                        if ( raw_threshold_crossing.at(it).density < (noise_reference + detection_threshold) ) { 
                                            raw_threshold_crossing.at(it).type = false;
                                        }
                                    // if the segment before the flag is above the threshold, classify as signal (true) 
                                        else {
                                            raw_threshold_crossing.at(it).type = true;
                                        }

                                    // if the previous segment and the current segment have the same classification, merge then
                                        if ( raw_threshold_crossing.at(it).type == raw_threshold_crossing.at(it-1).type ) {
                                            // recompute density and segment begin position for the current flag, taking care of the exception of the first flag. No need to update the noise reference or segment classification since the density of the merged segment will be necessarily between the density values of the initial segments
                                                if ( it == 1 ) {
                                                    raw_threshold_crossing.at(it).density = output_sum[raw_threshold_crossing.at(it).trace_position] / (double) raw_threshold_crossing.at(it).trace_position;
                                                    raw_threshold_crossing.at(it).segment_begin_position = 0;
                                                }
                                                else {
                                                    raw_threshold_crossing.at(it).density = (raw_threshold_crossing.at(it).sum_to_flag - raw_threshold_crossing.at(it-2).sum_to_flag) / (raw_threshold_crossing.at(it).trace_position - raw_threshold_crossing.at(it-2).trace_position);
                                                    raw_threshold_crossing.at(it).segment_begin_position = raw_threshold_crossing.at(it-2).trace_position;
                                                }

                                            // delete previous flag, merging both segments;
                                                raw_threshold_crossing.erase(raw_threshold_crossing.begin()+it-1);

                                            // set flag deletion flag
                                                flag_deletion = true;

                                        }
                                    // else adjacent segments have different classification
                                        else {
                                            // set the begin postion for the segment at the previous flag position
                                                raw_threshold_crossing.at(it).segment_begin_position = raw_threshold_crossing.at(it-1).trace_position;

                                            // move to the next flag
                                                it++;
                                        }
                                }

                            // if there are remainig at least two flags
                                if (raw_threshold_crossing.size()>1) {
                                    // set the begin position for the end flag
                                        raw_threshold_crossing.at(raw_threshold_crossing.size()-1).segment_begin_position = raw_threshold_crossing.at(raw_threshold_crossing.size()-2).trace_position;
                                }

                            // loop through flags to delete any flag pair that defines a channel that is too narrow 
                                it = 2;
                                noise_reference = raw_threshold_crossing.at(0).density;
                                while ( it < raw_threshold_crossing.size()-1 ) {
                                    // if the channel defined as occupied
                                        if ( raw_threshold_crossing.at(it).type ) {
                                            // if the busy channel is too narrow                                
                                                if ( raw_threshold_crossing.at(it).trace_position - raw_threshold_crossing.at(it).segment_begin_position < minimum_channel_width ) {
                                                    // bypass the two consecutive crossings linking the previous and the following of the pair
                                                        raw_threshold_crossing.at(it+1).segment_begin_position = raw_threshold_crossing.at(it-2).trace_position;
                                                        raw_threshold_crossing.at(it+1).density = (raw_threshold_crossing.at(it+1).sum_to_flag - raw_threshold_crossing.at(it-2).sum_to_flag) / (double)(raw_threshold_crossing.at(it+1).trace_position - raw_threshold_crossing.at(it+1).segment_begin_position);

                                                    // delete the two inner flags
                                                        raw_threshold_crossing.erase(raw_threshold_crossing.begin()+it);
                                                        raw_threshold_crossing.erase(raw_threshold_crossing.begin()+it-1);
                                                        flag_deletion = true;


                                                }
                                        }
                                        it++;
                                }

                            // update the noise reference
                                noise_reference = find_noise(&raw_threshold_crossing);
                                
                        } while ( flag_deletion );    // TODO: check if noise level is flat for all the band, if not, split into two and repeat evaluation until noise reference is flat.
                    
                    // stores the final noise reference for later use
                        noise_reference_output->push_back(noise_reference); 
                }

            // Insert new crossings on the threshold crossing vector received as input and stored with the trace. 
                threshold_crossing->insert(threshold_crossing->end(),raw_threshold_crossing.begin() ,raw_threshold_crossing.end());
        }

    // plot the detection results for a segment of the data. Only possible after detection
        void plot_detection(int start_position,
                            int end_position,
                            int step,
                            int trace_number,
                            vector<detection_flag>   *threshold_crossing)
        {
            // Check if detection was performed befor proceeding
                if (threshold_crossing == nullptr) {
                    cout << "\n\t\t\"Warning\": \"Detection not performed, debug plotting is not available\",";
                    return;
                }

            // Check if range paramenters are properly set
                if ( end_position > array_length ) end_position = array_length;
                if ( start_position > array_length ) start_position = array_length;
                if ( end_position < 0 ) end_position = 0;
                if ( start_position < 0 ) start_position = 0;

                if ( start_position == end_position )  {
                    cout << "\n\t\t\"Warning\": \"No valid plot range selected\",";
                    return;
                }

                int x = start_position; 
                if ( start_position > end_position ) {
                    start_position = end_position;
                    end_position = x;
                }

            // Create vectors to the data to be plotted
                vector<pair<double, double>> output_data_xy_pair;
                vector<pair<double, double>> output_sum_xy_pair;
                vector<pair<double, double>> sum_difference_xy_pair;

                vector<pair<double, double>> mark_positive_xy_pair;
                vector<pair<double, double>> mark_negative_xy_pair;

                double maximum = 0;
                double minimum = 0;

                double y;

            // Lambda function that update the maximum and minimum values used for controling the range of the plot
                auto update_max_min = [&] {
                    if ( y > maximum ) { 
                        maximum = y;
                    }
                    else if ( y < minimum ) minimum = y;
                };

                for(x=start_position; x<end_position; x+=step) {
                    y = (double)output_data[x];
                    output_data_xy_pair.push_back(make_pair((double)x, y));
                    update_max_min();

                    y = sum_difference[x]/window_size;
                    sum_difference_xy_pair.push_back(make_pair((double)x, y));
                    update_max_min();
                }

                int offset = (int)round((double)window_size/2.0);
                if (end_position+offset > array_length) end_position = array_length;
                for(x=start_position; x<end_position; x+=step) {
                    y = output_moving_sum[x+offset]/window_size;
                    output_sum_xy_pair.push_back(make_pair((double)x, y));
                    update_max_min();
                }

            // Create plot
                Gnuplot gp;
                stringstream title;
                title << "set title \"Debug detection plot on trace " << trace_number << "\"\n";
                gp << title.str().c_str(); 

            // Create label for positive breaks
                stringstream label_positive;
                stringstream label_negative;

                //label_positive << "set label 1 \"Positive break position: ";
                //label_negative << "set label 2 \"Negative break position: ";

            // Prepare points and label for positive breaks
                const char* separator_positive = "";
                const char* separator_negative = "";
                for(vector<detection_flag>::iterator it = threshold_crossing->begin(); it != threshold_crossing->end(); ++it) {
                    if ( (it->trace_position > (long)start_position) && (it->trace_position < (long)end_position) ) { 
                        if ( it->type ) {
                            mark_positive_xy_pair.push_back(make_pair((double)it->trace_position,minimum));
                            mark_positive_xy_pair.push_back(make_pair((double)it->trace_position,maximum));
                            mark_positive_xy_pair.push_back(make_pair((double)it->trace_position,minimum));
                            // label_positive << separator_positive << it->trace_position;
                            // separator_positive = ", ";
                        }
                        else {
                            mark_negative_xy_pair.push_back(make_pair((double)it->trace_position,minimum));
                            mark_negative_xy_pair.push_back(make_pair((double)it->trace_position,maximum));
                            mark_negative_xy_pair.push_back(make_pair((double)it->trace_position,minimum));
                            // label_negative << separator_negative << it->trace_position;
                            // separator_negative = ", ";
                        }
                    }
                };

                //label_positive <<  "\" at graph 0.02, 0.50, 0 left norotate back textcolor rgb \"#56b4e9\"  nopoint\n";
                //label_negative <<  "\" at graph 0.02, 0.45, 0 left norotate back textcolor rgb \"#56b4e9\"  nopoint\n";
                //gp << label_positive.str().c_str();
                //gp << label_negative.str().c_str();

            // Plot data
                gp << "set xrange [" << start_position << ":" << end_position << "]\n";
                gp << "set yrange [" << minimum << ":"<< maximum << "]\n";
                gp << "plot '-' with linespoints title 'Output Data', '-' with linespoints title 'Moving Average', '-' with linespoints title 'Difference', '-' with lines title 'Flag Signal End', '-' with lines title 'Flag Noise End'\n";
                gp.send1d(output_data_xy_pair);
                gp.send1d(output_sum_xy_pair);
                gp.send1d(sum_difference_xy_pair);
                gp.send1d(mark_positive_xy_pair);
                gp.send1d(mark_negative_xy_pair);
        }

private:
    // Iteration pointers are kept as private members and are used to control the conversion and detection process
        // interator over the input_data array
            uint8_t         *read_input_pointer;
        // interator over the correction_factor array
            double          *correction_factor_pointer;
        // iterator over the output array corresponding to the element under computation 
            float           *window_start_output_pointer; 
        // iterator over the output array corresponding to the last element of the moving average computation
            float           *window_end_output_pointer;
        // iterator over the output_moving_sum array corresponding to the first window to be used for computation of the sum difference
            double          *first_window_sum_pointer;
        // iterator over the output_moving_sum array corresponding to the second window to be used for  computation of the sum difference
            double          *second_window_sum_pointer;
        // iterator over the sum_difference array to be used for detection
            double          *sum_difference_pointer;
        // iterator over the output_sum array to be used to compute the sum over any segment of the array
            double          *output_sum_pointer;

    // Macro expresion to compute the output element in the array from the corresponding input element
        #define compute_output() *window_start_output_pointer = ((float)(*read_input_pointer)/beta) + alpha + *correction_factor_pointer;

    // Macro expresion to compute the sum value of the moving window
        #define compute_window_sum() *first_window_sum_pointer = first_window_sum_pointer[-1] + *window_start_output_pointer - *window_end_output_pointer;

    // Macro expresion to compute the difference between windows
        #define compute_sum_difference() *sum_difference_pointer = *first_window_sum_pointer - *second_window_sum_pointer;

    // Macro expresion to compute sum value of the output
        #define compute_output_sum() *output_sum_pointer = output_sum_pointer[-1] + *window_start_output_pointer;

    // Macro expresion to increment only the pointers used for the output computation
        #define increment_some_pointer() read_input_pointer++;          \
                                         correction_factor_pointer++;   \
                                         window_start_output_pointer++; \
                                         first_window_sum_pointer++;    \
                                         output_sum_pointer++;

    // Macro expresion to increment all pointers used only for the output computation
        #define increment_all_pointer()  increment_some_pointer();      \
                                         window_end_output_pointer++;   \
                                         second_window_sum_pointer++;   \
                                         sum_difference_pointer++;

    // initialize computation for window sum
        void start(void) {
            // compute the first element on the output and sum array
                compute_output();
                *first_window_sum_pointer = *window_start_output_pointer;
                *output_sum_pointer = *window_start_output_pointer;
                increment_some_pointer();

            // sweep the remaining length of the first window minus one element computing the output and sum array values
                float * pointer_end = &output_data[window_size-1];

                while ( window_start_output_pointer != pointer_end ) {
                    compute_output();
                    *first_window_sum_pointer = first_window_sum_pointer[-1] + *window_start_output_pointer;
                    *output_sum_pointer = *first_window_sum_pointer;
                    increment_some_pointer();
                };

            // compute the last element of the first window leaving the pointers at the last valid position.
                compute_output();
                *first_window_sum_pointer = first_window_sum_pointer[-1] + *window_start_output_pointer;
                *output_sum_pointer = *first_window_sum_pointer;

            // sweep the length of the offset between windows and the second window of the input and antenna factor vectors computing the output vector resulting values
                proceed(window_size+window_offset);
            
            // reset second_window_sum_pointer to the correct reference, moving back the length of the Window Offset that was incorrectly added
                second_window_sum_pointer = &second_window_sum_pointer[-window_offset];

            // reset the sum difference pointer to the initial position;
                sum_difference_pointer = &sum_difference[(int)round((double)window_size+((double)window_offset/2.0))];

            // compute the first power difference. Use previous because pointer to the first window was already incremented by the proceed method
                compute_sum_difference();
        }

    // computation for window sum one step further
        void proceed_one_step(void) {
            increment_all_pointer()

/*      DEBUG CODE
            if (correction_factor_pointer > &correction_factor[array_length-1]) {
                cout << "erro\n";
            }
            if (window_start_output_pointer > &output_data[array_length-1] ) {
                cout << "erro\n";
            }
            if (first_window_sum_pointer > &output_moving_sum[array_length-1] ) {
                cout << "erro\n";
            }
            if (output_sum_pointer > &output_sum[array_length-1] ) {
                cout << "erro\n";
            }
            if (window_end_output_pointer > &output_data[array_length-1] ) {
                cout << "erro\n";
            }
            if (second_window_sum_pointer > &output_moving_sum[array_length-1] ) {
                cout << "erro\n";
            }
            if (sum_difference_pointer > &sum_difference[array_length-1] ) {
                cout << "erro\n";
            }
*/
            compute_output();
            compute_window_sum();
            compute_sum_difference();
            compute_output_sum()
        }

    // computation for window sum for several steps
        void proceed(int number_of_steps) {
        // TODO: Can be optimized to skip the window sum computation until for the bins where this information will be ignored
        // create a flag to finish the loop at the designated number of steps
            float * pointer_end = &window_start_output_pointer[number_of_steps];

        // check if the flag still inside the array;
            if (pointer_end>=&output_data[array_length]) pointer_end = &output_data[array_length-1];

        // iterate the assigned number of steps
            while ( window_start_output_pointer <= pointer_end ) {
                proceed_one_step();
            }
        }

    // return the noise reference from a vector containing the density values between threshold crossings
        double find_noise(vector<detection_flag>   *raw_threshold_crossing) {
            // numeric interator is used. Not used vector interator since multiple elements will be accessed at the same iteration
                int it = 0;
                vector<double> density_values;
            // copy the density values to another vector for reordering
                while ( it < raw_threshold_crossing->size() ) {                     
                        density_values.push_back(raw_threshold_crossing->at(it).density);
                        it++;
                }

            //  sort density values vector
                sort(density_values.begin(),density_values.end());

            // compute the noise value as the average of the lower part of the density vector
                double noise_reference = 0.0;
            // if there are more than three segments on the trace, meaning that there are two or more segments representing noise values
                if ( density_values.size() > 4 ) {
                    // loop through the lower half of the density vector  
                        for (it = 0; it < (int)round((double)density_values.size()/2.0)-1; it++) {
                            // Compute the sum as the noise value
                                noise_reference += density_values.at(it);
                        }
                    // compute the average
                            noise_reference = noise_reference / (double)it;
                }
            // else, if there are 3 or less segments representing noise
                else {
                    // the noise reference will be the one with the lower value, the first on the density vector after reordering
                        noise_reference = density_values.front();
                }
            
                return ( noise_reference );
        }
};
