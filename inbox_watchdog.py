#!/usr/bin/python3

# This code runs on two parallel process that may spawn several others.
# First process uses inotify to monitor a folder for access on files. 
# Once a file of the designated extension is accessed, its name is stored on the list for processing. ( queue )
# Each new access on the file, e.g. appending a new block to it, the access time on the list is updated
# Also, on the event of file access, the second watchdog is spawned
# The second watchdog process monitor the list for items that don't have any access for a period of time, allowing a slow transfer to complete,
# The second watchdog process monitor perform the following actions:
#   1. Move the file to a working folder if it is not accessed for a period of time.
#   2. Execute a call for an external program with several paramenters, including the file name and variants for output names
#   3. Monitor the external program execution, many parallel threads can be monitored, as many as there are files to process
#   4. Move files to archive or error folders after execution, according to the result.
#   5. Stop the second watchdog timer if there is no files on the queue or process to monitor

# TODO: Capture and process the text output from the program into a log file.
# TODO: Organize activity log in JSON format

import os
import subprocess
from datetime import datetime
from datetime import timedelta
from threading import Timer

import inotify.adapters

# constants that control the script
# TODO: Change to load from the control database or configuration file. Maybe use this second option and add event trigger to reload configuration on changes
FOLDER_TO_WATCH = "/home/lobao/TFM_Code/InBox"
FOLDER_TO_WORK = "/home/lobao/TFM_Code/DoBox"
FOLDER_TO_PLACE_RESULTS = "/home/lobao/TFM_Code/OutBox"
FOLDER_TO_ARCHIVE = "/home/lobao/TFM_Code/DoneBox"
FOLDER_TO_STORE_FAILED = "/home/lobao/TFM_Code/ErrorBox"
FILE_EXTENSION_TO_WATCH = ".bin"
DESTINATION_FILE_EXTENSION = ".h5"
COMMAND_TO_PERFORM = ["/home/lobao/TFM_Code/decode", "-d", "1", "-u", "1"]
INPUT_FILENAME_COMMAND_OPTION = ["-f"]
OUTPUT_FILENAME_COMMAND_OPTION = ["-o"]
TIME_TO_FINISH_FILE_TRANSFER = timedelta(seconds=60)
QUEUE_CHECK_PERIOD = 10

# class used for multithreading the file processing with delay to accommodate slow transfer of large files
class WatchDog(object):
    # initialization method to the WatchDog
    def __init__(self, interval):
        self._timer     = None
        self.interval   = interval
        self.is_running = False
        self.file_queue = dict()
        self.decode_running_process = dict()

    # method that is run each periodic interval
    def _run(self):
        self.is_running = False
        self.start()
        self.run_decode()

    # method that perform the action
    def run_decode(self):
        call_timestamp = datetime.now()
        queue_size = self.file_queue.__len__()
        number_of_running_process = self.decode_running_process.__len__()
        log_output = True

        # if there is no process to monitor or file to process, stop watchdog timer
        if number_of_running_process == 0 and queue_size == 0:
            self.stop()
        # else, if there is something to monitor
        else:
            # if there are files to process
            if queue_size > 0:
                # for each file on the queue list
                for file_name in list(self.file_queue):
                    # if enough time has passed since the last file access
                    if call_timestamp > self.file_queue[file_name]+TIME_TO_FINISH_FILE_TRANSFER:
                        # TODO: Include error handling for all file operations
                        # move file to a work directory. This avoid retrigggering the inotify
                        source_file = FOLDER_TO_WATCH+"/"+file_name
                        work_file = FOLDER_TO_WORK+"/"+file_name
                        os.rename(source_file, work_file)

                        # create a filename for the output identical to the input
                        file_extension_length = -FILE_EXTENSION_TO_WATCH.__len__()
                        output_file = FOLDER_TO_PLACE_RESULTS + "/" + file_name[:file_extension_length]+DESTINATION_FILE_EXTENSION

                        # Create the command list and execute
                        bash_comand = COMMAND_TO_PERFORM+INPUT_FILENAME_COMMAND_OPTION
                        bash_comand.append(work_file)
                        bash_comand = bash_comand + OUTPUT_FILENAME_COMMAND_OPTION
                        bash_comand.append(output_file)
                        self.decode_running_process[file_name] = subprocess.Popen(bash_comand)

                        # increment the counter for the number of running process
                        number_of_running_process += 1

                        # convert the comand to string and output the message to log
                        bash_text = " ".join(bash_comand)
                        print("{}: $".format(call_timestamp)+bash_text)

                        # delete the filename from the queue and reset the queue_size variable
                        del self.file_queue[file_name]
                        queue_size = self.file_queue.__len__()

                        # reset timer to be used for the next file on the queue
                        call_timestamp = datetime.now()
                    # else, if not enough time has passed since last file access
                    else:
                        # Select the appropriate message output according to the queue size
                        if queue_size == 1:
                            print("{}: Waiting. {} file on the queue".format(call_timestamp, queue_size))
                        else:
                            # for large queues, output only one message.
                            if log_output:
                                print("{}: Waiting. {} files on the queue".format(call_timestamp, queue_size))
                                log_output = False
            # if there are no files on the queue, output the corresponding message
            else:
                print("{}: No file on the queue".format(call_timestamp))

            # if there are process running
            if number_of_running_process > 0:
                # for each process, associated to a file
                for file_name in list(self.decode_running_process):
                    # if the process has finished
                    if self.decode_running_process[file_name].poll() is not None:
                        # get the return code from the process
                        program_returncode = self.decode_running_process[file_name].returncode

                        # If the process finished with success
                        if program_returncode == 0:
                            # move file from the work folder to archive
                            work_file = FOLDER_TO_WORK+"/"+file_name
                            archive_file = FOLDER_TO_ARCHIVE+"/"+file_name
                            os.rename(work_file, archive_file)
                        # If the process failed
                        else:
                            # move the file from the work folder to the error folder for later debug
                            call_timestamp = datetime.now()
                            work_file = FOLDER_TO_WORK+"/"+file_name
                            failed_file = FOLDER_TO_STORE_FAILED+"/"+file_name
                            os.rename(work_file, failed_file)

                            #print the corresponding error message
                            print("{}: Process exited code: {}".format(call_timestamp, program_returncode))

                        # remove the corresponding process from the monitoring list
                        del self.decode_running_process[file_name]

                # update the number of running process
                number_of_running_process = self.decode_running_process.__len__()

                # Output the message according to the number of process being monitored
                call_timestamp = datetime.now()
                if number_of_running_process == 0:
                    print("{}: No running process".format(call_timestamp))
                else:
                    print("{}: Running {} process".format(call_timestamp, number_of_running_process))
            # else, if there are no process being monitored
            else:
                # output log message
                print("{}: No running process".format(call_timestamp))

    # method that start the timer
    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    # method that stop the timer
    def stop(self):
        self._timer.cancel()
        self.is_running = False

def _main():
    print("{}: Initializing watch for files with ""{}"" extension on {} folder".format(datetime.now(), FILE_EXTENSION_TO_WATCH, FOLDER_TO_WATCH))

    #store the file extention length for later substring extraction from the filename
    file_extension_length = -FILE_EXTENSION_TO_WATCH.__len__()

    # create notification object to monitor the folder
    i = inotify.adapters.Inotify()

    # create a process to watch the folder and generate events when the folder is changed. Using Linux Inotify
    i.add_watch(FOLDER_TO_WATCH)

    # create a timer to keep a list of files and act on than after a delay
    watchdog_timer = WatchDog(QUEUE_CHECK_PERIOD)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        # look for the event 'IN_MODIFY', associated with the file write operation
        #print("type_names: {}, path: {}, filename: {}".format(type_names, path, filename))
        if 'IN_MODIFY' in type_names:
            # check if the file has the .bin extension
            path_plus_filename = path+"/"+filename
            if filename[file_extension_length:] == FILE_EXTENSION_TO_WATCH:
                # get the file access timestamp as the last activity reference
                file_access_timestamp = datetime.fromtimestamp(os.path.getatime(path_plus_filename))

                # set the file on the watchdog timer queue or reset the reference time if the file was already placed on the queue
                watchdog_timer.file_queue[filename] = file_access_timestamp

                # start the timer. Call actually do something only if the timer is nor already started
                watchdog_timer.start()
            else:
                print("{}: Ignored event: IN_MODIFY on file {}.".format(datetime.now(), path_plus_filename))

if __name__ == '__main__':
    _main()
