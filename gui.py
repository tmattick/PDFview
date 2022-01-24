import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
from pdf import PDF, XAxisException

sg.theme("SystemDefault")
pdfs = []

# Matplotlib setup
fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
matplotlib.use("TkAgg")
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
    [sg.Text("File:"), sg.In(size=(25, 1), enable_events=True, key="-FILE_IN-"), sg.FileBrowse()],
    [sg.Listbox(values=pdfs, enable_events=True, size=(40, 20), key="-PDF_LIST-")],
    [sg.Button("Import", key="-IMPORT_BUTTON-"), sg.Button("dPDF", key="-DIFF_BUTTON-")]
]
right_layout = [
    [sg.Canvas(size=(60, 60), key="-CANVAS-")],
    [sg.Text("Scaling Factor:"), sg.In(size=(3, 1), key="-SCALE_IN-"), sg.Button("OK", key="-SCALE_BUTTON-")]]
layout = [[sg.Column(left_layout), sg.VSeperator(), sg.Column(right_layout)]]

window = sg.Window("PDFview", layout=layout, finalize=True)
fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)

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
            path = window["-FILE_IN-"].get()
            pdfs.append(PDF.read_gr_file(path))
            window["-PDF_LIST-"].update(pdfs)
            delete_fig(fig_agg)
            sub.plot(pdfs[-1].r, pdfs[-1].g * pdfs[-1].scaling_factor)

            fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
        elif event == "-DIFF_BUTTON-":
            # calculate differential PDF
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
                    minuend = diff_values["-PDF_MINUENDS-"][0]
                    subtrahend = diff_values["-PDF_SUBTRAHENDS-"][0]
                    try:
                        diff_pdf = PDF.differential_pdf(minuend, subtrahend)
                        pdfs.append(diff_pdf)
                        window["-PDF_LIST-"].update(pdfs)
                        delete_fig(fig_agg)
                        sub.plot(pdfs[-1].r, pdfs[-1].g * pdfs[-1].scaling_factor)
                        fig_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
                        diff_run = False
                        break
                    except XAxisException as e:
                        sg.popup_error("The provided PDFs don't share a r axis. dPDF could not be calculated.")

            diff_window.close()

    window.close()
