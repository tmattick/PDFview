from typing import List
import os
import numpy as np


class XAxisException(Exception):
    def __init__(self, x1, x2, message="The x axes provided do not fit."):
        self.x1 = x1
        self.x2 = x2
        self.message = message
        super().__init__(self.message)


class PDF():
    """This is a class representing a pair distribution function (PDF). 
    
    :param r: the range of distances in the PDF, commonly given in Angstrom.
    :type r: List
    :param g: the values of g(r)
    :type g: List
    :param name: the name of the PDF, defaults to "exPDF"
    :type name: str, optional
    """
    def __init__(self, r: List, g: List, name:str = "exPDF"):
        if isinstance(r, np.array):
            self.r = r
        else:
            self.r = np.array(r)
        if isinstance(r, np.array):
            self.g = g
        else:
            self.g = np.array(g)
        self.name = name
    

    def __eq__(self, __o: object) -> bool:
        """Returns whether r and g of the given PDFs are equal
        
        :param __o: the PDF to compare to
        :type __o: object
        :return: true, if r and g arrays are equal
        :rtype: bool
        """
        return np.array_equal(self.r, __o.r) and np.array_equal(self.g, __o.g)


    def scale(self, factor: float):
        """Scales the PDF by multiplying g with the factor given.
        
        :param factor: the factor with which g is getting multiplied
        :type factor: float
        """
        self.g = self.g * factor

    
    def save_gr_file(self, path: str):
        """Saves the PDF to a .gr-file after checking if the file already exists. Prompts the user whether to overwrite the existing file if it exists.
        
        :param path: The path to save the .gr-file to. Has to contain the file-extension.
        :type path: str"""
        if os.path.exists(path):
            print("The file already exists.")
            while True:
                overwrite = input("Overwrite the file? (y/n): ")
                if overwrite.lower() == "y":
                    os.remove(path)
                    break
                elif overwrite.lower() == "n":
                    return
                else:
                    print("Input could not be parsed.")
                    continue
        
        with open(path, "a") as f:
            for x, y in zip(self.r, self.g):
                f.write(f"{x} {y}\n")

    @staticmethod
    def differential_pdf(pdf1: PDF, pdf2: PDF) -> PDF:
        """Returns the differential PDF of two PDFs with the same r-range. Raises a class:`XAxisExeption`, if the r ranges of the PDFs are not equal.

        :param pdf1: the minuend PDF
        :type pdf1: :class:`PDF`
        :param pdf2: the subtrahend PDF
        :type pdf2: :class:`PDF`
        :return: the differential PDF
        :rtype: :class:`PDF`
        :raises XAxisException: if the r ranges of the provided PDFs are not equal
        """
        if np.array_equal(pdf1.r, pdf2.r):
            g = pdf1.g - pdf2.g
            return PDF(pdf1.r, g)
        else:
            raise XAxisException(pdf1.r, pdf2.r)
    

    @staticmethod
    def read_gr_file(path: str) -> PDF:
        """Reads a PDF from a .gr-file produced by PDFgetX3.
        
        :param path: the path to the .gr-file to read from
        :type path: str
        :return: the PDF that is read from the file with name of the file without extension
        :rtype: :class:`PDF`
        """
        with open(path, "r") as f:
            lines = f.readlines()
        
        r = []
        g = []
        
        for line in lines[29:]:
            x, y = line.split(" ")
            r.append(float(x))
            g.append(float(y))
        
        name: str = os.path.basename(path).split(".")[0]

        return PDF(r, g, name)
    