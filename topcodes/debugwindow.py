"""
"""
import PySimpleGUI as sg
from scanner import Scanner

"""
Layout
"""
sg.theme("Default1")

file_types = [("PNG (*.png)", "*.png"), ("All files (*.*)", "*.*")]

bottom = sg.Column(
    [
        [sg.Text("Codes found:")],
        [sg.Multiline(default_text="", key="-output-", size=(80, 5), autoscroll=True)],
    ]
)

mid = sg.Column(
    [
        [
            sg.Button("Find Codes", key="-findCode-"),
            sg.Button("Highlight Codes", key="-highlight-"),
            sg.Button("Show Threshold", key="-treshold-"),
        ],
        [
            sg.FileBrowse(
                "Load Image",
                target="-path-",
                file_types=file_types,
                initial_folder="topcodes/test_img/",
                key="-browse-"
            ),
            sg.Input("", disabled=True, key="-path-",  enable_events=True,),
        ],
    ]
)

top = sg.Column(
    [[sg.Image(source=r"topcodes/default.png", size=(700, 700), key="-image-")]]
)

layout = [[top], [mid], [bottom]]

window: sg.Window = sg.Window("TopCode-Debug", layout, finalize=False)
myScanner: Scanner = Scanner()
"""
Functions
"""
test = r"topcodes/test_img/341.png"


def findTopCodes() -> None:
    codes: list = myScanner.scan_by_filename(test)
    output = window["-output-"]
    for code in codes:
        output.print(code)

    output.print("--Finished--")


def loadImage(path: str = "") -> None:
    window["-image-"].update(source=path)


while True:
    event, values = window.read()
    if (
        event == sg.WIN_CLOSED or event == "Cancel"
    ):  # if user closes window or clicks cancel
        break
    if event == "-close-":
        pass
    if event == "-findCode-":
        findTopCodes()
    if event == "-path-":
        loadImage(values["-path-"])


window.close()
