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
from Preprocessing.TransformationImages import *
import scipy.ndimage as ndi
from scipy.ndimage import map_coordinates, gaussian_filter
import numpy as np
np.random.seed(2017)


class ElasticDeformationImages(TransformationImages):

    def __init__(self, size_images):
        super(ElasticDeformationImages, self).__init__(size_images)

    def get_transformed_image(self, X, Y=None, seed=None):
        pass

    def get_inverse_transformed_image(self, X, Y=None, seed=None):
        print("Error: Inverse transformation not implemented for 'ElasticDeformationImages'... Exit")
        return 0

    def get_images_array(self, images_array, index=None, masks_array=None, seed=None):

        seed = self.get_mod_seed(seed)

        if masks_array is None:
            out_images_array = self.get_transformed_image(images_array, seed=seed)

            return out_images_array
        else:
            (out_images_array, out_masks_array) = self.get_transformed_image(images_array, Y=masks_array, seed=seed)

            return (out_images_array, out_masks_array)


class ElasticDeformationPixelwiseImages2D(ElasticDeformationImages):
    # implemented by Florian Calvet: florian.calvet@centrale-marseille.fr
    alpha_default = 15
    sigma_default = 3

    def __init__(self, size_images, alpha=alpha_default, sigma=sigma_default):
        self.alpha = alpha
        self.sigma = sigma
        super(ElasticDeformationPixelwiseImages2D, self).__init__(size_images)


    def get_transformed_image(self, X, Y=None, seed=None):
        if seed is not None:
            np.random.seed(seed)

        shape = X.shape
        # originally with random_state.rand * 2 - 1
        dx = gaussian_filter(np.random.randn(*shape), self.sigma, mode="constant", cval=0) * self.alpha
        dy = gaussian_filter(np.random.randn(*shape), self.sigma, mode="constant", cval=0) * self.alpha

        x, y = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), indexing='ij')
        indices = (x + dx, y + dy)

        out_X = map_coordinates(X, indices, order=3).reshape(shape)

        if Y is None:
            return out_X
        else:
            out_Y = map_coordinates(Y, indices, order=0).reshape(shape)

            return (out_X, out_Y)


class ElasticDeformationGridwiseImages2D(ElasticDeformationImages):
    # implemented by Florian Calvet: florian.calvet@centrale-marseille.fr
    sigma_default = 25
    points_default = 3

    def __init__(self, size_images, sigma=sigma_default, points=points_default):
        self.sigma  = sigma
        self.points = points
        super(ElasticDeformationGridwiseImages2D, self).__init__(size_images)


    def get_transformed_image(self, X, Y=None, seed=None):
        if seed is not None:
            np.random.seed(seed)

        shape = X.shape
        # creates the grid of coordinates of the points of the image (an ndim array per dimension)
        coordinates = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), indexing='ij')
        # creates the grid of coordinates of the points of the image in the "deformation grid" frame of reference
        xi = np.meshgrid(np.linspace(0, self.points - 1, shape[0]), np.linspace(0, self.points - 1, shape[1]), indexing='ij')
        grid = [self.points, self.points]

        # creates the deformation along each dimension and then add it to the coordinates
        for i in range(len(shape)):
            # creating the displacement at the control points
            yi = np.random.randn(*grid) * self.sigma
            # print(y.shape,coordinates[i].shape) #y and coordinates[i] should be of the same shape otherwise the same displacement is applied to every ?row? of points ?
            y = map_coordinates(yi, xi, order=3).reshape(shape)
            # adding the displacement
            coordinates[i] = np.add(coordinates[i], y)

        out_X = map_coordinates(X, coordinates, order=3).reshape(shape)

        if Y is None:
            return out_X
        else:
            out_Y = map_coordinates(Y, coordinates, order=0).reshape(shape)

            return (out_X, out_Y)


class ElasticDeformationPixelwiseImages3D(ElasticDeformationImages):
    # implemented by Florian Calvet: florian.calvet@centrale-marseille.fr
    alpha_default = 15
    sigma_default = 3

    def __init__(self, size_images, alpha=alpha_default, sigma=sigma_default):
        self.alpha = alpha
        self.sigma = sigma
        super(ElasticDeformationPixelwiseImages3D, self).__init__(size_images)


    def get_transformed_image(self, X, Y=None, seed=None):
        if seed is not None:
            np.random.seed(seed)

        shape = X.shape
        # originally with random_state.rand * 2 - 1
        dx = gaussian_filter(np.random.randn(*shape), self.sigma, mode="constant", cval=0) * self.alpha
        dy = gaussian_filter(np.random.randn(*shape), self.sigma, mode="constant", cval=0) * self.alpha
        dz = gaussian_filter(np.random.randn(*shape), self.sigma, mode="constant", cval=0) * self.alpha

        x, y, z = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
        indices = (x + dx, y + dy, z + dz)

        out_X = map_coordinates(X, indices, order=3).reshape(shape)

        if Y is None:
            return out_X
        else:
            out_Y = map_coordinates(Y, indices, order=0).reshape(shape)

            return (out_X, out_Y)


class ElasticDeformationGridwiseImages3D(ElasticDeformationImages):
    # implemented by Florian Calvet: florian.calvet@centrale-marseille.fr
    sigma_default = 25
    points_default = 3

    def __init__(self, size_images, sigma=sigma_default, points=points_default):
        self.sigma  = sigma
        self.points = points
        super(ElasticDeformationGridwiseImages3D, self).__init__(size_images)


    def get_transformed_image(self, X, Y=None, seed=None):
        if seed is not None:
            np.random.seed(seed)

        shape = X.shape
        # creates the grid of coordinates of the points of the image (an ndim array per dimension)
        coordinates = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
        # creates the grid of coordinates of the points of the image in the "deformation grid" frame of reference
        xi = np.meshgrid(np.linspace(0, self.points - 1, shape[0]), np.linspace(0, self.points - 1, shape[1]), np.linspace(0, self.points - 1, shape[2]), indexing='ij')
        grid = [self.points, self.points, self.points]

        # creates the deformation along each dimension and then add it to the coordinates
        for i in range(len(shape)):
            # creating the displacement at the control points
            yi = np.random.randn(*grid) * self.sigma
            # print(y.shape,coordinates[i].shape) #y and coordinates[i] should be of the same shape otherwise the same displacement is applied to every ?row? of points ?
            y = map_coordinates(yi, xi, order=3).reshape(shape)
            # adding the displacement
            coordinates[i] = np.add(coordinates[i], y)

        out_X = map_coordinates(X, coordinates, order=3).reshape(shape)

        if Y is None:
            return out_X
        else:
            out_Y = map_coordinates(Y, coordinates, order=0).reshape(shape)

            return (out_X, out_Y)