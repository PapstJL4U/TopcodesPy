"""Small GUI to find out if this stuff is working"""
import PySimpleGUI as sg
import time as T
from scanner import Scanner
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
        [
            sg.Text("MaxCodeDiameter"),
            sg.Slider(
                (0, 1000),
                default_value=320,
                tick_interval=200,
                enable_events=True,
                key="-code_dia-",
                orientation="horizontal",
                expand_x=True,
            ),
        ],
    ],
    expand_x=True,
)

top = sg.Column([[sg.Image(source=r"topcodes/default.png", key="-image-")]])

layout = [[top], [mid], [bottom]]

window: sg.Window = sg.Window("TopCode-Debug", layout, finalize=False)
myScanner: Scanner = Scanner()
myScanner.setMaxCodeDiameter(window["-code_dia-"].DefaultValue)
draw_codes: Image.Image | None = None
draw_threshold: Image.Image | None = None
show_threshold: bool = False
show_topcodes: bool = False
codes: list[TopCode] = []
"""
Functions
"""

def findTopCodes(path: str = "") -> None:
    """find all codes in the current displayed image"""
    global codes
    start = T.time()
    #scalene_profiler.start()
    codes = myScanner.scan_by_filename(path)
    #scalene_profiler.stop()
    output = window["-output-"]
    output.print("--Codes--")
    for code in codes:
        output.print(code.code)
    
    end = T.time()
    output.print("Ellapsed Time (ms): "+str(round((end-start)*1000,0)))
    candidates: str = str(myScanner.ccount)
    tested:str = str(myScanner.tcount)
    output.print("Candidates: "+candidates+" || Tested: "+tested)
    output.print(str(myScanner._maxu))
    output.print("--Finished--")

def reset() -> None:
    """reset buttons and buffered images"""
    global draw_codes
    draw_codes = None
    global draw_threshold
    draw_threshold = None
    global show_threshold
    show_threshold = False
    global show_topcodes
    show_topcodes = False

    window["-findCode-"].update(disabled=False)
    window["-highlight-"].update(disabled=True)
    window["-threshold-"].update(disabled=True)


def loadImage(path: str = "") -> None:
    window["-image-"].update(source=path)


def drawCodes(path: str = "") -> None:
    """draw every Topcode at the correct position and orientation"""
    global draw_codes
    buf = BytesIO()
    if draw_codes == None:
        draw_codes = Image.open(path)
        for code in codes:
            code.draw(draw_codes)

    draw_codes.save(buf, format="PNG")
    window["-image-"].update(data=buf.getvalue())


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
        window["-highlight-"].update(disabled=False)
        window["-threshold-"].update(disabled=False)

    if event == "-path-":
        reset()
        draw_codes = None
        draw_threshold = None
        loadImage(values["-path-"])

    if event == "-threshold-":
        if not show_threshold:
            image: Image.Image = myScanner.getPreview()
            buffered = BytesIO()
            # image.save("threshold.png")
            image.save(buffered, format="PNG")
            window["-image-"].update(data=buffered.getvalue())
            del image
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

    if event == "-code_dia-":
        reset()
        i: int = int(values["-code_dia-"])
        myScanner.setMaxCodeDiameter(i)


window.close()
