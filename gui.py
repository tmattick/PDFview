import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from pdf import PDF

sg.theme("SystemDefault")
pdfs = []
pdf_names = []

# Matplotlib
fig = matplotlib.figure.Figure(figsize=(5,4), dpi=100)
matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

# PySimpleGUI
left_layout = [
    [sg.Text("File:"), sg.In(size=(25,1), enable_events=True, key="-FILE_IN-"), sg.FileBrowse()],
    [sg.Listbox(values=pdf_names, enable_events=True, size=(40,20), key="-PDF_LIST-")],
    [sg.Button("Import", key="-IMPORT_BUTTON-")]
    ]
right_layout = [[sg.Canvas(size=(40,40), key="-CANVAS-")]]
layout = [[sg.Column(left_layout), sg.VSeperator(), sg.Column(right_layout)]]

window = sg.Window("PDFview", layout=layout, finalize=True)
fig_canvas_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)


if __name__ == "__main__":
    run = True

    while run:
        event, values = window.read()

        # user exits window
        if event == "Exit" or event == sg.WIN_CLOSED:
            run = False
            break
        elif event == "-IMPORT_BUTTON-":
            path = window["-FILE_IN-"].get()
            pdfs.append(PDF.read_gr_file(path))
            pdf_names.append(pdfs[-1].name)
            window["-PDF_LIST-"].update(pdf_names)

    window.close()
