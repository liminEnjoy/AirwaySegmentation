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
from Preprocessing.OperationsImages import *
import argparse


def main(args):

    workDirsManager = WorkDirsManager(args.basedir)
    BaseDataPath    = workDirsManager.getNameBaseDataPath()
    TestingDataPath = workDirsManager.getNameExistPath(workDirsManager.getNameDataPath(args.typedata))
    ModelsPath      = workDirsManager.getNameExistPath(args.basedir, args.modelsdir)
    PredictDataPath = workDirsManager.getNameNewPath(args.basedir, args.predictionsdir)
    OriginImagesPath = workDirsManager.getNameExistPath(BaseDataPath, 'ProcImages')
    OriginMasksPath  = workDirsManager.getNameExistPath(BaseDataPath, 'ProcMasks')

    # Get the file list:
    nameImagesFiles = 'images*'+ getFileExtension(FORMATINOUTDATA)
    nameMasksFiles  = 'masks*' + getFileExtension(FORMATINOUTDATA)

    listImagesFiles = findFilesDir(TestingDataPath, nameImagesFiles)
    listMasksFiles  = findFilesDir(TestingDataPath, nameMasksFiles )

    # Get the file list:
    nameOriginImagesFiles = '*.dcm'
    nameOriginMasksFiles  = '*.dcm'

    listOriginImagesFiles = findFilesDir(OriginImagesPath, nameOriginImagesFiles)
    listOriginMasksFiles  = findFilesDir(OriginMasksPath,  nameOriginMasksFiles)

    tempNamePredictMasksFiles = 'predictMasks-%s_acc%0.2f.nii.gz'


    if (args.cropImages):
        namefile_dict = joinpathnames(BaseDataPath, "boundBoxesMasks.npy")
        dict_masks_boundingBoxes = readDictionary(namefile_dict)

    if (args.confineMasksToLungs):

        OriginAddMasksPath = workDirsManager.getNameExistPath(BaseDataPath, 'RawAddMasks')
        nameAddMasksFiles  = '*.dcm'
        listAddMasksFiles  = findFilesDir(OriginAddMasksPath, nameAddMasksFiles)


    print("-" * 30)
    print("Loading saved model...")
    print("-" * 30)

    # Loading Saved Model
    modelSavedPath = joinpathnames(ModelsPath, getSavedModelFileName(args.prediction_modelFile))

    train_model_funs = [DICTAVAILLOSSFUNS(args.lossfun)] + [DICTAVAILMETRICFUNS(imetrics, set_fun_name=True) for imetrics in args.listmetrics]
    custom_objects = dict(map(lambda fun: (fun.__name__, fun), train_model_funs))

    model = NeuralNetwork.getLoadSavedModel(modelSavedPath, custom_objects=custom_objects)

    predictAccuracyMetrics_before = args.predictAccuracyMetrics + ('_Masked' if args.confineMasksToLungs else '')

    computePredictAccuracy_before = DICTAVAILMETRICFUNS(predictAccuracyMetrics_before, use_in_Keras=False)

    computePredictAccuracy_after  = DICTAVAILMETRICFUNS(args.predictAccuracyMetrics,   use_in_Keras=False)


    print("-" * 30)
    print("Predicting model...")
    print("-" * 30)

    if (args.multiClassCase):
        num_classes_out = args.numClassesMasks + 1
    else:
        num_classes_out = 1


    for i, (imagesFile, masksFile) in enumerate(zip(listImagesFiles, listMasksFiles)):

        print('\'%s\'...' % (imagesFile))

        # Assign original imagea and masks files
        index_origin_images = getIndexOriginImagesFile(basename(imagesFile), beginString='images')

        origin_imagesFile = listOriginImagesFiles[index_origin_images]
        origin_masksFile  = listOriginMasksFiles [index_origin_images]

        print("assigned to original files: '%s' and '%s'..." %(basename(origin_imagesFile), basename(origin_masksFile)))


        # Loading Data
        print("Loading data...")

        if (args.slidingWindowImages or args.transformationImages):

            test_images_generator = getImagesDataGenerator3D(args.slidingWindowImages, args.prop_overlap_Z_X_Y, args.transformationImages, args.elasticDeformationImages)

            (test_xData, test_yData) = LoadDataManagerInBatches_DataGenerator(IMAGES_DIMS_Z_X_Y,
                                                                              test_images_generator,
                                                                              num_classes_out=num_classes_out).loadData_1File(imagesFile, masksFile, shuffle_images=False)
        else:
            (test_xData, test_yData) = LoadDataManagerInBatches(IMAGES_DIMS_Z_X_Y).loadData_1File(imagesFile, masksFile, shuffle_images=False)


        # EVALUATE MODEL
        print("Evaluate model...")
        predict_data = model.predict(test_xData, batch_size=1)


        # Reconstruct batch images to full 3D array
        predict_masks_array_shape = FileReader.getImageSize(masksFile)

        if (args.slidingWindowImages or args.transformationImages):

            images_reconstructor = getImagesReconstructor3D(args.slidingWindowImages, predict_masks_array_shape, args.prop_overlap_Z_X_Y) #args.transformationImages)
        else:
            images_reconstructor = SlicingReconstructorImages3D(IMAGES_DIMS_Z_X_Y, predict_masks_array_shape)

        predict_masks_array = images_reconstructor.compute(predict_data)


        # Reconstruct cropped image to original size
        if (args.cropImages):

            origin_masks_array_shape = FileReader.getImageSize(origin_masksFile)

            if (predict_masks_array.shape > origin_masks_array_shape):
                message = "size of predictions array: %s, cannot be larger than that of original masks: %s..." %(predict_masks_array.shape, origin_masks_array_shape)
                CatchErrorException(message)
            else:
                print("Predictions are cropped. Augment size of predictions array from %s to original size %s..."%(predict_masks_array.shape, origin_masks_array_shape))

            crop_boundingBox = dict_masks_boundingBoxes[filenamenoextension(origin_imagesFile)]

            new_predict_masks_array = np.zeros(origin_masks_array_shape)
            new_predict_masks_array[crop_boundingBox[0][0]:crop_boundingBox[0][1],
                                    crop_boundingBox[1][0]:crop_boundingBox[1][1],
                                    crop_boundingBox[2][0]:crop_boundingBox[2][1]] = predict_masks_array

            predict_masks_array = new_predict_masks_array
        else:
            if (predict_masks_array.shape != origin_masks_array_shape):
                message = "size of predictions array: %s, not equal to size of masks: %s..." %(predict_masks_array.shape, origin_masks_array_shape)
                CatchErrorException(message)


        if (args.confineMasksToLungs):
            print("Confine masks to exclude the area outside the lungs...")

            exclude_masksFile   = listAddMasksFiles[index_origin_images]
            exclude_masks_array = FileReader.getImageArray(exclude_masksFile)

            predict_masks_array = ExclusionMasks.computeInverse(predict_masks_array, exclude_masks_array)


        # Compute test accuracy
        accuracy_before = computePredictAccuracy_before(test_yData.astype(FORMATPREDICTDATA), predict_data)

        accuracy_after  = computePredictAccuracy_after (origin_masks_array, predict_masks_array)

        print("Computed accuracy (before post-processing): %s..." %(accuracy_before))
        print("Computed accuracy (after post-processing): %s..." %(accuracy_after))


        # Save reconstructed prediction maps (or thresholding masks)
        print("Saving prediction masks, with dims: %s..." %(tuple2str(predict_masks_array.shape)))

        out_predictMasksFilename = joinpathnames(PredictDataPath, tempNamePredictMasksFiles%(filenamenoextension(origin_imagesFile), accuracy_after))

        FileReader.writeImageArray(out_predictMasksFilename, predict_masks_array)


        # Save predictions in images
        if (args.savePredictionImages):
            SaveImagesPath = workDirsManager.getNameNewPath(PredictDataPath, 'imagesSlices-%s'%(filenamenoextension(origin_imagesFile)))

            origin_images_array = FileReader.getImageArray(origin_imagesFile)
            origin_masks_array  = FileReader.getImageArray(origin_masksFile)

            #take only slices in the middle of lungs (1/5 - 4/5)*depth_Z
            begin_slices = origin_images_array.shape[0] // 5
            end_slices   = 4 * origin_images_array.shape[0] // 5

            PlotsManager.plot_compare_images_masks_allSlices(origin_images_array[begin_slices:end_slices],
                                                             origin_masks_array [begin_slices:end_slices],
                                                             predict_masks_array[begin_slices:end_slices],
                                                             isSaveImages=True, outfilespath=SaveImagesPath)
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
    parser.add_argument('--listPostprocessMetrics', type=parseListarg, default=LISTPOSTPROCESSMETRICS)
    parser.add_argument('--multiClassCase', type=str2bool, default=MULTICLASSCASE)
    parser.add_argument('--numClassesMasks', type=int, default=NUMCLASSESMASKS)
    parser.add_argument('--cropImages', type=str2bool, default=CROPIMAGES)
    parser.add_argument('--confineMasksToLungs', default=CONFINEMASKSTOLUNGS)
    parser.add_argument('--slidingWindowImages', type=str2bool, default=SLIDINGWINDOWIMAGES)
    parser.add_argument('--prop_overlap_Z_X_Y', type=str2tuplefloat, default=PROP_OVERLAP_Z_X_Y)
    parser.add_argument('--transformationImages', type=str2bool, default=False)
    parser.add_argument('--elasticDeformationImages', type=str2bool, default=False)
    parser.add_argument('--savePredictMaskSlices', default=SAVEPREDICTMASKSLICES)
    args = parser.parse_args()

    if (args.confineMasksToLungs):
        args.lossfun     = args.lossfun + '_Masked'
        args.listmetrics = [item + '_Masked' for item in args.listmetrics]

    print("Print input arguments...")
    for key, value in vars(args).iteritems():
        print("\'%s\' = %s" %(key, value))

    main(args)