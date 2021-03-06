import os
import csv
import pandas as pd


def _check_log_directory(directory):
    """
    Check that the log directory exists and create it if it doesn't
    """
    try:
        if not os.path.exists(directory):
            print("Attempting to make log directory at " + directory)
            os.makedirs(directory)
    except IOError as e:
        sys.exit("Error attempting to create log directory: {0}".format(e.strerror).strip())


def _initialise_model_log(log_filepath):
    """Create a model logging file if it doesn't already exist"""
    if not os.path.exists(log_filepath):
        with open(log_filepath, 'a') as fp:
            a = csv.writer(fp, delimiter=',')
            data = [['DATETIME', 'Model', 'Accuracy', 'Feature function', 'Normalization',
            'Feature function config', 'Feature function training time', 
            'Model config', 'Model training time']]
            a.writerows(data)


def _read_model_log(log_dir, directories, filename):
    results = []
    for directory in directories:
        directory_path = os.path.join(log_dir,directory,filename)
        results.append(pd.read_csv(directory_path, sep=','))
    overall_results = pd.concat(results)
    return overall_results
