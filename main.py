from typing import List
import numpy as np


class XAxisException(Exception):
    def __init__(self, x1, x2, message="The x axes provided do not fit."):
        self.x1 = x1
        self.x2 = x2
        self.message = message
        super().__init__(self.message)


class PDF:
    def __init__(self, r: List, g: List):
        if isinstance(r, np.array):
            self.r = r
        else:
            self.r = np.array(r)
        if isinstance(r, np.array):
            self.g = g
        else:
            self.g = np.array(g)
    

    def __eq__(self, __o: object) -> bool:
        return self.r == __o.r and self.g == __o.g

    
    @staticmethod
    def differential_pdf(pdf1, pdf2):
        if pdf1.r == pdf2.r:
            g = pdf1.g - pdf2.g
            return PDF(pdf1.r, g)
        else:
            raise XAxisException(pdf1.r, pdf2.r)
    