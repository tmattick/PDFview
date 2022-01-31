import os
import numpy as np
import numpy.typing as npt
from typing import Optional, List
from scipy.optimize import minimize_scalar
import re
import json


class XAxisException(Exception):
    def __init__(self, x1: npt.ArrayLike, x2: npt.ArrayLike, message: str = "The x axes provided do not match."):
        self.x1 = x1
        self.x2 = x2
        self.message = message
        super().__init__(self.message)


class PDF:
    """This is a class representing a pair distribution function (PDF). 
    
    :param r: The range of distances in the PDF, commonly given in Angstrom.
    :type r: :class:`npt.ArrayLike`
    :param g: The values of g(r).
    :type g: :class:`npt.ArrayLike`
    :param name: The name of the PDF, defaults to "exPDF".
    :type name: str, optional
    """

    def __init__(self, r: npt.ArrayLike, g: npt.ArrayLike, name: str = "exPDF"):
        if isinstance(r, np.ndarray):
            self.r = r
        else:
            self.r = np.array(r)
        if isinstance(r, np.ndarray):
            self.g = g
        else:
            self.g = np.array(g)
        self.name = name
        self.scaling_factor: float = 1

    def __eq__(self, __o: 'PDF') -> bool:
        """Returns whether r and g of the given PDFs are equal.
        
        :param __o: The :class:`PDF` to compare to.
        :type __o: object
        :return: True, if r and g arrays are equal, False otherwise.
        :rtype: bool
        """
        return np.array_equal(self.r, __o.r) and np.array_equal(self.g * self.scaling_factor,
                                                                __o.g * __o.scaling_factor)

    def __str__(self) -> str:
        return self.name

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

    def scale(self, factor: float):
        """Scales the :class:`PDF` by multiplying `self.g` with the `factor` given.
        
        :param factor: The factor with which `self.g` is getting multiplied.
        :type factor: float
        """
        self.scaling_factor = factor

    def get_distance(self, other: 'PDF') -> float:
        """Calculates the distance between the :class:`PDF` and another via squared distance. Raises a
        class:`XAxisException` if the r ranges of the PDFs are not equal.

        :param other: The PDF to calculate the distance to.
        :type other: :class:`PDF`
        :return: The squared distance between the :class:`PDF` objects.
        :rtype: float
        :raises `XAxisException`: If the r ranges of the  PDFs are not equal.
        """
        if np.array_equal(self.r, other.r):
            dist_array = self.g * self.scaling_factor - other.g * other.scaling_factor
            dist_array = np.square(dist_array)
            dist: float = np.sum(dist_array)
            return dist
        else:
            raise XAxisException(self.r, other.r)

    def scale_to_pdf(self, other: 'PDF', start: Optional[float], end: Optional[float]):
        """Scales the :class:`PDF` object to best approximate another :class:`PDF` object. This is done by minimizing
        the squared distance between the PDFs. Raises a class:`XAxisException`, if the r ranges of the PDFs are not
        equal.

        :param other: The PDF to approximate.
        :type other: :class:`PDF`
        :param start: r value where to start the fit.
        :type start: Optional[float]
        :param end: r value where to end the fit.
        :type end: Optional[float]
        :raises `XAxisException`: If the r ranges of the PDFs are not equal between start and end.
        """

        def _distance_with_factor(factor: float, x: np.ndarray, y: np.ndarray) -> float:
            dist_array = factor * x - y
            dist_array = np.square(dist_array)
            dist: float = np.sum(dist_array)
            return dist

        if start is None:
            start = np.amax([np.amin(self.r), np.amin(other.r)])
        if end is None:
            end = np.amin([np.amax(self.r), np.amax(other.r)])

        start_i_self: int = self._get_rmin_index(start)
        start_i_other: int = other._get_rmin_index(start)
        end_i_self: int = self._get_rmax_index(end)
        end_i_other: int = other._get_rmax_index(end)
        if np.array_equal(self.r[start_i_self:end_i_self], other.r[start_i_other:end_i_other]):
            res = minimize_scalar(_distance_with_factor, args=(
                self.g[start_i_self:end_i_self], other.g[start_i_other:end_i_other] * other.scaling_factor),
                                  method="Brent")
            if res.success:
                self.scaling_factor = res.x
        else:
            raise XAxisException(self.r, other.r)

    def save_gr_file(self, path: str):
        """Saves the :class:`PDF` object to a .gr-file after checking if the file already exists. Raises a
        :class:`FileExistsError` if the file already exists.
        
        :param path: The path to save the .gr-file to. Has to contain the file-extension.
        :type path: str
        :raises `FileExistsError`: If the file already exists.
        """
        if not os.path.exists(path):
            with open(path, "a") as f:
                for x, y in zip(self.r, self.g * self.scaling_factor):
                    f.write(f"{x} {y}\n")
        else:
            raise FileExistsError("The file your about to write to already exists.")

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
        json_dict: dict = json.loads(json_str)
        self.r = np.array(json_dict["r"])
        self.g = np.array(json_dict["g"])
        self.name = json_dict["name"]
        self.scaling_factor = json_dict["scaling_factor"]

    @staticmethod
    def differential_pdf(pdf1: 'PDF', pdf2: 'PDF') -> 'PDF':
        """Returns the differential :class`PDF` of two :class:`PDF` objects with the same r-range. Raises a
        class:`XAxisException`, if the r ranges of the PDFs are not equal.

        :param pdf1: The minuend PDF.
        :type pdf1: :class:`PDF`
        :param pdf2: The subtrahend PDF.
        :type pdf2: :class:`PDF`
        :return: The differential PDF.
        :rtype: :class:`PDF`
        :raises `XAxisException`: If the r ranges of the provided PDFs are not equal.
        """
        if np.array_equal(pdf1.r, pdf2.r):
            g: np.ndarray = pdf1.g * pdf1.scaling_factor - pdf2.g * pdf2.scaling_factor
            return PDF(pdf1.r, g, f"{pdf1} - {pdf2}")
        else:
            raise XAxisException(pdf1.r, pdf2.r)

    @staticmethod
    def read_gr_file(path: str) -> 'PDF':
        """Creates a :class:`PDF` object from a .gr-file that is formatted with r values in the first column and g(r) in
        the second column with one or multiple spaces separating them. Floats have to use a "." as decimal separator.
        Uses the base filename without extension for `PDF.name`.

        :param path: The path to the .gr-file to read from.
        :type path: str
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
