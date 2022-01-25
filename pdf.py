import os
import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize_scalar
import math
import re


class XAxisException(Exception):
    def __init__(self, x1, x2, message="The x axes provided do not match."):
        self.x1 = x1
        self.x2 = x2
        self.message = message
        super().__init__(self.message)


class PDF:
    """This is a class representing a pair distribution function (PDF). 
    
    :param r: the range of distances in the PDF, commonly given in Angstrom.
    :type r: :class:`npt.ArrayLike`
    :param g: the values of g(r).
    :type g: :class:`npt.ArrayLike`
    :param name: the name of the PDF, defaults to "exPDF".
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
        self.scaling_factor = 1

    def __eq__(self, __o: 'PDF') -> bool:
        """Returns whether r and g of the given PDFs are equal
        
        :param __o: the PDF to compare to.
        :type __o: object
        :return: true, if r and g arrays are equal, false otherwise.
        :rtype: bool
        """
        return np.array_equal(self.r, __o.r) and np.array_equal(self.g * self.scaling_factor,
                                                                __o.g * __o.scaling_factor)

    def __str__(self) -> str:
        return self.name

    def scale(self, factor: float):
        """Scales the PDF by multiplying g with the factor given.
        
        :param factor: the factor with which g is getting multiplied.
        :type factor: float
        """
        self.scaling_factor = factor

    def distance(self, other: 'PDF') -> float:
        """Calculates the distance between the PDF and another via the Euclidean distance. Raises a
        class:`XAxisException`, if the r ranges of the PDFs are not equal.

        :param other: the PDF to calculate the distance to.
        :type other: :class:`PDF`
        :raises XAxisException: if the r ranges of the  PDFs are not equal.
        """
        if np.array_equal(self.r, other.r):
            dist_array = self.g - other.g
            dist_array = np.square(dist_array)
            dist = math.sqrt(np.sum(dist_array))
            return dist
        else:
            raise XAxisException(self.r, other.r)

    def scale_to_pdf(self, other: 'PDF'):
        """Scales the PDF to best approximate another PDF. This is done by minimizing the Euclidean distance between the
        PDFs. Raises a class:`XAxisException`, if the r ranges of the PDFs are not equal.

        :param other: the PDF to approximate.
        :type other: :class:`PDF`
        :raises XAxisException: if the r ranges of the PDFs are not equal.
        """

        def _distance_with_factor(factor: float, x: np.ndarray, y: np.ndarray) -> float:
            dist_array = factor * x - y
            dist_array = np.square(dist_array)
            dist = math.sqrt(np.sum(dist_array))
            return dist

        if np.array_equal(self.r, other.r):
            res = minimize_scalar(_distance_with_factor, args=(self.g, other.g), method="Brent")
            if res.success:
                self.scaling_factor = res.x
        else:
            raise XAxisException(self.r, other.r)

    def save_gr_file(self, path: str):
        """Saves the PDF to a .gr-file after checking if the file already exists. Prompts the user whether to overwrite
        the existing file if it exists.
        
        :param path: The path to save the .gr-file to. Has to contain the file-extension.
        :type path: str
        """
        if not os.path.exists(path):
            with open(path, "a") as f:
                for x, y in zip(self.r, self.g * self.scaling_factor):
                    f.write(f"{x} {y}\n")
        else:
            raise FileExistsError("The file your about to write to already exists.")

    @staticmethod
    def differential_pdf(pdf1: 'PDF', pdf2: 'PDF') -> 'PDF':
        """Returns the differential PDF of two PDFs with the same r-range. Raises a class:`XAxisException`, if the r
        ranges of the PDFs are not equal.

        :param pdf1: the minuend PDF.
        :type pdf1: :class:`PDF`
        :param pdf2: the subtrahend PDF.
        :type pdf2: :class:`PDF`
        :return: the differential PDF.
        :rtype: :class:`PDF`
        :raises XAxisException: if the r ranges of the provided PDFs are not equal.
        """
        if np.array_equal(pdf1.r, pdf2.r):
            g = pdf1.g * pdf1.scaling_factor - pdf2.g * pdf2.scaling_factor
            return PDF(pdf1.r, g, f"{pdf1} - {pdf2}")
        else:
            raise XAxisException(pdf1.r, pdf2.r)

    @staticmethod
    def read_gr_file(path: str):
        """Reads a PDF from a .gr-file that is formatted with r values in the first column and g(r) in the second column
        with one or multiple spaces separating them. Floats have to use a "." as decimal separator.
        
        :param path: the path to the .gr-file to read from.
        :type path: str
        :return: the PDF that is read from the file with name of the file without extension.
        :rtype: :class:`PDF`
        """

        def _is_data_row(row: str) -> bool:
            """Determines whether an input string is "float space(s) float".

            :param row: the string to evaluate.
            :type row: str
            :return: True if the input string is "float space(s) float", false otherwise.
            :rtype: bool
            """
            regexp = re.compile(
                "[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)( +)[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)")  # float space(s) float
            return bool(regexp.search(row))

        with open(path, "r") as f:
            lines = f.readlines()

        r = []
        g = []
        for line in lines:
            if _is_data_row(line):
                x, y = line.split(" ")
                r.append(float(x))
                g.append(float(y))

        name: str = os.path.basename(path).split(".")[0]  # filename without extension

        return PDF(r, g, name)
