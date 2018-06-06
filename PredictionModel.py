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
from CommonUtil.FileReaders import *
from CommonUtil.FunctionsUtil import *
from CommonUtil.ImageGeneratorManager import *
from CommonUtil.ImageReconstructorManager import *
from CommonUtil.LoadDataManager import *
from CommonUtil.PlotsManager import *
from CommonUtil.WorkDirsManager import *
from Networks.Metrics import *
from Networks.Networks import *
import argparse


def main(args):

    workDirsManager = WorkDirsManager(args.basedir)
    TestingDataPath = workDirsManager.getNameExistPath(workDirsManager.getNameDataPath(args.typedata))
    ModelsPath      = workDirsManager.getNameExistPath(args.basedir, args.modelsdir)
    PredictDataPath = workDirsManager.getNameNewPath(args.basedir, args.predictionsdir)

    # Get the file list:
    nameImagesFiles = 'images*'+ getFileExtension(FORMATINOUTDATA)
    nameMasksFiles  = 'masks*' + getFileExtension(FORMATINOUTDATA)

    listImagesFiles = findFilesDir(TestingDataPath, nameImagesFiles)
    listMasksFiles  = findFilesDir(TestingDataPath, nameMasksFiles )

    tempNamePredictionsFiles = 'predict-%s_acc%0.2f'

    outFilesExtension = getFileExtension(FORMATINOUTDATA)


    print("-" * 30)
    print("Loading saved model...")
    print("-" * 30)

    # Loading Saved Model
    modelSavedPath = joinpathnames(ModelsPath, getSavedModelFileName(args.prediction_modelFile))

    train_model_funs = [DICTAVAILLOSSFUNS(args.lossfun)] + [DICTAVAILMETRICFUNS(imetrics, set_fun_name=True) for imetrics in args.listmetrics]
    custom_objects = dict(map(lambda fun: (fun.__name__, fun), train_model_funs))

    model = NeuralNetwork.getLoadSavedModel(modelSavedPath, custom_objects=custom_objects)

    computePredictAccuracy = DICTAVAILMETRICFUNS(PREDICTACCURACYMETRICS, use_in_Keras=False)


    print("-" * 30)
    print("Predicting model...")
    print("-" * 30)

    if (args.multiClassCase):
        num_classes_out = args.numClassesMasks + 1
    else:
        num_classes_out = 1


    for i, (imagesFile, masksFile) in enumerate(zip(listImagesFiles, listMasksFiles)):

        print('\'%s\'...' % (imagesFile))

        # Loading Data
        if (args.slidingWindowImages or args.transformationImages):

            test_images_generator = getImagesDataGenerator3D(args.slidingWindowImages, args.prop_overlap_Z_X_Y, args.transformationImages, args.elasticDeformationImages)

            (test_xData, test_yData) = LoadDataManagerInBatches_DataGenerator(IMAGES_DIMS_Z_X_Y,
                                                                              test_images_generator,
                                                                              num_classes_out=num_classes_out).loadData_1File(imagesFile, masksFile, shuffle_images=False)
        else:
            (test_xData, test_yData) = LoadDataManagerInBatches(IMAGES_DIMS_Z_X_Y).loadData_1File(imagesFile, masksFile, shuffle_images=False)


        # Evaluate Model
        predict_data = model.predict(test_xData, batch_size=1)

        # Compute test accuracy
        accuracy = computePredictAccuracy(test_yData.astype(FORMATPREDICTDATA), predict_data)

        print("Computed accuracy: %s..."%(accuracy))


        # Reconstruct batch images to full 3D array
        predict_masks_array_shape = FileReader.getImageSize(masksFile)

        if (args.slidingWindowImages or args.transformationImages):

            images_reconstructor = getImagesReconstructor3D(args.slidingWindowImages, predict_masks_array_shape, args.prop_overlap_Z_X_Y) #args.transformationImages)
        else:
            images_reconstructor = SlicingReconstructorImages3D(IMAGES_DIMS_Z_X_Y, predict_masks_array_shape)

        predict_masks_array = images_reconstructor.compute(predict_data)


        # Save predictions data
        print("Saving predictions data, with dims: %s..." %(tuple2str(predict_masks_array.shape)))

        out_predictionsFilename = joinpathnames(PredictDataPath, tempNamePredictionsFiles%(filenamenoextension(masksFile), accuracy) + outFilesExtension)

        FileReader.writeImageArray(out_predictionsFilename, predict_masks_array)


        if (args.saveVisualPredictData):
            print("Saving predictions data in image format for visualization...")

            out_predictionsFilename = joinpathnames(PredictDataPath, tempNamePredictionsFiles%(filenamenoextension(masksFile), accuracy) + '.nii')

            FileReader.writeImageArray(out_predictionsFilename, predict_masks_array)
    #endfor


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--basedir', default=BASEDIR)
    parser.add_argument('--typedata', default=TYPEDATA)
    parser.add_argument('--modelsdir', default='Models')
    parser.add_argument('--predictionsdir', default='Predictions')
    parser.add_argument('--lossfun', default=ILOSSFUN)
    parser.add_argument('--listmetrics', type=parseListarg, default=LISTMETRICS)
    parser.add_argument('--prediction_modelFile', default=PREDICTION_MODELFILE)
    parser.add_argument('--predictAccuracyMetrics', default=PREDICTACCURACYMETRICS)
    parser.add_argument('--multiClassCase', type=str2bool, default=MULTICLASSCASE)
    parser.add_argument('--numClassesMasks', type=int, default=NUMCLASSESMASKS)
    parser.add_argument('--confineMasksToLungs', default=CONFINEMASKSTOLUNGS)
    parser.add_argument('--slidingWindowImages', type=str2bool, default=SLIDINGWINDOWIMAGES)
    parser.add_argument('--prop_overlap_Z_X_Y', type=str2tuplefloat, default=PROP_OVERLAP_Z_X_Y)
    parser.add_argument('--transformationImages', type=str2bool, default=False)
    parser.add_argument('--elasticDeformationImages', type=str2bool, default=False)
    parser.add_argument('--saveVisualPredictData', type=str2bool, default=SAVEVISUALPREDICTDATA)
    args = parser.parse_args()

    if (args.confineMasksToLungs):
        args.lossfun     = args.lossfun + '_Masked'
        args.listmetrics = [item + '_Masked' for item in args.listmetrics]
        args.predictAccuracyMetrics = args.predictAccuracyMetrics + '_Masked'

    print("Print input arguments...")
    for key, value in vars(args).iteritems():
        print("\'%s\' = %s" %(key, value))

    main(args)