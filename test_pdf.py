import pytest
from pdf import PDF, XAxisException


def test_eq1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf2 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1 == test_pdf2


def test_eq2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    assert (test_pdf1 == test_pdf3) == False


def test_eq3():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    assert (test_pdf1 == test_pdf4) == False


def test_eq4():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 == test_pdf5) == False


def test_ne1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf2 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert (test_pdf1 != test_pdf2) == False


def test_ne2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    assert test_pdf1 != test_pdf3


def test_ne3():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1 != test_pdf4


def test_ne4():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert test_pdf1 != test_pdf5


def test_add1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 + test_pdf3


def test_add2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 + test_pdf5) == PDF([1, 2, 3, 4, 5], [11, 8, 6, 4, 2])


def test_iadd1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 += test_pdf3


def test_iadd2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf1 += test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [11, 8, 6, 4, 2])


def test_sub1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 - test_pdf4


def test_sub2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert (test_pdf1 - test_pdf5) == PDF([1, 2, 3, 4, 5], [-1, 0, 0, 0, 0])


def test_isub1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1 -= test_pdf4


def test_isub2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf1 -= test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [-1, 0, 0, 0, 0])


def test_len():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert len(test_pdf1) == 5


def test_rmin_index1():
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmin_index(1.5) == 1


def test_rmin_index2():
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmin_index(1.7) == 2


def test_rmax_index1():
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmax_index(1.5) == 1


def test_rmax_index2():
    test_pdf6 = PDF([1, 1.5, 2, 2.5, 3], [5, 4, 3, 2, 1])
    assert test_pdf6._get_rmax_index(1.7) == 1


def test_scale1():
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    test_pdf3.scale(2)
    assert test_pdf3 == PDF([1, 2, 3, 4], [8, 6, 4, 2])


def test_scale2():
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    test_pdf3.scale(2.5)
    assert test_pdf3 == PDF([1, 2, 3, 4], [10, 7.5, 5, 2.5])


def test_get_distance1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf4 = PDF([1, 2, 7, 4, 5], [5, 4, 3, 2, 1])
    with pytest.raises(XAxisException):
        test_pdf1.get_distance(test_pdf4)


def test_get_distance2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    assert test_pdf1.get_distance(test_pdf5) == 1


def test_scale_to_pdf1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf1.scale_to_pdf(test_pdf1, start = None, end = None)
    assert test_pdf1.scaling_factor == 1 and test_pdf1 == PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])


def test_scale_to_pdf2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf6 = PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
    test_pdf1.scale_to_pdf(test_pdf6, start = None, end = None)
    assert test_pdf1.scaling_factor == 2 and test_pdf1 == PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])

def test_scale_to_pdf3():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf6 = PDF([1, 2, 3, 4, 5], [1000, 8, 6, 4, 8000])
    test_pdf1.scale_to_pdf(test_pdf6, start = 2, end = 4)
    assert test_pdf1.scaling_factor == 2 and test_pdf1 == PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])


def test_json1():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert test_pdf1.json == '{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}'


def test_json2():
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.json = '{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}'
    assert test_pdf1 == test_pdf5


def test_from_json():
    test_pdf = PDF.from_json('{"r": [1, 2, 3, 4, 5], "g": [5, 4, 3, 2, 1], "name": "exPDF", "scaling_factor": 1}')
    assert test_pdf == PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
