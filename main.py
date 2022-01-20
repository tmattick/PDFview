from typing import List
import numpy as np


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
    