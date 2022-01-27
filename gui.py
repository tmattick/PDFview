from typing import List, Optional
from abc import ABC, abstractmethod
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
from pdf import PDF, XAxisException

sg.theme("SystemDefault")
matplotlib.use("TkAgg")


class Window(ABC):
    @abstractmethod
    def __init__(self, layout: List[List[sg.Element]], title: str, finalize: bool = True, resizable: bool = False):
        self.layout = layout
        self.window = sg.Window(title, layout=layout, finalize=finalize, resizable=resizable)

    @abstractmethod
    def run(self):
        pass


class MainWindow(Window):
    def __init__(self):
        self.pdfs: List[PDF] = []
        self._setup_fig_sub()
        self.left_layout = [
            [sg.Text("File:"), sg.In(size=(25, 1), enable_events=True, key="-FILE_IN-", expand_x=True),
             sg.FileBrowse()],
            [sg.Listbox(values=self.pdfs, enable_events=True, size=(40, 20), key="-PDF_LIST-", expand_x=True,
                        expand_y=True)],
            [sg.Frame("File IO", [[sg.Button("Import", key="-IMPORT_BUTTON-"),
                                   sg.InputText(visible=False, enable_events=True, key="-SAVE_PATH-"),
                                   # gets the filename from save dialog
                                   sg.FileSaveAs(file_types=((".gr-Files", ".gr"), ("ALL Files", ".*")),
                                                 default_extension=".gr",
                                                 key="-SAVE_BUTTON-")]])],
            [sg.Frame("Combine PDFs",
                      [[sg.Button("dPDF", key="-DIFF_BUTTON-"), sg.Button("Scale to...", key="-FIT_BUTTON-")]])]
        ]
        self.right_layout = [
            [sg.Canvas(size=(60, 60), key="-CANVAS-", expand_x=True, expand_y=True)],
            [sg.Text("Scaling Factor:"), sg.In(size=(3, 1), key="-SCALE_IN-"), sg.Button("OK", key="-SCALE_BUTTON-")]]
        super().__init__(layout=[[sg.Column(self.left_layout, expand_x=True, expand_y=True), sg.VSeperator(),
                                  sg.Column(self.right_layout, expand_x=True, expand_y=True)]], title="PDFview",
                         finalize=True, resizable=True)
        self._draw_figure()
        self.pdf: Optional[PDF] = None
        self.event = self.values = None

    def run(self):
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
                self._scale_pdf()
            elif self.event == "-FIT_BUTTON-":
                # fit the selected PDF to another one via scaling
                try:
                    self.pdf: PDF = self.values["-PDF_LIST-"][0]
                    self._fit_to_pdf()
                except IndexError:
                    sg.popup_error("Select a PDF to scale.")
            elif self.event == "-SAVE_PATH-":
                # save the selected PDF
                try:
                    self.pdf: PDF = self.values["-PDF_LIST-"][0]
                    self.pdf.save_gr_file(self.values["-SAVE_PATH-"])
                except IndexError as e:
                    sg.popup_error("Select a PDF to save.")

        self.window.close()

    def _import_pdf(self):
        path: str = self.window["-FILE_IN-"].get()
        self.pdfs.append(PDF.read_gr_file(path))
        self.window["-PDF_LIST-"].update(self.pdfs)
        self._add_to_plot()

    def _calc_diff_pdf(self):
        diff_window = DiffWindow(self.pdfs)
        diff_pdf: PDF = diff_window.run()
        self.pdfs.append(diff_pdf)
        self.window["-PDF_LIST-"].update(self.pdfs)
        self._add_to_plot()

    def _scale_pdf(self):
        try:
            pdf_to_scale: PDF = self.values["-PDF_LIST-"][0]
        except IndexError:
            sg.popup_error("Choose a PDF to scale.")
            return
        pdf_to_scale.scale(float(self.values["-SCALE_IN-"]))
        self._draw_new_plot()

    def _fit_to_pdf(self):
        fit_window = FitWindow(self.pdfs, self.values["-PDF_LIST-"][0])
        fit_window.run()
        self._draw_new_plot()

    def _setup_fig_sub(self):
        self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.sub = self.fig.add_subplot(111)
        self.sub.set_xlabel("r")
        self.sub.set_ylabel("G(r)")

    def _draw_figure(self):
        self.fig_agg = FigureCanvasTkAgg(self.fig, self.window["-CANVAS-"].TKCanvas)
        self.fig_agg.draw()
        self.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=1)

    def _delete_fig(self):
        self.fig_agg.get_tk_widget().forget()
        plt.close("all")

    def _add_to_plot(self):
        self._delete_fig()
        self.sub.plot(self.pdfs[-1].r, self.pdfs[-1].g * self.pdfs[-1].scaling_factor)
        self._draw_figure()

    def _draw_new_plot(self):
        self._delete_fig()
        self._setup_fig_sub()
        for p in self.pdfs:
            self.sub.plot(p.r, p.g * p.scaling_factor)

        self._draw_figure()


class DiffWindow(Window):
    def __init__(self, pdfs: List[PDF]):
        super().__init__([[sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_MINUENDS-"),
                           sg.Text(" - "),
                           sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_SUBTRAHENDS-")],
                          [sg.Button("OK", key="-DIFF_BUTTON-")]], "dPDF")

    def run(self) -> Optional[PDF]:
        run_window = True
        diff_pdf: Optional[PDF] = None
        while run_window:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                run_window = False
                break
            elif event == "-DIFF_BUTTON-":
                try:
                    minuend: PDF = values["-PDF_MINUENDS-"][0]
                    subtrahend: PDF = values["-PDF_SUBTRAHENDS-"][0]
                except IndexError:
                    sg.popup_error("Please select a minuend and a subtrahend PDF.")
                    continue
                try:
                    diff_pdf: PDF = PDF.differential_pdf(minuend, subtrahend)
                except XAxisException:
                    sg.popup_error("The provided PDFs don't share a r axis. dPDF could not be calculated.")
                    continue
                run_window = False
                break
        self.window.close()
        return diff_pdf


class FitWindow(Window):
    def __init__(self, pdfs: List[PDF], pdf_to_fit: PDF):
        self.pdf_to_fit = pdf_to_fit
        super().__init__([[sg.Text("Choose a PDF to scale to.")],
                          [sg.Listbox(values=pdfs, key="-FIT_TO_PDFS-", size=(20, 5))],
                          [sg.Text("Fit from"), sg.In(size=(5, 1), key="-FIT_START_IN-"), sg.Text("to"),
                           sg.In(size=(5, 1), key="-FIT_END_IN-")],
                          [sg.Button("OK", key="-FIT_BUTTON-")]], "Scale to...")

    def run(self):
        run_window = True

        while run_window:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                run_window = False
                break
            elif event == "-FIT_BUTTON-":
                try:
                    fit_pdf: PDF = values["-FIT_TO_PDFS-"][0]
                except IndexError:
                    sg.popup_error("Please select a PDF to fit to.")
                    continue

                if values["-FIT_START_IN-"] != "":
                    fit_start = float(values["-FIT_START_IN-"])
                else:
                    fit_start = None
                if values["-FIT_END_IN-"] != "":
                    fit_end = float(values["-FIT_END_IN-"])
                else:
                    fit_end = None

                try:
                    self.pdf_to_fit.scale_to_pdf(fit_pdf, fit_start, fit_end)
                except XAxisException:
                    sg.popup_error("The provided PDFs don't share a r axis. Fit could not be calculated.")
                    continue
                run_window = False
                break

        self.window.close()
