import os.path
import sys

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


def test_add3():
    """Test addition with scaling factor.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.scale(2)
    assert (test_pdf1 + test_pdf5) == PDF([1, 2, 3, 4, 5], [17, 12, 9, 6, 3])


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


def test_iadd3():
    """Test addition (+=) with scaling factor.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.scale(2)
    test_pdf1 += test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [17, 12, 9, 6, 3])


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


def test_sub3():
    """Test subtraction with scaling factor.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.scale(2)
    assert (test_pdf1 - test_pdf5) == PDF([1, 2, 3, 4, 5], [-7, -4, -3, -2, -1])


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


def test_isub3():
    """Test subtraction (-=) with scaling factor.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf5 = PDF([1, 2, 3, 4, 5], [6, 4, 3, 2, 1])
    test_pdf5.scale(2)
    test_pdf1 -= test_pdf5
    assert test_pdf1 == PDF([1, 2, 3, 4, 5], [-7, -4, -3, -2, -1])


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


def test_insert_point():
    """Test inserting a point.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf1._insert_point(2.5, 3.5)
    assert test_pdf1 == PDF([1, 2, 2.5, 3, 4, 5], [5, 4, 3.5, 3, 2, 1])


def test_add_point_linear():
    """Test whether `PDF.add_point_linear` adds a point when it is in the middle between neighboring points.
    """
    test_pdf3 = PDF([1, 2, 3, 4], [4, 3, 2, 1])
    test_pdf3.add_point_linear(2.5)
    assert test_pdf3 == PDF([1, 2, 2.5, 3, 4], [4, 3, 2.5, 2, 1])


def test_add_point_linear2():
    """Test whether `PDF.add_point_linear` adds a point when it is not in the middle between neighboring points.
    """
    test_pdf6 = PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
    test_pdf6.add_point_linear(2.2)
    assert test_pdf6 == PDF([1, 2, 2.2, 3, 4, 5], [10, 8, 7.6, 6, 4, 2])


def test_add_point_polynomial1():
    """Test adding a point using a polynomial of degree 1.
    """
    test_pdf6 = PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
    test_pdf61 = PDF([1, 2, 3, 4, 5], [10, 8, 6, 4, 2])
    test_pdf6.add_point_polynomial(2.2, 1)
    test_pdf61.add_point_linear(2.2)
    assert test_pdf6 == test_pdf61


def test_add_point_polynomial2():
    """Test adding a point using a polynomial of even degree.
    """
    test_pdf = PDF(list(range(11)), [-3, 0, 5, 12, 21, 32, 45, 60, 77, 96, 117])  # x^2+2x-3
    test_pdf1 = PDF([0, 1, 2, 3, 4, 4.7, 5, 6, 7, 8, 9, 10], [-3, 0, 5, 12, 21, 28.49, 32, 45, 60, 77, 96, 117])
    test_pdf.add_point_polynomial(4.7, 2)
    assert test_pdf == test_pdf1


def test_add_point_polynomial3():
    """Test adding a point using a polynomial of uneven degree.
    """
    test_pdf = PDF(list(range(11)), [1, -6.5, -17, 14.5, 133, 383.5, 811, 1460.5, 2377, 3605.5, 5191])
    test_pdf1 = PDF([0, 1, 2, 3, 4, 5, 5.2, 6, 7, 8, 9, 10],
                    [1, -6.5, -17, 14.5, 133, 383.5, 453.4, 811, 1460.5, 2377, 3605.5, 5191])
    test_pdf.add_point_polynomial(5.2, 3)
    assert test_pdf == test_pdf1


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


def test_read_gr_file1():
    """Test reading from a .gr-file generated by PDFgetX3.
    """
    import_pdf = PDF.read_gr_file(os.path.join("tests", "example_PDF1.gr"))
    assert import_pdf == PDF(
        [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18,
         0.19, 0.2],
        [0, 0.000792929, 0.00157326, 0.00233019, 0.00305358, 0.00373171, 0.00436159, 0.00494015, 0.00546591, 0.0059399,
         0.00637202, 0.00677166, 0.00715094, 0.00752721, 0.00791951, 0.00834747, 0.00883532, 0.0094082, 0.0100848,
         0.0108853, 0.0118365])


def test_read_gr_file2():
    """Test reading from a custom .gr-file without overhead.
    """
    import_pdf2 = PDF.read_gr_file(os.path.join("tests", "example_PDF2.gr"))
    assert import_pdf2 == PDF([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])


def test_save_gr_file():
    """Test saving a PDF to .gr-file.
    """
    test_pdf1 = PDF([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    test_pdf1.save_gr_file(os.path.join("tests", "saved_PDF.gr"))
    import_pdf = PDF.read_gr_file(os.path.join("tests", "saved_PDF.gr"))
    assert test_pdf1 == import_pdf
    os.remove(os.path.join("tests", "saved_PDF.gr"))


def test_find_maxima():
    """Test finding the maxima of a PDF.
    """
    test_pdf = PDF([1, 2, 3, 4, 5, 6], [0, 1, -1, 5, 4, 7])
    maxima = test_pdf.find_maxima()
    assert maxima == [(2, 1), (4, 5)]


def test_find_minima():
    """Test finding the minima of a PDF.
    """
    test_pdf = PDF([1, 2, 3, 4, 5, 6], [0, 1, -1, 5, 4, 7])
    minima = test_pdf.find_minima()
    assert minima == [(3, -1), (5, 4)]
