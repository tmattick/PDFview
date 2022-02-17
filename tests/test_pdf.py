import sys
import os.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from pdf import PDF, XAxisException


def test_eq1():
    """Test whether two equal PDFs are equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf2 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1 == test_pdf2


def test_eq2():
    """Test whether two PDFs of different length are equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    assert (test_pdf1 == test_pdf3) == False


def test_eq3():
    """Test whether two PDFs with differing x axes are equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    assert (test_pdf1 == test_pdf4) == False


def test_eq4():
    """Test whether two PDFs with differing values are equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 == test_pdf5) == False


def test_ne1():
    """Test whether two equal PDFs are not equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf2 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert (test_pdf1 != test_pdf2) == False


def test_ne2():
    """Test whether two PDFs of different length are not equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    assert test_pdf1 != test_pdf3


def test_ne3():
    """Test whether two PDFs with differing x axes are not equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1 != test_pdf4


def test_ne4():
    """Test whether two PDFs with differing values are not equal.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert test_pdf1 != test_pdf5


def test_add1():
    """Test whether addition of two PDFs with differing length raises an `XAxisException`.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 + test_pdf3


def test_add2():
    """Test addition of two PDFs with corresponding x axes.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 + test_pdf5) == PDF([1, 2, 3, 4, 5], [11, 8, 6, 4, 2])


def test_iadd1():
    """Test whether addition (+=) of two PDFs with differing length raises an `XAxisException`.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 += test_pdf3


def test_iadd2():
    """Test addition (+=) of two PDFs with corresponding x axes.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf1 += test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [11, 8, 6, 4, 2])


def test_sub1():
    """Test whether subtraction of two PDFs with differing length raises an `XAxisException`.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 - test_pdf4


def test_sub2():
    """Test subtraction of two PDFs with corresponding x axes.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 - test_pdf5) == PDF([1, 2, 3, 4, 5], [-1, 0, 0, 0, 0])


def test_isub1():
    """Test whether subtraction (-=) of two PDFs with differing length raises an `XAxisException`.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 -= test_pdf4


def test_isub2():
    """Test subtraction (-=) of two PDFs with corresponding x axes.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf1 -= test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [-1, 0, 0, 0, 0])


def test_len():
    """Test `PDF.length` method of PDFs.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert len(test_pdf1) == 5


def test_rmin_index1():
    """Test `PDF._rmin_index` method for rmin in r.
    """
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmin_index(1.5) == 1


def test_rmin_index2():
    """Test `PDF._rmin_index` method for rmin not in r.
    """
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmin_index(1.7) == 2


def test_rmax_index1():
    """Test `PDF._rmax_index` method for rmax in r.
    """
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmax_index(1.5) == 1


def test_rmax_index2():
    """Test `PDF._rmax_index` method for rmax not in r.
    """
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmax_index(1.7) == 1


def test_scale1():
    """Test `PDF.scale` method for an integer.
    """
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    test_pdf3.scale(2)
    assert test_pdf3 == PDF([1, 2, 3, 4], [8, 6, 4, 2])


def test_scale2():
    """Test `PDF.scale` method for a float.
    """
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    test_pdf3.scale(2.5)
    assert test_pdf3 == PDF([1, 2, 3, 4], [10, 7.5, 5, 2.5])


def test_get_distance1():
    """Test whether `PDF.get_distance` raises an `XAxisException` when the x axes do not fit.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1.get_distance(test_pdf4)


def test_get_distance2():
    """Test `PDF.get_distance` method.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert test_pdf1.get_distance(test_pdf5) == 1


def test_scale_to_pdf1():
    """Test `PDF.scale_to_pdf` for equal PDF.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf1.scale_to_pdf(test_pdf1, start=None, end=None)
    assert test_pdf1.scaling_factor == 1 and test_pdf1 == PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])


def test_scale_to_pdf2():
    """Test `PDF.scale_to_pdf` for differing PDF.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf6 = PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
    test_pdf1.scale_to_pdf(test_pdf6, start=None, end=None)
    assert test_pdf1.scaling_factor == 2 and test_pdf1 == PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])


def test_scale_to_pdf3():
    """Test `PDF.scale_to_pdf` for differing PDF with startpoint and endpoint.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf6 = PDF([1, 2, 3, 4, 5], [1000, 8, 6, 4, 8000])
    test_pdf1.scale_to_pdf(test_pdf6, start=2, end=4)
    assert test_pdf1.scaling_factor == 2 and test_pdf1 == PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])


def test_json1():
    """Test `PDF.json` property.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1.json == '{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}'


def test_json2():
    """Test `PDF.json` setter method.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.json = '{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}'
    assert test_pdf1 == test_pdf5


def test_from_json():
    """Test creation of PDFs from JSON.
    """
    test_pdf = PDF.from_json('{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}')
    assert test_pdf == PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
