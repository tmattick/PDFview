import os.path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gui
from pdf import PDF


def test_load_project():
    """Test loading a project containing one PDF.
    """
    window = gui.MainWindow()
    window._load_project(os.path.join("tests", "example_project.pvp"))
    pdf = PDF([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
    assert window.pdfs[0] == pdf

def test_save_project():
    """Test saving a project containing one PDF.
    """
    window = gui.MainWindow()
    pdf = PDF([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
    window.pdfs.append(pdf)
    window._save_project(os.path.join("tests", "example_project1.pvp"))
    window1 = gui.MainWindow()
    window1._load_project(os.path.join("tests", "example_project1.pvp"))
    assert window1.pdfs[0] == pdf
    os.remove(os.path.join("tests", "example_project1.pvp"))
