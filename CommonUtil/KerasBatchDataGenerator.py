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
from CommonUtil.LoadDataManager import OperationsArraysUseInKeras
from keras.preprocessing import image
import numpy as np
np.random.seed(2017)


class KerasTrainingBatchDataGenerator(image.Iterator):

    def __init__(self, size_image, list_xData_array, list_yData_array, images_generator, num_classes_out=1, size_outnnet=None, batch_size=1, shuffle=True, seed=None):

        self.size_image       = size_image
        self.list_xData_array = list_xData_array
        self.list_yData_array = list_yData_array
        self.images_generator = images_generator

        self.opersArrays = OperationsArraysUseInKeras(size_image, num_classes_out=num_classes_out, size_outnnet=size_outnnet)

        self.num_channels_in = self.opersArrays.get_num_channels_array(self.list_xData_array[0].shape)

        self.num_classes_out = num_classes_out
        if size_outnnet and (size_outnnet != size_image):
            self.size_outnnet = size_outnnet
        else:
            self.size_outnnet = size_image

        self.compute_pairIndexes_samples(shuffle, seed)

        numtot_samples = len(self.list_pairIndexes_samples)

        super(KerasTrainingBatchDataGenerator, self).__init__(numtot_samples, batch_size, shuffle, seed)


    def compute_pairIndexes_samples(self, shuffle, seed=None):

        self.list_pairIndexes_samples = []
        for ifile, xData_array in enumerate(self.list_xData_array):

            self.images_generator.complete_init_data(xData_array.shape[0:3])

            num_samples_file = self.images_generator.get_num_images()

            #store pair of indexes: (idx_file, idx_batch)
            for index in range(num_samples_file):
                self.list_pairIndexes_samples.append((ifile, index))
            #endfor
        #endfor

        numtot_samples = len(self.list_pairIndexes_samples)

        if (shuffle):
            if seed:
                np.random.seed(seed)
            randomIndexes = np.random.choice(numtot_samples, size=numtot_samples, replace=False)

            self.list_pairIndexes_samples_old = self.list_pairIndexes_samples
            self.list_pairIndexes_samples = []
            for index in randomIndexes:
                self.list_pairIndexes_samples.append(self.list_pairIndexes_samples_old[index])
            #endfor


    def _get_batches_of_transformed_samples(self, indexes_batch):

        num_samples_batch     = len(indexes_batch)
        out_xData_array_shape = self.opersArrays.get_shape_out_array(num_samples_batch, num_channels=self.num_channels_in)
        out_yData_array_shape = self.opersArrays.get_shape_out_array(num_samples_batch, num_channels=self.num_classes_out)

        out_xData_array = np.ndarray(out_xData_array_shape, dtype=self.list_xData_array[0].dtype)
        out_yData_array = np.ndarray(out_yData_array_shape, dtype=self.list_yData_array[0].dtype)

        for i, index in enumerate(indexes_batch):
            (index_file, index_sample_file) = self.list_pairIndexes_samples[index]

            self.images_generator.complete_init_data(self.list_xData_array[index_file].shape[0:3])

            xData_elem = self.images_generator.get_image_array(self.list_xData_array[index_file], index_sample_file, seed=index)
            yData_elem = self.images_generator.get_image_array(self.list_yData_array[index_file], index_sample_file, seed=index)

            out_xData_array[i] = self.opersArrays.get_array_reshaped_Keras(self.opersArrays.get_array_reshaped(xData_elem))

            if self.num_classes_out > 1:
                out_yData_array[i] = self.opersArrays.get_array_reshaped_Keras(self.opersArrays.get_array_categorical_masks(self.opersArrays.get_array_cropImages_outNnet(yData_elem)))
            else:
                out_yData_array[i] = self.opersArrays.get_array_reshaped_Keras(self.opersArrays.get_array_reshaped(self.opersArrays.get_array_cropImages_outNnet(yData_elem)))
        #endfor

        return (out_xData_array, out_yData_array)