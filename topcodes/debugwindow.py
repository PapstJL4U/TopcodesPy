"""Small GUI to find out if this stuff is working"""
import PySimpleGUI as sg
from scanner import Scanner
import base64
from PIL import Image
from io import BytesIO
from topcode import TopCode

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
            sg.Button("Find Codes", key="-findCode-", disabled=True),
            sg.Button("Highlight Codes", key="-highlight-", disabled=True),
            sg.Button("Show Threshold", key="-threshold-", disabled=True),
        ],
        [
            sg.FileBrowse(
                "Load Image",
                target="-path-",
                file_types=file_types,
                initial_folder="topcodes/test_img/",
                key="-browse-",
                enable_events=True,
            ),
            sg.Input(
                "", disabled=True, key="-path-", enable_events=True, expand_x=True
            ),
        ],
    ],
    expand_x=True,
)

top = sg.Column([[sg.Image(source=r"topcodes/default.png", key="-image-")]])

layout = [[top], [mid], [bottom]]

window: sg.Window = sg.Window("TopCode-Debug", layout, finalize=False)
myScanner: Scanner = Scanner()
myScanner.setMaxCodeDiameter(320)
show_threshold: bool = False
show_topcodes: bool = False
codes: list[TopCode] = []
"""
Functions
"""


def findTopCodes(path: str = "") -> None:
    global codes
    codes = myScanner.scan_by_filename(path)
    output = window["-output-"]
    output.print("--Codes--")
    for code in codes:
        output.print(code.code)
    output.print("--Finished--")

def loadImage(path: str = "") -> None:
    window["-image-"].update(source=path)

def drawCodes(path: str = "")->None:
    """draw every Topcode at the correct position and orientation"""
    img = Image.open(path)
    for code in codes:
        code.draw(img)
    img.save("drawn.png", format="PNG")
    #window["-image-"].update(data=img)
        
while True:
    event, values = window.read()
    if (
        event == sg.WIN_CLOSED or event == "Cancel"
    ):  # if user closes window or clicks cancel
        break
    if event == "-close-":
        pass
    if event == "-findCode-":
        findTopCodes(values["-path-"])
    if event == "-path-":
        window["-findCode-"].update(disabled=False)
        window["-highlight-"].update(disabled=False)
        window["-threshold-"].update(disabled=False)
        loadImage(values["-path-"])
    if event == "-threshold-":
        if not show_threshold:
            image: Image.Image = myScanner.getPreview()
            buffered = BytesIO()
            #image.save("threshold.png")
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue())
            window["-image-"].update(data=img_str)
            show_threshold = True
            window["-threshold-"].update(text="Don't show Threshold")
        else:
            loadImage(values["-path-"])
            window["-threshold-"].update(text="Show Threshold")
            show_threshold = False   
    if event == "-highlight-":
        if not show_topcodes:
            drawCodes(values["-path-"])
            show_topcodes = True
        else:
            loadImage(values["-path-"])
            show_topcodes = False


window.close()
