#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

import numpy as np


DATADIR = '/home/antonio/testSegmentation/Data/LUVAR/'
BASEDIR = '/home/antonio/testSegmentation/Tests_LUVAR/'


# ******************** DATA DISTRIBUTION ********************
PROP_TRAINING   = 0.5
PROP_VALIDATION = 0.25
PROP_TESTING    = 0.25
DISTRIBUTE_RANDOM = False
# ******************** DATA DISTRIBUTION ********************


# ******************** INPUT IMAGES PARAMETERS ********************
# MUST BE MULTIPLES OF 16
IMAGES_DEPTHZ = 16
IMAGES_HEIGHT = 352
#IMAGES_HEIGHT = 256
IMAGES_WIDTH  = 240
#IMAGES_WIDTH  = 256

IMAGES_DIMS_X_Y   = (IMAGES_HEIGHT, IMAGES_WIDTH)
IMAGES_DIMS_Z_X_Y = (IMAGES_DEPTHZ, IMAGES_HEIGHT, IMAGES_WIDTH)

TYPEDATA = 'validation'

FORMATIMAGEDATA = np.int16
FORMATMASKDATA  = np.int8
# ******************** INPUT IMAGES PARAMETERS ********************


# ******************** PRE-PROCESSING PARAMETERS ********************
SHUFFLEIMAGES = True

CONFINEMASKSTOLUNGS = False

CROPPINGIMAGES = True

CHECKBALANCECLASSES = True

if (CROPPINGIMAGES):
    CROPSIZEBOUNDINGBOX = (352, 480)

SLIDINGWINDOWIMAGES = True

SAVEIMAGESFILESINBATCHES = True

if (SLIDINGWINDOWIMAGES):
    PROP_OVERLAP_Z_X_Y = (0.5, 0.0, 0.0)
# ******************** PRE-PROCESSING PARAMETERS ********************


# ******************** TRAINING PARAMETERS ********************
NBEPOCHS   = 1000
BATCH_SIZE = 1
IMODEL     = 'Unet3D'
IOPTIMIZER = 'Adam'
LEARN_RATE = 1.0e-05

USE_DATAAUGMENTATION = True

USE_RESTARTMODEL = False
# ******************** TRAINING PARAMETERS ********************


# ******************** POST-PROCESSING PARAMETERS ********************
RECONSTRUCTPREDICTION = True

THRESHOLDOUTIMAGES = True

if (THRESHOLDOUTIMAGES):
    THRESHOLDVALUE = 0.5
# ******************** POST-PROCESSING PARAMETERS ********************
