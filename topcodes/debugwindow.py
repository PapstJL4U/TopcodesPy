"""
"""
import PySimpleGUI as sg
from scanner import Scanner
from topcode import TopCode

"""
Layout
"""
sg.theme("Default1")

bottom = sg.Column(
    [
        [sg.Text("Codes found:")],
        [sg.Multiline(default_text="", key="-output-", size=(80, 5), autoscroll=True)],
    ]
)

mid = sg.Column(
    [
        [
            sg.Button("Highlight Codes", key="-highlight-"),
            sg.Button("Show Threshold", key="-treshold-"),
            sg.Button("Load Image", key="-load-"),
        ]
    ]
)

top = sg.Column(
    [[sg.Image(source=r"topcodes/test_img/tops.png", size=(700, 700), key="-image-")]]
)

layout = [[top], [mid], [bottom]]

window = sg.Window("TopCode-Debug", layout, finalize=False)
"""
Functions
"""


def findTopCodes() -> None:
    pass


while True:
    event, values = window.read()
    if (
        event == sg.WIN_CLOSED or event == "Cancel"
    ):  # if user closes window or clicks cancel
        break
    if event == "-close-":
        pass

window.close()
