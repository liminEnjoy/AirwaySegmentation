#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

from CommonUtil.Constants import *
from CommonUtil.ErrorMessages import *
from CommonUtil.FileReaders import *
from CommonUtil.FrocUtil import computeFROC, plotFROC
from CommonUtil.FunctionsUtil import *
from CommonUtil.PlotsManager import *
from CommonUtil.WorkDirsManager import *
from Preprocessing.OperationsImages import *
import argparse
np.random.seed(2017)


def main(args):

    workDirsManager  = WorkDirsManager(args.basedir)
    BaseDataPath     = workDirsManager.getNameBaseDataPath()
    PredictMasksPath = workDirsManager.getNameExistPath(args.basedir, args.predictionsdir)
    OriginMasksPath  = workDirsManager.getNameExistPath(BaseDataPath, 'RawMasks')

    # Get the file list:
    namePredictMasksFiles = '*.nii'
    nameOriginMasksFiles  = '*.dcm'

    listPredictMasksFiles= findFilesDir(PredictMasksPath, namePredictMasksFiles)
    listOrigMasksFiles   = findFilesDir(OriginMasksPath,  nameOriginMasksFiles)

    print listPredictMasksFiles
    print listOrigMasksFiles
    exit

    nbPredictMasksFiles = len(listPredictMasksFiles)

    # create file to save FROC values
    tempFROCvaluesFilename = '%s-FROCvalues.txt'


    # Run checkers
    if (nbPredictMasksFiles == 0):
        message = "num Predictions found in dir \'%s\'" %(PredictMasksPath)
        CatchErrorException(message)

    if (args.confineMasksToLungs):

        OriginAddMasksPath = workDirsManager.getNameExistPath(BaseDataPath, 'RawAddMasks')

        nameAddMasksFiles = '*.dcm'
        listAddMasksFiles = findFilesDir(OriginAddMasksPath, nameAddMasksFiles)


    # parameters
    nbr_of_thresholds = 11
    range_threshold = [0.0, 1.0]
    thresholds_list = (np.linspace(range_threshold[0], range_threshold[1], nbr_of_thresholds)).tolist()
    #thresholds_list = (np.logspace(range_threshold[0], range_threshold[1], nbr_of_thresholds)).tolist()
    allowedDistance = 0


    threshold_listcases   = np.zeros((nbr_of_thresholds, nbPredictMasksFiles))
    sensitivity_listcases = np.zeros((nbr_of_thresholds, nbPredictMasksFiles))
    FPaverage_listcases   = np.zeros((nbr_of_thresholds, nbPredictMasksFiles))


    for i, predictionsFile in enumerate(listPredictMasksFiles):

        print('\'%s\'...' %(predictionsFile))

        predict_masks_array = FileReader.getImageArray(predictionsFile)

        print("Predictions masks array of size: %s..." % (str(predict_masks_array.shape)))


        index_origin_masks = re.search('av[0-9]*', predictionsFile).group(0)

        origin_masksFile = ''
        for file in listOrigMasksFiles:
            if index_origin_masks in file:
                origin_masksFile = file
                break

        print("assigned to '%s'..." % (basename(origin_masksFile)))

        origin_masks_array  = FileReader.getImageArray(origin_masksFile)

        # Turn to binary masks (0, 1)
        origin_masks_array = processBinaryMasks(origin_masks_array)

        if (args.confineMasksToLungs):
            print("Confine masks to exclude the area outside the lungs...")

            index_origin_masks = int(index_origin_masks.replace('av',''))

            exclude_masksFile   = listAddMasksFiles[index_origin_masks]
            exclude_masks_array = FileReader.getImageArray(exclude_masksFile)

            origin_masks_array = ExclusionMasks.compute(origin_masks_array, exclude_masks_array)


        # need to convert to lists for FROC methods
        predict_masks_array = np.expand_dims(predict_masks_array, axis=0)
        origin_masks_array  = np.expand_dims(origin_masks_array,  axis=0)

        # compute FROC
        print("computing FROC...")
        print("for list of threshold values: %s" %(thresholds_list))
        sensitivity_list, FPaverage_list = computeFROC(predict_masks_array, origin_masks_array, allowedDistance, thresholds_list)
        print("...done")


        out_FROCvaluesFilename = joinpathnames(PredictMasksPath, tempFROCvaluesFilename %(filenamenoextension(origin_masksFile)))
        fout = open(out_FROCvaluesFilename, 'w')

        strheader = '/threshold/ /sensitivity/ /FPaverage/' +'\n'
        fout.write(strheader)

        for threshold, sensitivity, FPaverage in zip(thresholds_list, sensitivity_list, FPaverage_list):
            strdata = str(threshold) + ' ' + str(sensitivity) + ' ' + str(FPaverage) +'\n'
            fout.write(strdata)
        #endfor

        fout.close()

        #store to compute average values over all cases
        threshold_listcases  [:,i] = thresholds_list
        sensitivity_listcases[:,i] = sensitivity_list
        FPaverage_listcases  [:,i] = FPaverage_list


        # plot FROC
        print("plotting FROC...")
        plotFROC(FPaverage_list, sensitivity_list)
    #endfor


    thresholds_list  = np.mean(threshold_listcases,   axis=1)
    sensitivity_list = np.mean(sensitivity_listcases, axis=1)
    FPaverage_list   = np.mean(FPaverage_listcases,   axis=1)

    out_FROCvaluesFilename = joinpathnames(PredictMasksPath, tempFROCvaluesFilename %('mean'))
    fout = open(out_FROCvaluesFilename, 'w')

    strheader = '/threshold/ /sensitivity/ /FPaverage/' + '\n'
    fout.write(strheader)

    for threshold, sensitivity, FPaverage in zip(thresholds_list, sensitivity_list, FPaverage_list):
        strdata = str(threshold) + ' ' + str(sensitivity) + ' ' + str(FPaverage) + '\n'
        fout.write(strdata)
    # endfor

    fout.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--basedir', default=BASEDIR)
    parser.add_argument('--predictionsdir', default='Predictions')
    parser.add_argument('--confineMasksToLungs', default=CONFINEMASKSTOLUNGS)
    args = parser.parse_args()

    print("Print input arguments...")
    for key, value in vars(args).iteritems():
        print("\'%s\' = %s" %(key, value))

    main(args)