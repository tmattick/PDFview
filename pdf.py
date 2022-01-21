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
        return np.array_equal(self.r, __o.r) and np.array_equal(self.g, __o.g)

    
    def save_gr_file(self, path: str):
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
        if np.array_equal(pdf1.r, pdf2.r):
            g = pdf1.g - pdf2.g
            return PDF(pdf1.r, g)
        else:
            raise XAxisException(pdf1.r, pdf2.r)
    

    @staticmethod
    def read_gr_file(path: str) -> PDF:
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
    