import json
import math
import os
import re
from typing import Optional, List, Tuple

import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize_scalar
from scipy.signal import argrelextrema


class XAxisException(Exception):
    def __init__(self, x1: npt.ArrayLike, x2: npt.ArrayLike, message: str = "The x axes provided do not match."):
        self.x1 = x1
        self.x2 = x2
        self.message = message
        super().__init__(self.message)


class UnderdeterminedException(Exception):
    def __init__(self, num_provided: int, num_needed: int, message: Optional[str] = None):
        self.num_provided = num_provided
        self.num_needed = num_needed
        if message is None:
            self.message = f"The system of equations you are trying to solve is underdetemined. You gave {num_provided} points but needed {num_needed}."
        else:
            self.message = message
        super().__init__(self.message)


class PDF:
    """This is a class representing a pair distribution function (PDF). 
    
    :param r: The range of distances in the PDF, commonly given in Angstrom.
    :type r: :class:`npt.ArrayLike`
    :param g: The values of the PDF G(r).
    :type g: :class:`npt.ArrayLike`
    :param name: The name of the PDF, defaults to "exPDF".
    :type name: str, optional
    :raises `ValueError`: If `r` and `g` are of differing lengths.
    """

    def __init__(self, r: npt.ArrayLike, g: npt.ArrayLike, name: str = "exPDF"):
        if not isinstance(r, np.ndarray):
            r = np.array(r)
        if not isinstance(g, np.ndarray):
            g = np.array(g)

        if not np.all(r[:-1] <= r[1:]):
            # sort both r and g based on r if r is not sorted
            sort_indices = np.argsort(r)
            r = r[sort_indices]
            g = g[sort_indices]

        if len(r) == len(g):
            self.r = r
            self.g = g
        else:
            raise ValueError(
                f"r and g arrays have to be of equal length. Length of r: {len(r)}, length of g: {len(g)}.")
        self.name = name
        self.scaling_factor: float = 1

    def add_point_linear(self, x: float):
        """Add a point to the `PDF` by taking the neighboring points on each side and extrapolating them linearly.
        Raises a `ValueError` if the point `x` is already in `self.r`.

        :param x: The x value of the point that will be added.
        :type x: float
        :raises `ValueError`: If `x` is already in `self.r`.
        """
        if x not in self.r:
            rmax_index: int = self._get_rmax_index(x)
            rmin_index: int = self._get_rmin_index(x)
            x1: float = self.r[rmax_index]
            x2: float = self.r[rmin_index]
            y1: float = self.g[rmax_index]
            y2: float = self.g[rmin_index]
            m: float = (y2 - y1) / (x2 - x1)
            y: float = m * x + (y1 - x1 * m)
            self._insert_point(x, y)
        else:
            raise ValueError(f"The value {x} is already present in this PDF.")

    def add_point_polynomial(self, x: float, degree: int):
        """Add a point to the `PDF` object by taking the (`degree` + 1) neighboring points and extrapolating them to a
        polynomial function. Calculate the value `y` of the function at `x` and insert `x` into `self.r`, `y` into
        `self.g`. Raises a `ValueError` if the point `x` is already in `self.r`.

        :param x: The x value of the point that will be added.
        :type x: float
        :param degree: The degree of the polynomial function that will be used for extrapolating.
        :type degree: int
        :raises `ValueError`: If `x` is already in `self.r`.
        :raises `ValueError`: If `degree` isn't a positive integer.
        :raises `UnderdeterminedException`: If there aren't enough points to solve for a polynomial of degree `degree`.
        There need to be at least (`degree` + 1) points.
        """

        def _solve_for_polynomial(a_values: List[float], b_values: List[float], x_val: float, deg: int) -> float:
            x_matrix = np.stack([a_values for _ in range(deg + 1)])
            for i, row in enumerate(x_matrix):
                x_matrix[i] = np.power(row, deg - i)
            x_matrix = x_matrix.transpose()
            a = np.linalg.solve(x_matrix, b_values)
            x_powers = np.empty(deg + 1)
            x_powers.fill(x_val)
            x_powers = np.power(x_powers, np.arange(deg, -1, -1))
            f = np.multiply(a, x_powers)
            ans: float = np.sum(f)
            return ans

        if x not in self.r:
            if degree >= 2 and isinstance(degree, int):
                rmax_index: int = self._get_rmax_index(x)
                rmin_index: int = self._get_rmin_index(x)
                num_points: int = degree + 1  # n+1
                range_min: int = max(0,
                                     rmax_index - math.floor(num_points / 2 - 0.5))  # smallest index is in bounds of r
                range_max: int = min(self.r.size - 1, rmin_index + num_points // 2)  # greatest index is in bounds of r

                x_values: List[float] = [self.r[index] for index in range(range_min, range_max)]
                y_values: List[float] = [self.g[index] for index in range(range_min, range_max)]

                """If you can't take points equally from both sides, take from one side (where there still are new
                points) until there are enough points. If there aren't enough, raise an `UnderdeterminedException`."""
                while len(x_values) < num_points:
                    if range_min > 0:
                        range_min -= 1
                        x_values.insert(0, self.r[range_min])
                        y_values.insert(0, self.g[range_min])
                    elif range_max < self.r.size - 1:
                        range_max += 1
                        x_values.append(self.r[range_max])
                        y_values.append(self.g[range_max])
                    else:
                        raise UnderdeterminedException(len(x_values), num_points)

                y: float = _solve_for_polynomial(x_values, y_values, x, degree)
                self._insert_point(x, y)
            elif degree == 1:
                self.add_point_linear(x)
            else:
                raise ValueError("degree should be a positive integer.")
        else:
            raise ValueError(f"The value {x} is already present in this PDF.")

    def scale(self, factor: float):
        """Scales the :class:`PDF` by changing `self.scaling_factor` to the given factor.
        
        :param factor: The scaling factor.
        :type factor: float
        """
        self.scaling_factor = factor

    def get_distance(self, other: 'PDF') -> float:
        """Calculates the distance between the :class:`PDF` and another via Euclidean distance. Raises a
        class:`XAxisException` if the r ranges of the PDFs are not equal.

        :param other: The PDF to calculate the distance to.
        :type other: :class:`PDF`
        :return: The distance between the :class:`PDF` objects.
        :rtype: float
        :raises `XAxisException`: If the r ranges of the  PDFs are not equal.
        """
        if self.x_axes_compatible(other):
            dist_array = self.g * self.scaling_factor - other.g * other.scaling_factor
            dist_array = np.abs(dist_array)
            dist: float = np.sum(dist_array)
            return dist
        else:
            raise XAxisException(self.r, other.r)

    def scale_to_pdf(self, other: 'PDF', start: Optional[float] = None, end: Optional[float] = None):
        """Scales the :class:`PDF` object to best approximate another :class:`PDF` object. This is done by minimizing
        the squared distance between the PDFs. Raises a class:`XAxisException`, if the r ranges of the PDFs are not
        equal.

        :param other: The PDF to approximate.
        :type other: :class:`PDF`
        :param start: r value where to start the fit.
        :type start: float, optional
        :param end: r value where to end the fit.
        :type end: float, optional
        :raises `XAxisException`: If the r ranges of the PDFs are not equal between start and end.
        """

        def _distance_with_factor(factor: float, x: np.ndarray, y: np.ndarray) -> float:
            dist_array: np.ndarray = factor * x - y
            dist_array = np.square(dist_array)
            dist_sq: float = np.sum(dist_array)
            return dist_sq

        if start is None:
            start = max(np.amin(self.r), np.amin(other.r))
        if end is None:
            end = min(np.amax(self.r), np.amax(other.r))

        start_i_self: int = self._get_rmin_index(start)
        start_i_other: int = other._get_rmin_index(start)
        end_i_self: int = self._get_rmax_index(end)
        end_i_other: int = other._get_rmax_index(end)

        if self.r[start_i_self:end_i_self].size == other.r[start_i_other:end_i_other].size and np.allclose(
                self.r[start_i_self:end_i_self], other.r[start_i_other:end_i_other], rtol=0):
            res = minimize_scalar(_distance_with_factor, args=(
                self.g[start_i_self:end_i_self], other.g[start_i_other:end_i_other] * other.scaling_factor),
                                  method="Brent")
            if res.success:
                self.scaling_factor = res.x
            else:
                print(res.message)
        else:
            raise XAxisException(self.r, other.r)

    def find_maxima(self) -> List[Tuple[float, float]]:
        """Finds the local maxima of the `PDF` object via `scipy.signal.argrelextrema`. Returns a list of all maxima
        as (r, g) pairs.

        :return: List of local maxima as (r, g) pairs.
        :rtype: List[Tuple[float, float]]
        """
        indices: Tuple[int] = argrelextrema(self.g, np.greater)[0]
        max_r_g = [(self.r[i], self.g[i]) for i in indices]
        return max_r_g

    def find_minima(self) -> List[Tuple[float, float]]:
        """Finds the local minima of the `PDF` object via `scipy.signal.argrelextrema`. Returns a list of all minima
        as (r, g) pairs.

        :return: List of local minima as (r, g) pairs.
        :rtype: List[Tuple[float, float]]
        """
        indices: Tuple[int] = argrelextrema(self.g, np.less)[0]
        min_r_g = [(self.r[i], self.g[i]) for i in indices]
        return min_r_g

    def save_gr_file(self, path: str):
        """Saves the :class:`PDF` object to a .gr-file after checking if the file already exists. Takes
        `self.scaling_factor` into account by saving (`self.g` * `self.scaling_factor`). Raises a
        :class:`FileExistsError` if the file already exists.
        
        :param path: The path to save the .gr-file to. Has to contain the file-extension.
        :type path: str
        :raises `FileExistsError`: If the file already exists.
        """
        gr_entry: str = ""
        for x, y in zip(self.r, self.g * self.scaling_factor):
            gr_entry += f"{x} {y}\n"

        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(gr_entry)
        else:
            raise FileExistsError("The file your about to write to already exists.")

    def x_axes_compatible(self, other: 'PDF') -> bool:
        """Returns whether the x axes of the given `PDF` objects are compatible, meaning they have equal size and all
        the values are close via `np.allclose`.

        :param other: The :class:`PDF` object to compare to.
        :type other: `PDF`
        :return: True, if x axes of the PDFs have equal size and all the values are close. False otherwise.
        :rtype: bool
        """
        return self.r.size == other.r.size and np.allclose(self.r, other.r, rtol=0)

    @property
    def json(self) -> str:
        """Returns all the object parameters in JSON format.

        :return: A JSON string containing all the object parameters.
        :rtype: str
        """
        object_dict: dict = {"r": self.r.tolist(), "g": self.g.tolist(), "name": self.name,
                             "scaling_factor": self.scaling_factor}
        json_str: str = json.dumps(object_dict)
        return json_str

    @json.setter
    def json(self, json_str: str):
        """Sets all object parameters according to the JSON string provided. `json_str` has to contain r
        (:class:`npt.ArrayLike`), g (:class:`npt.ArrayLike`), name (`str`) and scaling_factor (`float`).

        :param json_str: A JSON string containing all object parameters.
        :type json_str: str
        """
        object_dict: dict = json.loads(json_str)
        self.r = np.array(object_dict["r"])
        self.g = np.array(object_dict["g"])
        self.name = object_dict["name"]
        self.scaling_factor = object_dict["scaling_factor"]

    @staticmethod
    def differential_pdf(pdf1: 'PDF', pdf2: 'PDF') -> 'PDF':
        """Returns the differential :class`PDF` of two :class:`PDF` objects with the same r-range. Raises a
        class:`XAxisException`, if the r ranges of the PDFs are not equal. Alternative way to access `pdf1` - `pdf2`.

        :param pdf1: The minuend PDF.
        :type pdf1: :class:`PDF`
        :param pdf2: The subtrahend PDF.
        :type pdf2: :class:`PDF`
        :return: The differential PDF.
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the provided PDFs are not equal.
        """
        return pdf1 - pdf2

    @staticmethod
    def read_gr_file(path: str, name: Optional[str] = None) -> 'PDF':
        """Creates a :class:`PDF` object from a .gr-file that is formatted with r values in the first column and g(r) in
        the second column with one or multiple spaces separating them. Floats have to use a "." as decimal separator.
        Gives the PDF the name `name` if `name` is given, uses the base filename without extension for `PDF.name`
        otherwise.

        :param path: The path to the .gr-file to read from.
        :type path: str
        :param name: The name of the PDF.
        :type name: str, optional.
        :return: The PDF that is read from the file with name of the file without extension.
        :rtype: :class:`PDF`
        """

        def _is_data_row(row: str) -> bool:
            """Determines whether an input string is "float space(s) float".

            :param row: the string to evaluate.
            :type row: str
            :return: True if the input string is "float space(s) float", false otherwise.
            :rtype: bool
            """
            regexp: re.Pattern[str] = re.compile(
                "[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)( +)[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)")  # float space(s) float
            return bool(regexp.search(row))

        with open(path, "r") as f:
            lines = f.readlines()

        r: List[float] = []
        g: List[float] = []
        for line in lines:
            if _is_data_row(line):
                x, y = line.split(" ")
                r.append(float(x))
                g.append(float(y))

        if name is None:
            name: str = os.path.basename(path).split(".")[0]  # filename without extension

        return PDF(r, g, name)

    @staticmethod
    def from_json(json_str: str) -> 'PDF':
        """Creates a :class:`PDF` object from a JSON string. The JSON string has to contain r (:class:`npt.ArrayLike`),
        g (:class:`npt.ArrayLike`), name (`str`) and scaling_factor (`float`).

        :param json_str: The JSON string to convert to :class:`PDF` object.
        :type json_str: str
        :return: The :class:`PDF` object generated from the JSON string.
        :rtype: :class:`PDF`
        """
        json_dict: dict = json.loads(json_str)
        r: npt.ArrayLike = json_dict["r"]
        g: npt.ArrayLike = json_dict["g"]
        name: str = json_dict["name"]
        scaling_factor: float = json_dict["scaling_factor"]

        pdf = PDF(r, g, name)
        pdf.scaling_factor = scaling_factor
        return pdf

    def __eq__(self, other: 'PDF') -> bool:
        """Returns whether r and g of the given PDFs are equal.

        :param other: The :class:`PDF` to compare to.
        :type other: `PDF`
        :return: True, if r and g arrays are equal, False otherwise.
        :rtype: bool
        """
        return self.r.size == other.r.size and self.g.size == other.g.size and np.allclose(self.r, other.r,
                                                                                           rtol=0) and np.allclose(
            self.g * self.scaling_factor, other.g * other.scaling_factor, rtol=0)

    def __ne__(self, other: 'PDF') -> bool:
        """Returns whether r and g of the given PDFs are unequal.

        :param other: The :class:`PDF` to compare to.
        :type other: `PDF`
        :return: True, if r and g arrays are equal, False otherwise.
        :rtype: bool
        """
        return not self == other

    def __str__(self) -> str:
        return self.name

    def __add__(self, other: 'PDF') -> 'PDF':
        """Returns a :class:`PDF` object with the same r values as the provided :class:`PDF` objects, g values are the
        sum of the provided g values. `name` is '`self.name` + `other.name`'. Raises a `XAxisException` if r values are
        not equal.

        :param other: The :class:`PDF` object to add.
        :type other: :class:`PDF`
        :return: The sum of the PDFs.
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the :class:`PDF` objects are not equal.
        """
        if self.x_axes_compatible(other):
            return PDF(self.r, self.g * self.scaling_factor + other.g * other.scaling_factor,
                       f"{self.name} + {other.name}")
        else:
            raise XAxisException(self.r, other.r)

    def __iadd__(self, other: 'PDF') -> 'PDF':
        """Adds `other.g` to `self.g`, if `self.r` and `other.r` are equal, and returns `self`. Raises a
        `XAxisException` otherwise.

        :param other: The :class:`PDF` to add.
        :type other: :class:`PDF`
        :return: `self` after addition.
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the :class:`PDF` objects are not equal.
        """
        if self.x_axes_compatible(other):
            self.g = self.g + other.g * (other.scaling_factor / self.scaling_factor)
            return self
        else:
            raise XAxisException(self.r, other.r)

    def __sub__(self, other: 'PDF') -> 'PDF':
        """Returns a :class:`PDF` object with the same r values as the provided :class:`PDF` objects, g values are the
        difference of the provided g values. `name` is '`self.name` - `other.name`'. Raises a `XAxisException` if r
        values are not equal.

        :param other: The :class:`PDF` object to subtract.
        :type other: :class:`PDF`
        :return: The difference of the PDFs (dPDF).
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the :class:`PDF` objects are not equal.
        """
        if self.x_axes_compatible(other):
            return PDF(self.r, self.g * self.scaling_factor - other.g * other.scaling_factor,
                       f"{self.name} - {other.name}")
        else:
            raise XAxisException(self.r, other.r)

    def __isub__(self, other: 'PDF') -> 'PDF':
        """Subtracts `other.g` from `self.g`, if `self.r` and `other.r` are equal, and returns `self`. Raises a
        `XAxisException` otherwise.

        :param other: The :class:`PDF` to subtract.
        :type other: :class:`PDF`
        :return: `self` after subtraction.
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the :class:`PDF` objects are not equal.
        """
        if self.x_axes_compatible(other):
            self.g = self.g - other.g * (other.scaling_factor / self.scaling_factor)
            return self
        else:
            raise XAxisException(self.r, other.r)

    def __len__(self) -> int:
        """Returns the size of `self.r`. Should be equal to `self.g` in any reasonable :class:`PDF` instance.

        :return: The size of `self.r`.
        :rtype: int
        """
        return self.r.size

    def _get_rmin_index(self, r_min: float) -> int:
        """Gets the index of the smallest value in `self.r` where r >= `r_min`.

        :param r_min: The minimum r to look for.
        :type r_min: float
        :return: The index of `r_min`, if `r_min` is in `self.r`. Otherwise, the index of the smallest value in `self.r`
        that is greater than `r_min`.
        :rtype: int
        """
        arr: np.ndarray = np.where(self.r >= r_min)[0]  # Returns an array of indices where self.r >= r_min
        if arr.size > 0:
            index: int = np.amin(arr)
        else:
            index = 0
        return index

    def _get_rmax_index(self, r_max: float) -> int:
        """Gets the index of the greatest value in `self.r` where r <= `r_max`.

        :param r_max: The maximum r to look for.
        :type r_max: float
        :return: The index of `r_max`, if `r_max` is in `self.r`. Otherwise, the index of the greatest value in `self.r`
        that is less than `r_min`.
        :rtype: int
        """
        arr: np.ndarray = np.where(self.r <= r_max)[0]  # Returns an array of indices where self.r <= r_max
        if arr.size > 0:
            index: int = np.amax(arr)
        else:
            index = self.r.size
        return index

    def _insert_point(self, x: float, y: float):
        """Inserts a point (x,y) into `self.r` and `self.g` respectively.

        :param x: The value to insert into `self.r`.
        :type x: float
        :param y: The value to insert into `self.g`.
        :type y: float
        """
        index: int = self._get_rmin_index(x)
        if self.r.dtype == int and isinstance(x, float):
            self.r = self.r.astype(float)
        if self.g.dtype == int and isinstance(y, float):
            self.g = self.g.astype(float)
        self.r = np.insert(self.r, index, x)
        self.g = np.insert(self.g, index, y)
