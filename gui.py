from abc import ABC, abstractmethod
import json
import os.path
import sys
from typing import List, Optional, Tuple
import zlib

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

from pdf import PDF, XAxisException

sg.theme("SystemDefault")
matplotlib.use("TkAgg")

VERSION: str = "0.3"


class Window(ABC):
    """An abstract class representing a PySimpleGUI window with a :method:`run` method containing the event loop.

    :param layout: A list of lists of PySimpleGUI elements. See the PySimpleGUI documentation for more info.
    :type layout: List[List[:class:`sg.Element`]]
    :param title: The title of the window.
    :type title: str
    :param finalize: Whether to finalize the window. Defaults to True.
    :type finalize: bool, optional
    :param resizable: Whether the window is resizable. Defaults to True.
    :type resizable: bool, optional
    """

    @abstractmethod
    def __init__(self, layout: List[List[sg.Element]], title: str, finalize: bool = True, resizable: bool = False):
        self.layout = layout
        # icon by Font Awesome (https://fontawesome.com/icons/chart-line?s=solid); CC BY 4.0
        try:
            icon_path: str = os.path.join(sys._MEIPASS, "chart_line.ico")
        except AttributeError:
            icon_path: str = "chart_line.ico"
        self.window = sg.Window(title, layout=layout, finalize=finalize, resizable=resizable,
                                icon=icon_path)

    @abstractmethod
    def run(self) -> Optional[PDF]:
        """The abstract event loop.
        :return: Some instances return a :class:`PDF` object when the event loop is finished.
        :rtype: :class:`PDF`, optional
        """
        raise NotImplementedError()


class MainWindow(Window):
    """The main window of the PDFview application. Inherits from :class:`Window`.
    """

    __slots__ = "pdfs", "selected_pdf", "event", "mouse_x", "mouse_y", "layout", "window"

    def __init__(self):
        self.pdfs: List[PDF] = []
        self.selected_pdf: Optional[PDF] = None
        self.event = self.values = None
        self.mouse_x: float = 0
        self.mouse_y: float = 0
        self._setup_fig_sub()

        left_layout = [
            [sg.Text("File:"), sg.In(size=(25, 1), enable_events=True, key="-FILE_IN-", expand_x=True),
             sg.FileBrowse()],
            [sg.Listbox(values=self.pdfs, enable_events=True, size=(40, 20), key="-PDF_LIST-", expand_x=True,
                        expand_y=True, right_click_menu=["Doesnt matter", ["Delete"]])],
            [sg.Frame("File IO", [[sg.Button("Import PDF", key="-IMPORT_BUTTON-"),
                                   sg.InputText(visible=False, enable_events=True, key="-SAVE_PATH-"),
                                   sg.FileSaveAs("Save PDF", file_types=((".gr-Files", ".gr"), ("ALL Files", ".*")),
                                                 default_extension=".gr",
                                                 key="-SAVE_BUTTON-"),
                                   sg.InputText(visible=False, enable_events=True, key="-PROJECT_LOAD_PATH-"),
                                   sg.FileBrowse("Load Project",
                                                 file_types=((".pvp-Files", ".pvp"), ("ALL Files", ".*")),
                                                 key="-PROJECT_LOAD_BUTTON-"),
                                   sg.InputText(visible=False, enable_events=True, key="-PROJECT_SAVE_PATH-"),
                                   sg.FileSaveAs("Save Project",
                                                 file_types=((".pvp-Files", ".pvp"), ("ALL Files", ".*")),
                                                 default_extension=".pvp", key="-PROJECT_SAVE_BUTTON-")]])],
            [sg.Frame("Combine PDFs",
                      [[sg.Button("dPDF", key="-DIFF_BUTTON-"), sg.Button("Scale to...", key="-FIT_BUTTON-"),
                        sg.Button("Find maxima", key="-MAXIMA_BUTTON-"),
                        sg.Button("Find minima", key="-MINIMA_BUTTON-")]])]
        ]
        right_layout = [
            [sg.Canvas(size=(60, 60), key="-CANVAS-", expand_x=True, expand_y=True)],
            [sg.Text("x: , y: ", key="-MOUSE_POS_TEXT-")],
            [sg.Text("Scaling Factor:"), sg.In(size=(3, 1), key="-SCALE_IN-"), sg.Button("OK", key="-SCALE_BUTTON-")],
            [sg.Frame("Current PDF",
                      [[sg.Text(f"Name: ", key="-NAME_TEXT-")],
                       [sg.Text(f"Scaling Factor: ", key="-FACTOR_TEXT-")]])]]
        layout = [[sg.Column(left_layout, expand_x=True, expand_y=True), sg.VSeperator(),
                   sg.Column(right_layout, expand_x=True, expand_y=True)]]

        super().__init__(layout=layout, title=f"PDFview {VERSION}", finalize=True, resizable=True)

        self._draw_figure()

    def run(self):
        """The main event loop of :class:`MainWindow`. Terminates only when the user closes the window.
        """
        run_window = True

        while run_window:
            self.event, self.values = self.window.read()

            if self.event == "Exit" or self.event == sg.WIN_CLOSED:
                # exit window
                run_window = False
                break
            elif self.event == "-IMPORT_BUTTON-":
                # import new PDF from file
                self._import_pdf()
            elif self.event == "-DIFF_BUTTON-":
                # calculate differential PDF
                self._calc_diff_pdf()
            elif self.event == "-SCALE_BUTTON-":
                # scale a PDF to a multiple of itself
                if self.values["-PDF_LIST-"]:
                    self._scale_pdf()
                else:
                    sg.popup_error("Choose a PDF to scale.")
                self._update_pdf_info()
            elif self.event == "-FIT_BUTTON-":
                # fit the selected PDF to another one via scaling
                if self.values["-PDF_LIST-"]:
                    self.selected_pdf: PDF = self.values["-PDF_LIST-"][0]
                    self._fit_to_pdf()
                else:
                    sg.popup_error("Select a PDF to scale.")
                self._update_pdf_info()
            elif self.event == "-MAXIMA_BUTTON-":
                # find all local maxima and display them
                if self.values["-PDF_LIST-"]:
                    self.selected_pdf: PDF = self.values["-PDF_LIST-"][0]
                    self._display_extrema(True)
                else:
                    sg.popup_error("Select a PDF.")
            elif self.event == "-MINIMA_BUTTON-":
                # find all local minima and display them
                if self.values["-PDF_LIST-"]:
                    self.selected_pdf: PDF = self.values["-PDF_LIST-"][0]
                    self._display_extrema(False)
                else:
                    sg.popup_error("Select a PDF.")
            elif self.event == "-SAVE_PATH-":
                # save the selected PDF
                if self.values["-PDF_LIST-"]:
                    self.selected_pdf: PDF = self.values["-PDF_LIST-"][0]
                    self.selected_pdf.save_gr_file(self.values["-SAVE_PATH-"])
                else:
                    sg.popup_error("Select a PDF to save.")
            elif self.event == "Delete":
                # delete the selected PDF
                if self.values["-PDF_LIST-"]:
                    self.selected_pdf: PDF = self.values["-PDF_LIST-"][0]
                    self._delete_pdf()
                    self._draw_new_plot()
                self._update_pdf_info()
            elif self.event == "-PROJECT_SAVE_PATH-":
                # save project as a whole
                self._save_project(self.values["-PROJECT_SAVE_PATH-"])
            elif self.event == "-PROJECT_LOAD_PATH-":
                # load project as a whole
                self._load_project(self.values["-PROJECT_LOAD_PATH-"])
            elif self.event == "-PDF_LIST-":
                # PDF is selected from PDF list
                self._update_pdf_info()

        self.window.close()

    # working with PDFs
    def _import_pdf(self):
        """Method for importing :class:`PDF` objects from file. Appends them to `self.pdfs` and plots them to the
        right-hand canvas.
        """
        path: str = self.window["-FILE_IN-"].get()
        try:
            pdfs: Tuple[PDF] | Tuple[PDF, PDF] = PDF.read_from_file(path)
        except UnicodeDecodeError:
            sg.popup_error("The file could not be read as a PDF.")
            return
        for pdf in pdfs:
            self.pdfs.append(pdf)
            self.window["-PDF_LIST-"].update(self.pdfs)
            self._add_to_plot()

    def _calc_diff_pdf(self):
        """Method for calculating dPDFs. Opens a :class:`DiffWindow` object, that returns the dPDF from two selected
        PDFs as a :class:`PDF` object. Appends it to `self.pdfs` and plots it on the right-hand canvas.
        """
        diff_window = DiffWindow(self.pdfs)
        diff_pdf: PDF = diff_window.run()
        self.pdfs.append(diff_pdf)
        self.window["-PDF_LIST-"].update(self.pdfs)
        self._add_to_plot()

    def _scale_pdf(self):
        """Method for scaling :class:`PDF` objects. Draws a new plot with the scaled PDFs on the right-hand canvas.
        """
        pdf_to_scale: PDF = self.values["-PDF_LIST-"][0]
        try:
            factor = float(self.values["-SCALE_IN-"])
        except ValueError:
            sg.popup_error("Your input could not be converted to float.")
            return
        pdf_to_scale.scale(factor)
        self._draw_new_plot()
        self.window["-PDF_LIST-"].update(self.pdfs)

    def _fit_to_pdf(self):
        """Method for scaling :class:`PDF` objects to another :class:`PDF` object. Opens a :class:`FitWindow` object
        that performs the fitting. Draws a new plot with the fitted PDFs on the right-hand canvas.
        """
        fit_window = FitWindow(self.pdfs, self.values["-PDF_LIST-"][0])
        fit_window.run()
        self._draw_new_plot()
        self.window["-PDF_LIST-"].update(self.pdfs)

    def _display_extrema(self, maxima: bool):
        """Finds all extrema of the specified type (maxima if maxima is True, else minima) and displays them in a
        `ExtremaWindow`.

        :param maxima: Whether maxima or minima should be found and displayed.
        """
        extrema: List[
            Tuple[float, float]] = self.selected_pdf.find_maxima() if maxima else self.selected_pdf.find_minima()
        extrema_window = ExtremaWindow(extrema, maxima)
        extrema_window.run()

    # mouse movement
    def mouse_move(self, event):
        if not (event.xdata is None and event.ydata is None):
            self.mouse_x, self.mouse_y = event.xdata, event.ydata
        self.window["-MOUSE_POS_TEXT-"].update(f"x: {self.mouse_x:.3f}, y: {self.mouse_y:.3f}")

    # utilities for drawing
    def _setup_fig_sub(self):
        """Sets up `self.fig` and `self.sub` for the right-hand canvas.
        """
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.fig.canvas.mpl_connect("motion_notify_event", self.mouse_move)
        self.sub = self.fig.add_subplot(111)
        self.sub.set_xlabel("r")
        self.sub.set_ylabel("G(r)")

    def _draw_figure(self):
        """Sets up `self.fig_agg` and performs the drawing on it.
        """
        self.fig_agg = FigureCanvasTkAgg(self.fig, self.window["-CANVAS-"].TKCanvas)
        self.fig_agg.draw()
        self.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
        self.fig.legend()

    def _delete_fig(self):
        """Deletes `self.fig_agg`.
        """
        self.fig_agg.get_tk_widget().forget()
        plt.close("all")

    def _add_to_plot(self):
        """This method is used for adding a new PDF to existing plots. The new :class:`PDF` object has to be the last
        element in `self.pdfs`. Replaces the old `self.fig_agg`.
        """
        self._delete_fig()
        self.sub.plot(self.pdfs[-1].r, self.pdfs[-1].g * self.pdfs[-1].scaling_factor, label=self.pdfs[-1].name)
        self._draw_figure()

    def _draw_new_plot(self):
        """This method is used for drawing an entirely new plot with all the :class:`PDF` objects in `self.pdfs`.
        Replaces the old `self.fig_agg`."""
        self._delete_fig()
        self._setup_fig_sub()

        for p in self.pdfs:
            self.sub.plot(p.r, p.g * p.scaling_factor, label=p.name)

        self._draw_figure()

    # working with PDF list
    def _delete_pdf(self):
        """Deletes the :class:`PDF` object selected in `self.values['-PDF_LIST-']` from `self.pdfs` and removes it from
        memory.
        """
        self.pdfs.remove(self.values["-PDF_LIST-"][0])
        del self.values["-PDF_LIST-"][0]
        self.window["-PDF_LIST-"].update(self.pdfs)

    def _update_pdf_info(self):
        """Sets `self.pdf` to the currently selected :class:`PDF` object and updates the information in
        `self.window['-NAME_TEXT-']` and `self.window['-FACTOR_TEXT-'] with the information about the selected PDF.
        """
        if self.values["-PDF_LIST-"]:
            self.selected_pdf = self.values["-PDF_LIST-"][0]
            self.window["-NAME_TEXT-"].update(f"Name: {self.selected_pdf.name}")
            self.window["-FACTOR_TEXT-"].update(f"Scaling Factor: {self.selected_pdf.scaling_factor}")
        else:
            # PDF list is empty
            self.selected_pdf = None
            self.window["-NAME_TEXT-"].update("Name: ")
            self.window["-FACTOR_TEXT-"].update("Scaling Factor: ")

    # working with projects
    def _save_project(self, path):
        """Saves the :class:`PDF` objects in `self.pdfs` in a zlib compressed JSON array. Saves the data to the provided
        path.

        :param path: The path where to save.
        :type path: str
        """
        data: List[str] = [pdf.json for pdf in self.pdfs]
        data_json: str = json.dumps(data)
        data_json_compressed: bytes = zlib.compress(data_json.encode())
        with open(path, "wb") as f:
            f.write(data_json_compressed)

    def _load_project(self, path):
        """Loads a project from the provided path. The project data has to be a zlib compressed JSON array containing
        data that can be read by :method:`PDF.from_json`. Creates :class:`PDF` objects from the JSON and saves them in
        `self.pdfs`. Updates the window afterwards.

        :param path: The path where to load from.
        :type path: str
        """
        with open(path, "rb") as f:
            data_json_compressed: bytes = f.read()
        data_json: str = zlib.decompress(data_json_compressed).decode()
        data: List[str] = json.loads(data_json)
        self.pdfs = [PDF.from_json(json_str) for json_str in data]
        self.window["-PDF_LIST-"].update(self.pdfs)
        self._draw_new_plot()


class DiffWindow(Window):
    """Window for calculating dPDFs. Lets you select two :class:`PDF` from `pdfs` and returns the dPDF after hitting the
    OK button. Uses :method:`PDF.differential_pdf`.

    :param pdfs: :class`PDF` objects to select from for calculating the dPDF.
    :type pdfs: List[PDF]
    """

    __slots__ = "layout", "window"

    def __init__(self, pdfs: List[PDF]):
        layout = [[sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_MINUENDS-"),
                   sg.Text(" - "),
                   sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_SUBTRAHENDS-")],
                  [sg.Button("OK", key="-DIFF_BUTTON-")]]
        super().__init__(layout, "dPDF")

    def run(self) -> Optional[PDF]:
        """The event loop for the :class:``DiffWindow``. Returns the dPDF after selecting two :class:`PDF` objects and
        hitting OK. Uses :method:`PDF.differential_pdf`.

        :return: The dPDF if the user hits OK. Otherwise, returns `None`.
        :rtype: Optional[PDF]
        """
        run_window = True
        while run_window:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                run_window = False
                break
            elif event == "-DIFF_BUTTON-":
                if values["-PDF_MINUENDS-"] and values["-PDF_SUBTRAHENDS-"]:
                    minuend: PDF = values["-PDF_MINUENDS-"][0]
                    subtrahend: PDF = values["-PDF_SUBTRAHENDS-"][0]
                else:
                    sg.popup_error("Please select a minuend and a subtrahend PDF.")
                    continue
                if minuend.x_axes_compatible(subtrahend):
                    diff_pdf: PDF = PDF.differential_pdf(minuend, subtrahend)
                    return diff_pdf
                else:
                    sg.popup_error("The provided PDFs don't share a r axis. dPDF could not be calculated.")
                    continue
        self.window.close()


class FitWindow(Window):
    """Window for fitting a :class:`PDF` objects to another :class:`PDF` object via scaling. Scales `pdf_to_fit` in
    place. Lets you select :class:`PDF` to fit to from `pdfs`. Uses :method:`PDF.scale_to_pdf`.

    :param pdfs: list of PDFs to choose the PDF to fit to.
    :type pdfs: List[PDF]
    :param pdf_to_fit: the PDF to fit.
    :type pdf_to_fit: :class:``PDF``
    """

    __slots__ = "pdf_to_fit", "layout", "window"

    def __init__(self, pdfs: List[PDF], pdf_to_fit: PDF):
        self.pdf_to_fit: PDF = pdf_to_fit
        layout = [[sg.Text("Choose a PDF to scale to.")],
                  [sg.Listbox(values=pdfs, key="-FIT_TO_PDFS-", size=(20, 5))],
                  [sg.Text("Fit from"), sg.In(size=(5, 1), key="-FIT_START_IN-"), sg.Text("to"),
                   sg.In(size=(5, 1), key="-FIT_END_IN-")],
                  [sg.Button("OK", key="-FIT_BUTTON-")]]
        super().__init__(layout, "Scale to...")

    def run(self):
        """Event loop for :class:`FitWindow`. Performs the fitting after the user hits the OK button. Uses
        :method:`PDF.scale_to_pdf`.
        """
        run_window = True

        while run_window:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                run_window = False
                break
            elif event == "-FIT_BUTTON-":
                if values["-FIT_TO_PDFS-"]:
                    fit_pdf: PDF = values["-FIT_TO_PDFS-"][0]
                else:
                    sg.popup_error("Please select a PDF to fit to.")
                    continue
                try:
                    fit_start: Optional[float] = float(values["-FIT_START_IN-"]) if values["-FIT_START_IN-"] else None
                    fit_end: Optional[float] = float(values["-FIT_END_IN-"]) if values["-FIT_END_IN-"] else None
                except ValueError:
                    sg.popup_error("Your input could not be converted to float.")
                    continue

                try:
                    self.pdf_to_fit.scale_to_pdf(fit_pdf, fit_start, fit_end)
                except XAxisException:
                    sg.popup_error("The provided PDFs don't share a r axis. Fit could not be calculated.")
                    continue
                run_window = False
                break

        self.window.close()


class ExtremaWindow(Window):
    """Window for displaying the extrema of a :class:`PDF` object.

    :param extrema: The list of extrema to be displayed as (x, y) coordinates.
    :type extrema: List[Tuple[float, float]]
    :param maxima: Whether maxima or minima are to be displayed.
    :type maxima: bool
    """

    def __init__(self, extrema: List[Tuple[float, float]], maxima: bool):
        layout = [[sg.Table(extrema, headings=["r", "g"], auto_size_columns=True)]]
        name = "Maxima" if maxima else "Minima"
        super().__init__(layout, name)

    def run(self):
        """Event loop for :class:`ExtremaWindow`. Displays the extrema given in a `sg.Table`.
        """
        run_window = True

        while run_window:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                run_window = False
                break
