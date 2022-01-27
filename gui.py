from typing import List
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
from pdf import PDF, XAxisException

sg.theme("SystemDefault")
pdfs: List[PDF] = []
matplotlib.use("TkAgg")

# Matplotlib setup
fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
sub = fig.add_subplot(111)
sub.set_xlabel("r")
sub.set_ylabel("G(r)")


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def delete_fig(agg):
    agg.get_tk_widget().forget()
    plt.close("all")


# PySimpleGUI setup
left_layout = [
    [sg.Text("File:"), sg.In(size=(25, 1), enable_events=True, key="-FILE_IN-", expand_x=True), sg.FileBrowse()],
    [sg.Listbox(values=pdfs, enable_events=True, size=(40, 20), key="-PDF_LIST-", expand_x=True, expand_y=True)],
    [sg.Frame("File IO", [[sg.Button("Import", key="-IMPORT_BUTTON-"),
                           sg.InputText(visible=False, enable_events=True, key="-SAVE_PATH-"),
                           # gets the filename from save dialog
                           sg.FileSaveAs(file_types=((".gr-Files", ".gr"), ("ALL Files", ".*")),
                                         default_extension=".gr",
                                         key="-SAVE_BUTTON-")]])],
    [sg.Frame("Combine PDFs", [[sg.Button("dPDF", key="-DIFF_BUTTON-"), sg.Button("Scale to...", key="-FIT_BUTTON-")]])]
]
right_layout = [
    [sg.Canvas(size=(60, 60), key="-CANVAS-", expand_x=True, expand_y=True)],
    [sg.Text("Scaling Factor:"), sg.In(size=(3, 1), key="-SCALE_IN-"), sg.Button("OK", key="-SCALE_BUTTON-")]]
layout = [[sg.Column(left_layout, expand_x=True, expand_y=True), sg.VSeperator(),
           sg.Column(right_layout, expand_x=True, expand_y=True)]]

window = sg.Window("PDFview", layout=layout, finalize=True, resizable=True)
fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)


def import_pdf():
    global fig_agg
    path: str = window["-FILE_IN-"].get()
    pdfs.append(PDF.read_gr_file(path))
    window["-PDF_LIST-"].update(pdfs)
    delete_fig(fig_agg)
    sub.plot(pdfs[-1].r, pdfs[-1].g * pdfs[-1].scaling_factor)
    fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)


def calc_diff_pdf():
    global fig_agg
    diff_layout = [[sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_MINUENDS-"),
                    sg.Text(" - "),
                    sg.Listbox(values=pdfs, enable_events=True, size=(20, 5), key="-PDF_SUBTRAHENDS-")],
                   [sg.Button("OK", key="-DIFF_BUTTON-")]]
    diff_window = sg.Window("dPDF", layout=diff_layout)
    diff_run = True
    while diff_run:
        diff_event, diff_values = diff_window.read()
        if diff_event == "Exit" or diff_event == sg.WIN_CLOSED:
            diff_run = False
            break
        elif diff_event == "-DIFF_BUTTON-":
            try:
                minuend: PDF = diff_values["-PDF_MINUENDS-"][0]
                subtrahend: PDF = diff_values["-PDF_SUBTRAHENDS-"][0]
            except IndexError:
                sg.popup_error("Please select a minuend and a subtrahend PDF.")
                continue
            try:
                diff_pdf: PDF = PDF.differential_pdf(minuend, subtrahend)
            except XAxisException:
                sg.popup_error("The provided PDFs don't share a r axis. dPDF could not be calculated.")
                continue

            pdfs.append(diff_pdf)
            window["-PDF_LIST-"].update(pdfs)
            delete_fig(fig_agg)
            sub.plot(pdfs[-1].r, pdfs[-1].g * pdfs[-1].scaling_factor)
            fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
            diff_run = False
            break
    diff_window.close()


def scale_pdf():
    global fig, sub, fig_agg
    try:
        pdf_to_scale: PDF = values["-PDF_LIST-"][0]
    except IndexError:
        sg.popup_error("Choose a PDF to scale.")
        return

    pdf_to_scale.scale(float(values["-SCALE_IN-"]))
    delete_fig(fig_agg)
    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    matplotlib.use("TkAgg")
    sub = fig.add_subplot(111)
    sub.set_xlabel("r")
    sub.set_ylabel("G(r)")
    for p in pdfs:
        sub.plot(p.r, p.g * p.scaling_factor)

    fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)


def fit_to_pdf():
    global fig, sub, fig_agg

    fit_layout = [[sg.Text("Choose a PDF to scale to.")],
                  [sg.Listbox(values=pdfs, key="-FIT_TO_PDFS-", size=(20, 5))],
                  [sg.Text("Fit from"), sg.In(size=(5, 1), key="-FIT_START_IN-"), sg.Text("to"),
                   sg.In(size=(5, 1), key="-FIT_END_IN-")],
                  [sg.Button("OK", key="-FIT_BUTTON-")]]

    fit_window = sg.Window("Scale to...", layout=fit_layout)
    fit_run = True

    while fit_run:
        fit_event, fit_values = fit_window.read()
        if fit_event == "Exit" or fit_event == sg.WIN_CLOSED:
            fit_run = False
            break
        elif fit_event == "-FIT_BUTTON-":
            try:
                fit_pdf: PDF = fit_values["-FIT_TO_PDFS-"][0]
            except IndexError:
                sg.popup_error("Please select a PDF to fit to.")
                continue

            if fit_values["-FIT_START_IN-"] != "":
                fit_start = float(fit_values["-FIT_START_IN-"])
            else:
                fit_start = None
            if fit_values["-FIT_END_IN-"] != "":
                fit_end = float(fit_values["-FIT_END_IN-"])
            else:
                fit_end = None

            try:
                pdf.scale_to_pdf(fit_pdf, fit_start, fit_end)
            except XAxisException:
                sg.popup_error("The provided PDFs don't share a r axis. Fit could not be calculated.")
                continue

            delete_fig(fig_agg)
            fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
            matplotlib.use("TkAgg")
            sub = fig.add_subplot(111)
            sub.set_xlabel("r")
            sub.set_ylabel("G(r)")
            for p in pdfs:
                sub.plot(p.r, p.g * p.scaling_factor)

            fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
            fit_run = False
            break

    fit_window.close()


if __name__ == "__main__":
    run = True

    while run:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            # exit window
            run = False
            break
        elif event == "-IMPORT_BUTTON-":
            # import new PDF from file
            import_pdf()
        elif event == "-DIFF_BUTTON-":
            # calculate differential PDF
            calc_diff_pdf()
        elif event == "-SCALE_BUTTON-":
            # scale a PDF to a multiple of itself
            scale_pdf()
        elif event == "-FIT_BUTTON-":
            # fit the chosen PDF to another one via scaling
            try:
                pdf: PDF = values["-PDF_LIST-"][0]
                fit_to_pdf()
            except IndexError:
                sg.popup_error("Choose a PDF to scale.")
        elif event == "-SAVE_PATH-":
            # save the chosen PDF
            try:
                pdf: PDF = values["-PDF_LIST-"][0]
                pdf.save_gr_file(values["-SAVE_PATH-"])
            except IndexError as e:
                sg.popup_error("Choose a PDF to save.")

    window.close()
