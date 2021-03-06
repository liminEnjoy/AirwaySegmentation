#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

from Common.ErrorMessages import *
from Common.FunctionsUtil import *
import numpy as np


class OperationMasks(object):
    val_mask_background = 0
    val_mask_exclude_voxels = -1

    @staticmethod
    def is_images_array_without_channels(images_array_shape, masks_exclude_voxels_array_shape):
        return len(images_array_shape) == len(masks_exclude_voxels_array_shape)

    @classmethod
    def check_correct_shape_input_array(cls, images_array_shape, masks_exclude_voxels_array_shape):
        if cls.is_images_array_without_channels(images_array_shape, masks_exclude_voxels_array_shape):
            if (images_array_shape == masks_exclude_voxels_array_shape):
                return True
        else:
            if (images_array_shape[0:-1] == masks_exclude_voxels_array_shape):
                return True
        message = "size of input array, %s; not equal to size of mask, %s..." %(images_array_shape, masks_exclude_voxels_array_shape)
        CatchErrorException(message)


    @classmethod
    def template_apply_mask_to_image_with_channels_2args(cls, function_apply_mask_without_channels,
                                                         images_array, masks_exclude_voxels_array):
        num_channels = images_array.shape[-1]
        for ichan in range(num_channels):
            images_array[..., ichan] = function_apply_mask_without_channels(images_array[..., ichan], masks_exclude_voxels_array)
        #endfor
        #return images_array

    @classmethod
    def template_apply_mask_to_image_with_channels_3args(cls, function_apply_mask_without_channels,
                                                         images_array, original_images_array, masks_exclude_voxels_array):
        num_channels = images_array.shape[-1]
        for ichan in range(num_channels):
            images_array[..., ichan] = function_apply_mask_without_channels(images_array[..., ichan], original_images_array, masks_exclude_voxels_array)
        # endfor
        #return images_array


    @classmethod
    def function_apply_mask_exclude_voxels(cls, images_array, masks_exclude_voxels_array):
        return np.where(masks_exclude_voxels_array == cls.val_mask_background, cls.val_mask_exclude_voxels, images_array)

    @classmethod
    def function_apply_mask_exclude_voxels_fillzero(cls, images_array, masks_exclude_voxels_array):
        return np.where(masks_exclude_voxels_array == cls.val_mask_background, cls.val_mask_background, images_array)

    @classmethod
    def function_reverse_mask_exclude_voxels(cls, images_array, original_images_array, masks_exclude_voxels_array):
        return np.where(masks_exclude_voxels_array == cls.val_mask_background, original_images_array, images_array)

    @classmethod
    def function_reverse_mask_exclude_voxels_fillzero(cls, images_array, masks_exclude_voxels_array):
        return np.where(masks_exclude_voxels_array == cls.val_mask_background, cls.val_mask_background, images_array)


    @classmethod
    def apply_mask_exclude_voxels(cls, images_array, masks_exclude_voxels_array):

        if cls.check_correct_shape_input_array(images_array.shape, masks_exclude_voxels_array.shape):
            if cls.is_images_array_without_channels(images_array.shape, masks_exclude_voxels_array.shape):
                return cls.function_apply_mask_exclude_voxels(images_array, masks_exclude_voxels_array)
            else:
                cls.template_apply_mask_to_image_with_channels_2args(cls.function_apply_mask_exclude_voxels,
                                                                     images_array, masks_exclude_voxels_array)

    @classmethod
    def apply_mask_exclude_voxels_fillzero(cls, images_array, masks_exclude_voxels_array):

        if cls.check_correct_shape_input_array(images_array.shape, masks_exclude_voxels_array.shape):
            if cls.is_images_array_without_channels(images_array.shape, masks_exclude_voxels_array.shape):
                return cls.function_apply_mask_exclude_voxels_fillzero(images_array, masks_exclude_voxels_array)
            else:
                cls.template_apply_mask_to_image_with_channels_2args(cls.function_apply_mask_exclude_voxels_fillzero,
                                                                     images_array, masks_exclude_voxels_array)

    @classmethod
    def reverse_mask_exclude_voxels(cls, images_array, masks_exclude_voxels_array, original_images_array):

        if cls.check_correct_shape_input_array(images_array.shape, masks_exclude_voxels_array.shape):
            if cls.is_images_array_without_channels(images_array.shape, masks_exclude_voxels_array.shape):
                return cls.function_reverse_mask_exclude_voxels(images_array, masks_exclude_voxels_array, original_images_array)
            else:
                cls.template_apply_mask_to_image_with_channels_3args(cls.function_reverse_mask_exclude_voxels,
                                                                     images_array, masks_exclude_voxels_array. original_images_array)

    @classmethod
    def reverse_mask_exclude_voxels_fillzero(cls, images_array, masks_exclude_voxels_array):

        if cls.check_correct_shape_input_array(images_array.shape, masks_exclude_voxels_array.shape):
            if cls.is_images_array_without_channels(images_array.shape, masks_exclude_voxels_array.shape):
                return cls.function_reverse_mask_exclude_voxels_fillzero(images_array, masks_exclude_voxels_array)
            else:
                cls.template_apply_mask_to_image_with_channels_2args(cls.function_reverse_mask_exclude_voxels_fillzero,
                                                                     images_array, masks_exclude_voxels_array)


class OperationBinaryMasks(OperationMasks):

    val_mask_positive = 1

    @classmethod
    def process_masks(cls, masks_array):
        # convert to binary masks (0, 1)
        return np.where(masks_array != cls.val_mask_background, cls.val_mask_positive, cls.val_mask_background)

    @classmethod
    def check_masks(cls, masks_array):
        #check that 'masks_array' only contains binary vals (0, 1)
        values_found = np.unique(masks_array)
        if len(values_found) == 2 and \
            values_found[0] == cls.val_mask_background and \
            values_found[1] == cls.val_mask_positive:
            return True
        else:
            return False

    @classmethod
    def process_masks_with_exclusion(cls, masks_array):
        # convert to binary masks (0, 1), but keep exclusion mask "-1"
        return np.where(np.logical_or(masks_array != cls.val_mask_background,
                                      masks_array != cls.val_mask_exclude_voxels),
                        cls.val_mask_positive, cls.val_mask_background)

    @classmethod
    def check_masks_with_exclusion(cls, masks_array):
        # check that 'masks_array' only contains binary vals (0, 1), and exclusion mask "-1"
        values_found = np.unique(masks_array)
        if len(values_found) == 3 and \
            values_found[0] == cls.val_mask_exclude_voxels and \
            values_found[1] == cls.val_mask_background and \
            values_found[2] == cls.val_mask_positive:
            return True
        else:
            return False

    @classmethod
    def join_two_binmasks_one_image(cls, masks_array_1, masks_array_2):
        # check there is no overlap between the two masks
        #index_binmasks_1 = np.argwhere(masks_array_1 == cls.val_mask_positive)
        #index_binmasks_2 = np.argwhere(masks_array_2 == cls.val_mask_positive)

        # check there is no overlap between the two masks
        intersect_masks = np.multiply(masks_array_1, masks_array_2)
        index_posit_intersect = np.where(intersect_masks == cls.val_mask_positive)

        if len(index_posit_intersect[0] != 0):
            message = "Found intersection in between the two masks in 'join_two_binmasks_one_image'"
            CatchErrorException(message)
        else:
            return masks_array_1 + masks_array_2


class OperationMultiClassMasks(OperationMasks):

    def __init__(self, num_classes):
        self.num_classes = num_classes

    def process_masks(self, masks_array):
        # process masks to contain labels (1, ..., num_classes)
        return np.where(masks_array <= self.num_classes, masks_array, self.val_mask_background)

    def check_masks(self, masks_array):
        # check that 'masks_array' only contains labels (1, ..., num_classes)
        values_found = np.unique(masks_array)
        if len(values_found) == (self.num_classes + 1) and \
            values_found[0] == self.val_mask_background and \
            values_found[self.num_classes] == self.num_classes:
            return True
        else:
            return False

    def process_masks_with_exclusion(self, masks_array):
        # process masks to contain labels (1, ..., num_classes), but keep exclusion mask "-1"
        return np.where(np.logical_or(masks_array <= self.num_classes,
                                      masks_array != self.val_mask_exclude_voxels),
                        masks_array, self.val_mask_background)

    def check_masks_with_exclusion(self, masks_array):
        # check that 'masks_array' only contains labels (1, ..., num_classes), and exclusion mask "-1"
        values_found = np.unique(masks_array)
        if len(values_found) == (self.num_classes + 2) and \
            values_found[0] == self.val_mask_exclude_voxels and \
            values_found[1] == self.val_mask_background and \
            values_found[self.num_classes+1] == self.num_classes:
            return True
        else:
            return False
