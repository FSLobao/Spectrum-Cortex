// this program converts data stored in a char format into float using a linear transformation and evaluate the moving average along the way, storing the indexes where this moving average sum first croesses above a threshold

// Libraries
    #include <iostream>
    #include <vector>
    #include <cmath>
    #include <chrono>
    #include "gnuplot-iostream.h"
    #include "level_differential_detector.h"

// Namespaces
    using namespace std;
    using namespace std::chrono;

// constants that control the program
    const int DATA_SIZE = 2048;
    
// factors for linear transformation. Will place values originally coded from 0 to 255 to the range between -64 to +64 
    // intercept coefficient 
    const double ALPHA = 10.0;
    // slope coefficient 
    const double BETA = 2.0;

// set window size for moving sum and the thershold based on the window size, i.e equivalent to the moving average
    const int WINDOW_SIZE = 50;
    const int WINDOW_OFFSET = 5;
    const float THRESHOLD = 5.0; // will hit the middle value
    const int MINIMUM_ASCENDING_BREAK_SEPARATION = 100;
    const int MINIMUM_DECENDING_BREAK_SEPARATION = 100;

// fill vector with periodic peaks, flatted on the top above the cut
void fill_data (vector<uint8_t> *data_array,double period = 4.0) {
    const double PI = 3.14159265;
    const double NOISE_RANGE = 5;
    const double SIGNAL_RANGE = 255-NOISE_RANGE;
    const double SHIFT_RANGE_PER_CYCLE = 0.125;
    const double CUT_LEVEL = 0.1;

    int shift = (int)round((rand()/RAND_MAX) * ((double)data_array->size()/period) * SHIFT_RANGE_PER_CYCLE);

    period = DATA_SIZE / ( period * 2.0 * PI );

    double y;
    for(int x=0; x<data_array->size(); x++) {
        y = ((pow(1/(sin((double)(x+shift)/period)+2.0),8.0)*SIGNAL_RANGE)+NOISE_RANGE);
        if ( y > ( SIGNAL_RANGE * CUT_LEVEL ) ) y =  SIGNAL_RANGE * CUT_LEVEL;
        y = y -(NOISE_RANGE*rand()/RAND_MAX);
        data_array->at(x) = (uint8_t)round(y); // range between 0 and 254        
	}
}

// plot data from vector using indexes as 
void plot_data (float          *first_data_array,
                double         *second_data_array,
                double         *third_data_array,
                double         *fourth_data_array,
                int             array_length,
                vector<long>   *positive_threshold_crossing,
                vector<long>   *negative_threshold_crossing,
                int             output_resolution = 2048) {

    // variables used for plotting
        Gnuplot gp;

        vector<pair<double, double>> first_xy_pair;
        vector<pair<double, double>> second_xy_pair;
        vector<pair<double, double>> third_xy_pair;
        vector<pair<double, double>> fourth_xy_pair;
        vector<pair<double, double>> mark_positive_xy_pair;
        vector<pair<double, double>> mark_negative_xy_pair;

        double maximum = 0;
        double minimum = 0;

        double y;
        int step = array_length / output_resolution;

    // Lambda function that update the maximum and minimum values used for controling the range of the plot
        auto update_max_min = [&] {
            if ( y > maximum ) { 
                maximum = y;
            }
            else if ( y < minimum ) minimum = y;
        };

        for(int x=0; x<array_length; x+=step) {
            y = (double)first_data_array[x];
            first_xy_pair.push_back(make_pair((double)x, y));
            update_max_min();

            y = second_data_array[x]/WINDOW_SIZE;
            second_xy_pair.push_back(make_pair((double)x, y));
            update_max_min();

            y = third_data_array[x]/WINDOW_SIZE;
            third_xy_pair.push_back(make_pair((double)x, y));
            update_max_min();

            y = fourth_data_array[x];
            fourth_xy_pair.push_back(make_pair((double)x, y));
            update_max_min();
        }

        cout << "\n - Positive break positions: ";
        for(vector<long>::iterator it = positive_threshold_crossing->begin(); it != positive_threshold_crossing->end(); ++it) {
            mark_positive_xy_pair.push_back(make_pair((double)*it,minimum));
            mark_positive_xy_pair.push_back(make_pair((double)*it,maximum));
            mark_positive_xy_pair.push_back(make_pair((double)*it,minimum));
            cout << *it << ", ";
        };

        cout << "\n - Negative break positions: ";
        for(vector<long>::iterator it = negative_threshold_crossing->begin(); it != negative_threshold_crossing->end(); ++it) {
            mark_negative_xy_pair.push_back(make_pair((double)*it,minimum));
            mark_negative_xy_pair.push_back(make_pair((double)*it,maximum));
            mark_negative_xy_pair.push_back(make_pair((double)*it,minimum));
            cout << *it << ", ";
        }

        cout << "\n - Maximum: " << maximum << "; Minimum: " << minimum << "\n"; 

        gp << "set xrange [0:" << array_length << "]\nset yrange [" << minimum << ":"<< maximum << "]\n";
        gp << "plot '-' with points title 'level', '-' with points title 'average', '-' with points title 'difference', '-' with points title 'correction_factor', '-' with lines title 'Positive breaks', '-' with lines title 'Negative breaks'\n";
        gp.send1d(first_xy_pair);
        gp.send1d(second_xy_pair);
        gp.send1d(third_xy_pair);
        gp.send1d(fourth_xy_pair);
        gp.send1d(mark_positive_xy_pair);
        gp.send1d(mark_negative_xy_pair);
}

int main() {
    // let input variables
        const int NUMBER_OF_PARAMETERS = 6;
        pair<string,int> user_input[NUMBER_OF_PARAMETERS] ={
            make_pair("Data array size",DATA_SIZE),
            make_pair("Window size",WINDOW_SIZE),
            make_pair("Window offset",WINDOW_OFFSET),
            make_pair("Threshold",THRESHOLD),
            make_pair("Minimum separation between a positive and a negative break",MINIMUM_ASCENDING_BREAK_SEPARATION),
            make_pair("Minimum separation between a negative and a positive break",MINIMUM_DECENDING_BREAK_SEPARATION) };

        string typed_data;
        cout << "Type the indicated parameter. (Enter to keep the default) \n";
        for (int i = 0; i < NUMBER_OF_PARAMETERS; i++) {
            cout << " - " << user_input[i].first << " (" << user_input[i].second << "): ";
            getline(cin, typed_data);
            if (typed_data.length() != 0) istringstream(typed_data) >> user_input[i].second;
        }

    // synthetic input data is loaded into memory by the fill_data function
        vector<uint8_t> input_data(user_input[0].second);
        fill_data(&input_data);

    // synthetic correction factor data is loaded into memory
        vector<double> correction_factor_data(user_input[0].second);
        for(int i=0; i<correction_factor_data.size(); i++) {
            correction_factor_data[i] = (((double)i*20.0)/((double)user_input[0].second*(double)BETA)) - (5.0 * (double)ALPHA);
        };        

    // create output data arrays
        vector<float> output_data(user_input[0].second);
        vector<long> positive_threshold_crossing;
        vector<long> negative_threshold_crossing;

        cout << "\nComputation Summary:";

    // Starts the clock to measure performance of the silly version
        high_resolution_clock::time_point timer_start = high_resolution_clock::now();

    // construct the object to perform the detection
        signal signal_data(&input_data[0], &correction_factor_data[0], user_input[0].second, BETA, ALPHA, &output_data[0]);

    // perform the comptation and detection
        signal_data.run_detector(user_input[3].second, user_input[1].second, user_input[2].second, user_input[4].second, user_input[5].second, &positive_threshold_crossing, &negative_threshold_crossing);

    // Stop the clock to measure performance of the silly version
        high_resolution_clock::time_point timer_end = high_resolution_clock::now();

    // Plot results
        plot_data(&output_data[0], &signal_data.output_moving_sum[(int)round((double)user_input[1].second/2.0)], signal_data.sum_difference, &correction_factor_data[0], user_input[0].second, &positive_threshold_crossing, &negative_threshold_crossing);

    // Compute the duration
        auto execution_duration = duration_cast<microseconds>( timer_end - timer_start ).count();

    // Print the result
        cout << " - Execution time = " << (float)execution_duration/1000.0 << " ms \n";

    return 0;
}