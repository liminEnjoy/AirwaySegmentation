#!/usr/bin/python

from CommonUtil.FunctionsUtil import *
import matplotlib.pyplot as plt
from collections import *
import numpy as np
import sys


def plot_annotations_thresholds(xdata, ydata, threshold_vals):

    # round thresholds
    threshold_labels = ['%.2f' % elem for elem in threshold_vals]
    xy_buffer = None
    for i, xy in enumerate(zip(xdata, ydata)):
        if xy != xy_buffer:
            plt.annotate(str(threshold_labels[i]), xy=xy, textcoords='data')
            xy_buffer = xy

def find_index_optimal_threshold_sensitTPspecifFP(xdata, ydata):

    # find the optimal value corresponding to the closest to the left-upper corner.
    index_optim_thres = -1,
    min_dist = 1.0e+06
    max_x = 3.5e+05
    for index_i, (x, y) in enumerate(zip(xdata, ydata)):
        dist = np.sqrt((x / max_x) ** 2 + (y - 1) ** 2)
        if dist < min_dist:
            index_optim_thres = index_i
            min_dist = dist
    # endfor

    return index_optim_thres

def find_index_optimal_threshold_dice_coeff(dice_data):

    return np.argmax(dice_data)



# if( len(sys.argv)<2 ):
#     print("ERROR. Please input the FROC values tests file(s) name(s)... EXIT")
#     sys.exit(0)
#
# num_data_files = len(sys.argv)-1

list_input_data_files = ['SavedPredictions/Predictions_size352x240x120_LossWBEC_SlideWindow/mean_ROCsensTPspecFP.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow/mean_ROCsensTPspecFP.txt',
                         'SavedPredictions/Predictions_size352x240x120_LossWBEC_SlideWindow_TransformImages/mean_ROCsensTPspecFP.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow_TransformImages/mean_ROCsensTPspecFP.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow_ElasticDeformImages/mean_ROCsensTPspecFP.txt']

num_input_data_files = len(list_input_data_files)

print("Plot FROC values from %s test files:..." %(num_input_data_files))
print(', '.join(map(lambda item: '\''+basename(item)+'\'', list_input_data_files)))


threshold_list    = []
sensitivity_list  = []
FPaverage_list    = []
completeness_list = []
volumeleakage_list= []
dice_coeff_list   = []

for (i, in_file) in enumerate(list_input_data_files):

    data_this = np.loadtxt(in_file, skiprows=1)

    #TRICK to draw corectly the plots
    data_this[ 0,1:] = [1.0, 1000000, 1.0, 1.0, 0.0]
    data_this[-1,1:] = [0.0, 0.0, 0.0, 0.0, 0.0]

    threshold_list    .append(data_this[:, 0])
    sensitivity_list  .append(data_this[:, 1])
    FPaverage_list    .append(data_this[:, 2])
    completeness_list .append(data_this[:, 3] * 100)
    volumeleakage_list.append(data_this[:, 4] * 100)
    dice_coeff_list.   append(data_this[:, 5])
#endfor



list_reference1_files = ['SavedPredictions/Predictions_size352x240x120_LossWBEC_SlideWindow/mean_results_leakage_test.txt',
                         'SavedPredictions/Predictions_size352x240x120_LossWBEC_SlideWindow_TransformImages/mean_results_leakage_test.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow/mean_results_leakage_test.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow_TransformImages/mean_results_leakage_test.txt',
                         'SavedPredictions/Predictions_size352x240x104_LossDice_SlideWindow_ElasticDeformImages/mean_results_leakage_test.txt']

list_reference2_files = ['/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_10_10_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_11_11_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_12_12_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_13_13_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_14_14_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_15_15_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_16_16_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_17_17_100_i64_I3_o64_O1/mean_results_leakage_test.txt',
                         '/home/antonio/Results/AirwaySegmen_LUVAR/SavedPredictions/Predictions_Adria/Predictions_Airways_18_18_100_i64_I3_o64_O1/mean_results_leakage_test.txt']


completeness_reference1_list = []
volumeleakage_reference1_list= []

for (i, in_file) in enumerate(list_reference1_files):

    data_this = np.loadtxt(in_file, skiprows=1, usecols=[1,2])

    completeness_reference1_list .append(data_this[0] * 100)
    volumeleakage_reference1_list.append(data_this[1] * 100)
#endfor

completeness_reference2_list = []
volumeleakage_reference2_list= []

for (i, in_file) in enumerate(list_reference2_files):

    data_this = np.loadtxt(in_file, skiprows=1, usecols=[1,2])

    completeness_reference2_list .append(data_this[0] * 100)
    volumeleakage_reference2_list.append(data_this[1] * 100)
#endfor




labels = ['model_1',
          'model_2',
          'model_3',
          'model_4',
          'model_5']

if num_input_data_files == 1:
    # plot ROC: sensitivity - specificity
    plt.plot(FPaverage_list[0], sensitivity_list[0], 'o-', color='b')

    # annotate thresholds
    if threshold_list[0] is not None:
        plot_annotations_thresholds(FPaverage_list[0], sensitivity_list[0], threshold_list[0])

    plt.xlim([0, 400000])
    plt.ylim([0, 1.0])
    plt.xlabel('FalsePositives Average')
    plt.ylabel('True Positive Rate')
    plt.title('FROC curve')
    plt.show()


    # plot ROC: completeness - volume leakage
    plt.plot(volumeleakage_list[0], completeness_list[0], 'o-', color='b')

    # annotate thresholds
    if threshold_list[0] is not None:
        plot_annotations_thresholds(volumeleakage_list[0], completeness_list[0], threshold_list[0])

    plt.xlim([0, 100])
    plt.ylim([0, 100])
    plt.xlabel('Volume Leakage (%)')
    plt.ylabel('Completeness (%)')
    plt.show()


    # plot Dice coefficient - threshold
    plt.plot(threshold_list[0], dice_coeff_list[0], 'o-', color='b')

    plt.xlabel('Threshold')
    plt.ylabel('Dice coefficient')
    plt.show()

else:

    cmap = plt.get_cmap('rainbow')
    colors = [ cmap(float(i)/(num_input_data_files-1)) for i in range(num_input_data_files) ]


    # plot ROC: sensitivity - specificity
    print("plot ROC: sensitivity - specificity...")
    for i in range(num_input_data_files):

        plt.plot(FPaverage_list[i], sensitivity_list[i], color=colors[i], label=labels[i])

        # find optimal threshold
        index_mark_value = find_index_optimal_threshold_dice_coeff(dice_coeff_list[i])
        # annotation threshold
        plt.scatter(FPaverage_list[i][index_mark_value], sensitivity_list[i][index_mark_value], marker='o', color=colors[i])

        print("file %s, optimal threshold: %s..." %(i, threshold_list[i][index_mark_value]))
    # endfor

    plt.xlim([0, 400000])
    plt.ylim([0, 1.0])
    plt.xlabel('False Positive Average')
    plt.ylabel('True Positive Rate')
    plt.title('FROC curve')
    plt.legend(loc='right')
    plt.show()


    # plot ROC: completeness - volume leakage
    print("plot ROC: completeness - volume leakage...")
    for i in range(num_input_data_files):
        plt.plot(volumeleakage_list[i], completeness_list[i], color=colors[i], label=labels[i])

        # # find optimal threshold
        # index_mark_value = find_index_optimal_threshold_sensitTPspecifFP(volumeleakage_list[i], completeness_list[i])
        # # annotation threshold
        # plt.scatter(volumeleakage_list[i][index_mark_value], completeness_list[i][index_mark_value], marker='o', color=colors[i])

        #print("file %s, optimal threshold: %s..." % (i, threshold_list[i][index_mark_value]))
    # endfor

    # # Include annotations of other results
    # if completeness_reference1_list:
    #     plt.scatter(volumeleakage_reference1_list, completeness_reference1_list, marker='^', color='b')

    if completeness_reference2_list:
        plt.scatter(volumeleakage_reference2_list, completeness_reference2_list, marker='x', color='b')

    plt.xlim([0, 100])
    plt.ylim([0, 100])
    plt.xlabel('Volume Leakage (%)')
    plt.ylabel('Completeness (%)')
    plt.legend(loc='right')
    plt.show()


    # plot Dice coefficient - threshold
    print("plot Dice...")
    for i in range(num_input_data_files):
        plt.plot(threshold_list[i], dice_coeff_list[i], color=colors[i], label=labels[i])

        # find optimal threshold
        index_mark_value = find_index_optimal_threshold_dice_coeff(dice_coeff_list[i])

        print("file %s, optimal threshold: %s..." % (i, threshold_list[i][index_mark_value]))
    #endfor

    plt.xlabel('Threshold')
    plt.ylabel('Dice coefficient')
    plt.show()