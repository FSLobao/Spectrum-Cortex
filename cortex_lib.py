#!/usr/bin/python3

import math as m
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tkinter import *
from pandastable import Table, TableModel
import pandas as pd


import h5_spectrum as H5

STAT_NORMAL = np.dtype([(H5.MEAN_MEMBER, np.float64),
                        (H5.STANDARD_DEVIATION_MEMBER, np.float64),
                        (H5.NUMBER_OF_SAMPLES_MEMBER, np.int32),
                        (H5.SUM_MEMBER, np.float64),
                        (H5.SUM_OF_SQUARES_MEMBER, np.float64)])

# structure to store and perform online computation of basic descriptive indexes for a normally distributed variable
# Perform online computation by adding individual elements to the object as described by:
# Reference: @ARTICLE{Welford62noteon,
#                     author = {Author(s) B. P. Welford and B. P. Welford},
#                     title = {Note on a method for calculating corrected sums of squares and products},
#                     journal = {Technometrics},
#                     year = {1962},
#                     pages = {419--420}
#                    }
# TODO: Discuss algorithm variation on https://stackoverflow.com/questions/5543651/computing-standard-deviation-in-a-stream
class Normal:

    def __init__(self):
        self.mean_value = np.NaN # mean_value = ((count*mean_value)+ X )/(count+1)
        self.std_value = np.NaN # std_value = ( n-2 / n-1 ) std_value {n-1}+{1\over n}(X_n-\bar X_{n-1})**2.
        self.count = 0 # count = count + 1
        self.sum = 0.0 # to reduce the computational effort and rounding error on the average computation
        self.sum_squares = 0.0 # to reduce the computational effort and reduce error on the standard deviation computation

    # add element to the standard normal distribution
    def add_element(self, new_element):
        # local variable to help on the computation
        old_mean = 0.0
        delta = 0.0

        # select appropriate update procedure according to the number of elements.
        # for better efficiency, first consider an existing vector with 2 or more samples already registered
        if self.count > 1:
            old_mean = self.mean_value

            self.sum = self.sum + new_element

            self.count += 1
            self.mean_value = self.sum / self.count

            self.sum_squares = self.sum_squares + ((new_element-old_mean)*(new_element-self.mean_value))

            # self.std_value = m.sqrt(self.sum_squares / self.count) # To be used if one wants to keep std_value updated
        else:
            # if there are 0 (negative number of elements are considered 0), set the first element
            if self.count < 1:
                self.mean_value = new_element
                self.count = 1
                self.sum = new_element
            # else, if there is one element
            else:
                self.count = 2
                self.mean_value = (self.mean_value + new_element) / self.count
                self.sum = self.sum + new_element
                delta = new_element-self.mean_value
                self.sum_squares = delta*delta

    # to updated std.value if automatic update is not used
    def std_update(self) -> float:
        # std_value = ( n-2 / n-1 ) std_value {n-1}+{1\over n}(X_n-\bar X_{n-1})².
        if self.count > 1:
            self.std_value = m.sqrt(self.sum_squares / self.count)

        return self.std_value

    # add set to the standard normal distribution. Consider that the population described on each object is not
    # https://en.wikipedia.org/wiki/Pooled_variance#Population-based_statistics
    def add_set(self, new_set):
        # TODO: handle cases were one of the sets has one or two elements only
        if self.sum_squares == np.NaN:
            self.std_update()

        if new_set.sum_squares == np.NaN:
            new_set.std_update()

        old_set = self
        
        # TODO: handle case where

        self.count = old_set.count + new_set.count
        self.mean_value = (old_set.sum + new_set.sum) / self.count
        self.sum = old_set.sum + new_set.sum

        # TODO: handle cases to compute the sum_square, allowing to further add single elements to the object
        self.sum_squares = np.NaN

        self.std_value = m.sqrt(((((old_set.count*old_set.std_value**2) + (new_set.count*new_set.std_value**2))*self.count)+((old_set.count*new_set.count)*((old_set.mean_value-new_set.mean_value)**2)))/(self.count**2))

    def np_set(self, data):
        self.mean_value = data[H5.MEAN_MEMBER]
        self.std_value = data[H5.STANDARD_DEVIATION_MEMBER]
        self.count = data[H5.NUMBER_OF_SAMPLES_MEMBER]
        self.sum = data[H5.SUM_MEMBER]
        self.sum_squares = data[H5.SUM_OF_SQUARES_MEMBER]

    def print(self, reference):
        print(reference+"(\u03BC:{}, \u03C3:{}, #:{}, \u03A3:{}, SS:{})".format(self.mean_value, self.std_value, self.count, self.sum, self.sum_squares))

# program log function
def log_message (message):
    process_timestamp = datetime.now()
    print("{}: ".format(process_timestamp)+message)

# quick plot function for dataframe
def plot_dataframe(dataframe: pd.DataFrame, x_label = "Frequency[Hz]", y_label = ""):
    xy_array = dataframe.to_numpy(dtype='float32')
    x_axis = dataframe.columns.to_numpy(dtype='float64')
    y_axis = dataframe.index.to_numpy(dtype='float64')
    
    if y_axis[0] > 1000:
        y_label = "Time [sec]"
    else:
        if y_axis[len(y_axis)-1] < -80:
            y_label = "Level [dBm/m²]"
        else:
            y_label = "Level [dB\u03BCV/m]"

    plt.pcolormesh(x_axis, y_axis, xy_array)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()

# call pandas tables to visualize the dataframe. Will halt execution
class table_dataframe(Frame):

    def __init__(self, df_data: pd.DataFrame, parent=None):
        self.parent = parent
        Frame.__init__(self)
        self.main = self.master
        self.main.geometry('600x400+200+100')
        self.main.title('Table app')
        f = Frame(self.main)
        f.pack(fill=BOTH,expand=1)

        if not isinstance(df_data, pd.DataFrame):
            df_data_type = type(df_data)
            if isinstance(df_data, tuple):
                df_data = pd.DataFrame(df_data).T

        pt = Table(f,
                   dataframe=df_data,
                   showtoolbar=True,
                   showstatusbar=True)

        self.table = pt

        pt.show()
        self.mainloop()
        return