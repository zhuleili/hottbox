"""
Classes for different tensor representations
"""

import numpy as np
from .operations import unfold, fold, mode_n_product


class Tensor(object):
    """ This class describes multidimensional data.

    All its methods implement all common operation on a tensor alone

    Attributes
    ----------
    _data : np.ndarray
        N-dimensional array
    _orig_shape : tuple
        Original shape of a tensor. Defined at the object creation for convenience during unfolding and folding.
        Can potentially cause a lot of problems in a future.
    _mode_names : list[str]
        Description of the tensor modes
    """

    def __init__(self, array, mode_names=None) -> None:
        """ Create object of ``Tensor`` class

        Parameters
        ----------
        array : np.ndarray
            N-dimensional array
        mode_names : list[str]
            Description of the tensor modes.
            If nothing is specified then all modes of the created ``Tensor`` get generic names ['mode-0', 'mode-1', ...]
        """
        # TODO: covert data to a specific data type (int, float etc)
        if not isinstance(array, np.ndarray):
            raise TypeError('Input data should be a numpy array')
        self._data = array.copy()
        self._orig_shape = array.shape
        self._mode_names = self._assign_names(array=array, mode_names=mode_names)

    def _assign_names(self, array, mode_names):
        """ Generate list of names for the modes of a tensor
        
        Parameters
        ----------
        array : np.ndarray
            N-dimensional array
        mode_names : list[str]
            Description of the tensor modes.

        Returns
        -------
        names : list[str]
        """
        if mode_names is None:
            names = ["mode-{}".format(mode) for mode in range(array.ndim)]
        else:
            if array.ndim != len(mode_names):
                raise ValueError("Incorrect number of names for the modes of a tensor: {0} != {1} "
                                 "('array.ndim != len(mode_names)')\n".format(array.ndim, len(mode_names)))
            if not all(isinstance(name, str) for name in mode_names):
                raise TypeError('The list of names for the modes should only contain strings!')
            names = mode_names
        return names

    def copy(self):
        """ Produces a copy of itself as a new object

        Returns
        -------
        new_object : Tensor
        """
        cls = self.__class__
        new_object = cls.__new__(cls)
        new_object.__dict__.update(self.__dict__)
        return new_object

    @property
    def data(self):
        """ N-dimensional array with data values 
        
        Returns
        -------
        array : np.ndarray
        """
        array = self._data
        return array

    @property
    def frob_norm(self):
        """ Frobenious norm of a tensor

        Returns
        -------
        float
        """
        # return np.sqrt(np.sum(self.data ** 2))
        return np.linalg.norm(self.data)

    @property
    def shape(self):
        """ Sizes of all dimensions of a tensor

        Returns
        -------
        tuple
        """
        return self.data.shape

    @property
    def order(self):
        """ Order of a tensor

        Returns
        -------
        int
        """
        return self.data.ndim

    @property
    def size(self):
        """ Number of elements in a tensor

        Returns
        -------
        int
        """
        return self.data.size

    @property
    def mode_names(self):
        """ Description of the tensor modes

        Returns
        -------
        names : list[str]
        """
        names = self._mode_names
        return names

    def rename_modes(self, new_names):
        """ Rename modes of a tensor
        
        Parameters
        ----------        
        new_name : dict
            New names for the tensor modes.
            The name of the mode defined by the Value of the dict will be renamed to the corresponding Key            
        """
        for mode in new_names.values():
            if not isinstance(mode, int):
                raise TypeError("All values of the dictionary should be integers.")
            if mode > self.order:
                raise ValueError("All specified modes should not exceed the order of the tensor.")
            if mode < 0:
                raise ValueError("All specified modes should be non-negative.")
        for name, mode in new_names.items():
            self._mode_names[mode] = name

    def describe(self):
        """ Provides general information about this instance.        
        """
        print("This tensor is of order {}, consists of {} elements and its Frobenious norm = {:.2f}.\n"
              "Sizes and names of its modes are {} and {} respectively.".format(self.order, self.size, self.frob_norm,
                                                                                self.shape, self.mode_names))

    def unfold(self, mode, inplace=True):
        """ Perform mode-n unfolding to a matrix

        Parameters
        ----------
        mode : int
            Specifies a mode along which a `tensor` will be unfolded
        inplace : bool
            If True, then modifies itself.
            If False, then creates new object (copy)

        Returns
        ----------
        tensor : Tensor
            Unfolded version of a tensor
        """
        if inplace:
            tensor = self
        else:
            tensor = self.copy()
        tensor._data = unfold(self.data, mode)


        # TODO: think of a better implementation for changing mode names. And also make use of rename_mode function
        old_mode_names = tensor.mode_names.copy()
        new_mode_names = [old_mode_names[mode]]
        old_mode_names.pop(mode)
        new_mode_names.append(old_mode_names)
        tensor._mode_names = new_mode_names

        return tensor

    def fold(self, inplace=True):
        """ Fold to the original shape (undo self.unfold)

        Parameters
        ----------
        inplace : bool
            If True, then modifies itself.
            If False, then creates new object (copy)

        Returns
        ----------
        tensor : Tensor
            Tensor of original shape (self._orig_shape)
        """
        if inplace:
            tensor = self
        else:
            tensor = self.copy()
        # TODO: fix bug when original shape has mode size equal along different modes
        # Probably this will require to specify the mode explicitly instead of inferring it
        mode = tensor._orig_shape.index(tensor.shape[0])
        tensor._data = fold(self.data, mode, self._orig_shape)

        # TODO: think of a better implementation for changing mode names. And also make use of rename_mode function
        new_mode_names = tensor.mode_names[-1].copy()
        new_mode_names.insert(mode, tensor.mode_names[0])
        tensor._mode_names = new_mode_names
        return tensor

    def mode_n_product(self, matrix, mode, inplace=True):
        """ Mode-n product of a tensor with a matrix

        Parameters
        ----------
        matrix : {Tensor, np.ndarray}
            2D array
        mode : int
            Specifies mode along which a tensor is multiplied by a `matrix`
        inplace : bool
            If True, then modifies itself.
            If False, then creates new object (copy)

        Returns
        -------
        tensor : Tensor
            The result of the mode-n product of a tensor with a `matrix` along specified `mode`.

        Notes
        -------
        Remember that mode_n product changes the shape of the tensor. Presumably, it also changes the interpretation
        of that mode
        """
        # TODO: Think about the way to change mode_description
        if isinstance(matrix, np.ndarray):
            matrix = Tensor(matrix)
        if inplace:
            tensor = self
        else:
            tensor = self.copy()
        tensor._data = mode_n_product(tensor=tensor.data, matrix=matrix.data, mode=mode)
        tensor._orig_shape = tensor.shape
        return tensor


class BaseTensorTD(object):
    """
    This class provides a general interface for a tensor represented through a tensor decomposition.
    """
    def __init__(self):
        pass

    def copy(self):
        """ Produces a copy of itself as a new object

        Returns
        -------
        new_object : BaseTensorTD
        """
        cls = self.__class__
        new_object = cls.__new__(cls)
        new_object.__dict__.update(self.__dict__)
        return new_object

    @property
    def order(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    @property
    def rank(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    @property
    def size(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    @property
    def frob_norm(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    def unfold(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    def fold(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    def mode_n_product(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')

    @property
    def reconstruct(self):
        raise NotImplementedError('Not implemented in base (BaseTensorTD) class')


class TensorCPD(BaseTensorTD):
    """ Representation of a tensor in the CPD form.

    Attributes
    ----------
    _fmat : list[np.ndarray]
        Placeholder for a list of factor matrices for the CP representation of a tensor
    _core_values : np.ndarray
        Placeholder for an array of coefficients on the super-diagonal of a core for the CP representation of a tensor
    """
    def __init__(self, fmat, core_values):
        """
        
        Parameters
        ----------
        fmat : list[np.ndarray]
            List of factor matrices for the CP representation of a tensor
        core_values : np.ndarray
            Array of coefficients on the super-diagonal of a core for the CP representation of a tensor
        """
        super(TensorCPD, self).__init__()
        self._fmat = fmat.copy()
        self._core_values = core_values.copy()

    def copy(self):
        """ Produces a copy of itself as a new object

        Returns
        -------
        new_object : TensorCPD
        """
        new_object = super(TensorCPD, self).copy()
        return new_object

    @property
    def core(self):
        """ Core tensor of the CP representation of a tensor

        Returns
        -------
        core_tensor : Tensor
        """
        core_tensor = super_diag_tensor(self.order, values=self._core_values)
        return core_tensor

    @property
    def fmat(self):
        """ List of factor matrices for the CP representation of a tensor
        
        Returns
        -------
        factor_matrices : list[np.ndarray]
        """
        factor_matrices = self._fmat
        return factor_matrices

    @property
    def order(self):
        """ Order of a tensor represented through the CPD

        Returns
        -------
        order : int
        """
        order = len(self.fmat)
        return order

    @property
    def rank(self):
        """ Rank of the CP representation of a tensor.

        Returns
        -------
        rank : tuple

        Notes
        -----
        Most often referred to as the Kryskal rank
        """
        fmat = self.fmat[0]
        rank = (fmat.shape[1],)
        return rank

    @property
    def reconstruct(self):
        """ Converts the CP representation of a tensor into a full tensor

        Returns
        -------
        tensor : Tensor
        """
        tensor = self.core
        for mode, fmat in enumerate(self.fmat):
            tensor.mode_n_product(fmat, mode=mode, inplace=True)
        return tensor


class TensorTKD(BaseTensorTD):
    """ Representation of a tensor in the Tucker form.

    Parameters
    ----------
    _fmat : list[np.ndarray]
        Placeholder for a list of factor matrices for the Tucker representation of a tensor
    _core_values : np.ndarray
        Placeholder for a core of the Tucker representation of a tensor
    """
    def __init__(self, fmat, core_values):
        """
        
        Parameters
        ----------
        fmat : list[np.ndarray]
            List of factor matrices for the Tucker representation of a tensor
        core_values : np.ndarray
            Core of the Tucker representation of a tensor
        """
        super(TensorTKD, self).__init__()
        self._fmat = fmat.copy()
        self._core_values = core_values.copy()

    def copy(self):
        """ Produces a copy of itself as a new object

        Returns
        -------
        new_object : TensorTKD
        """
        new_object = super(TensorTKD, self).copy()
        return new_object

    @property
    def core(self):
        """ Core tensor of the CP representation of a tensor

        Returns
        -------
        core_tensor : Tensor
        """
        core_tensor = Tensor(self._core_values)
        return core_tensor

    @property
    def fmat(self):
        """ List of factor matrices for the Tucker representation of a tensor
        
        Returns
        -------
        factor_matrices : list[np.ndarray]
        """
        factor_matrices = self._fmat
        return factor_matrices

    @property
    def order(self):
        """ Order of a tensor represented through the TKD

        Returns
        -------
        order : int
        """
        order = len(self.fmat)
        return order

    @property
    def rank(self):
        """ Multi-linear rank of the Tucker representation of a tensor

        Returns
        -------
        rank : tuple

        Notes
        -----
        Most often referred to as the Tucker rank
        """
        rank = tuple([fmat.shape[1] for fmat in self.fmat])
        return rank

    @property
    def reconstruct(self):
        """ Converts the Tucker representation of a tensor into a full tensor

        Returns
        -------
        tensor : Tensor
        """
        tensor = self.core
        for mode, fmat in enumerate(self.fmat):
            tensor.mode_n_product(fmat, mode=mode, inplace=True)
        return tensor


class TensorTT(BaseTensorTD):
    """ Representation of a tensor in the TT form.

    Parameters
    ----------
    core_values : list[np.ndarray]
        Placeholder for a list of cores for the Tensor Train representation of a tensor.
    full_shape : tuple
        Placeholder for a shape of the full tensor (``TensorTT.reconstruct.shape``). Makes the reconstruction process easier.
    """
    def __init__(self, core_values, full_shape):
        """
        
        Parameters
        ----------
        core_values : list[np.ndarray]
            List of cores for the Tensor Train representation of a tensor.
        full_shape : tuple
            Shape of the full tensor (``TensorTT.reconstruct.shape``). Makes the reconstruction process easier.
        """
        super(TensorTT, self).__init__()
        self._core_values = core_values.copy()
        self.full_shape = full_shape

    def copy(self):
        """ Produces a copy of itself as a new object

        Returns
        -------
        new_object : TensorTT
        """
        new_object = super(TensorTT, self).copy()
        return new_object

    def core(self, i):
        """ Specific core of the TensorTT representation

        Parameters
        ----------
        i : int
            Should not exceed the order of ``TensorTT.order - 1`` representation

        Returns
        -------
        core_tensor : Tensor
        """
        core_tensor = Tensor(self._core_values[i])
        return  core_tensor

    @property
    def cores(self):
        """ All cores of the TensorTT representation

        Returns
        -------
        core_list : list[Tensor]
        """
        core_list = [self.core(i) for i in range(len(self._core_values))]
        return core_list

    @property
    def order(self):
        """ Order of a tensor represented through the TT

        Returns
        -------
        order : int
        """
        return len(self._core_values)

    @property
    def rank(self):
        """ Rank of the TT representation of a tensor

        Returns
        -------
        rank : tuple

        Notes
        -----
        Most often referred to as the TT rank
        """
        return tuple([core_values.shape[-1] for core_values in self._core_values[:-1]])

    @property
    def reconstruct(self):
        """ Converts the TT representation of a tensor into a full tensor

        Returns
        -------
        tensor : Tensor
        """
        rank = self.rank + (1,)
        core = self.cores[0]
        data = core.data
        for i, core in enumerate(self.cores[1:]):
            shape_2d = [rank[i], rank[i+1]*self.full_shape[i+1]]
            core_flat = np.reshape(core.data, shape_2d, order='F')
            data = np.reshape(data, [-1, rank[i]], order='F')
            data = np.dot(data, core_flat)
        data = np.reshape(data, self.full_shape, order='F')
        tensor = Tensor(data)
        return tensor


def super_diag_tensor(order, values=None):
    """ Super-diagonal tensor of the specified `order`.

    Parameters
    ----------
    order : int
        Desired order of the tensor
    values : np.ndarray
        Array of values on the super-diagonal of a tensor. By default contains only ones.
        Length of this vector defines the Kryskal rank of a tensor.

    Returns
    -------
    tensor : Tensor
    """
    rank = values.size
    shape = (rank,) * order
    if values is None:
        values = np.ones(rank)
    core = np.zeros(shape)
    core[np.diag_indices(rank, ndim=order)] = values
    tensor = Tensor(core)
    return tensor


def residual_tensor(tensor_A, tensor_B):
    """ Residual tensor

    Parameters
    ----------
    tensor_A : Tensor
    tensor_B : {Tensor, TensorCPD, TensorTKD, TensorTT}

    Returns
    -------
    residual : Tensor
    """
    if isinstance(tensor_B, TensorCPD) or isinstance(tensor_B, TensorTKD) or isinstance(tensor_B, TensorTT):
        residual = Tensor(tensor_A.data - tensor_B.reconstruct.data)
    elif isinstance(tensor_B, Tensor):
        residual = Tensor(tensor_A.data - tensor_B.data)
    else:
        raise TypeError('Unknown data type of the approximation')
    return residual