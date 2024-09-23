import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import os
import copy
import Utility
import Data
from PIL import Image, ImageDraw

# TK GUI
root = Tk()
root.title("Tekinput Generator")
root.geometry("1536x864")
Utility.CentraliseWindow(root)
root.iconbitmap(Utility.MakePath(r'\..\Images\Logo\tkig.ico'))

# ttk style
style = ttk.Style()

# GUI 프레임 설정
DisplayFrame = ttk.Frame(root)
DisplayFrame.pack(pady=10)

ControlsFrame = ttk.LabelFrame(root, text="명령 제어", padding=10)
ControlsFrame.pack(pady=10)

InputFrame = ttk.LabelFrame(root, text="입력 요소", padding=10)
InputFrame.pack(pady=10)

######################## VARIABLES ###############################

save_path = r"\..\Images\Output"
preview_size = 32

inputBuffer = []
inputWidgets = []

buttons = []

final_Images = {}
preview_Images = {}
proper_previews = {}

# Preload all Images Resized.
for element in Data.Inputs:
    # If the element is a space, create a transparent image
    if element.name == 'SPACE':
        f_im = Image.new("RGBA", (preview_size, preview_size), (255, 255, 255, 0))  # Fully transparent image
    else:
        f_im = Utility.MakeImage(element.filepath)

    final_Images[element.name] = f_im
    # Resizing images for preview
    p_im = copy.deepcopy(f_im)
    y = p_im.size[1] / preview_size
    x = p_im.size[0] / y
    preview_Images[element.name] = p_im.resize((32, 32))
    p_im.thumbnail((x, preview_size))
    proper_previews[element.name] = p_im

comboText = tk.StringVar()
comboText.set("Combo Output")

displayFinalOutput = BooleanVar()
displayFinalOutput.set(TRUE)

current_input_index = None  # 현재 선택된 이미지의 인덱스
focused = False  # True면 포커싱 상태임

######################## FUNCTIONS ###############################
def ensure_output_directory():
    """Output 디렉토리가 없으면 생성하는 함수"""
    aps_path = os.path.abspath(r"..\Images\Output")
    if not os.path.exists(aps_path):
        os.makedirs(aps_path)
        print(f"디렉토리가 생성되었습니다: {aps_path}")

def generateImage():
    root.focus_set()

    ensure_output_directory()
    
    if len(inputBuffer) == 0:
        return

    totalLength = sum(final_Images[element.name].size[0] for element in inputBuffer)

    # Create new empty image, RGBA mode, and size
    new_im = Utility.NewImage('RGBA', totalLength, final_Images[inputBuffer[0].name].size[1])

    currentLength = 0
    for element in inputBuffer:
        new_im.paste(final_Images[element.name], (currentLength, 0))
        currentLength += final_Images[element.name].size[0]

    new_im.save(Utility.MakePath(save_path + '\\' + generateFilename() + '.png'))

    if displayFinalOutput.get():
        new_im.show()

    

def generateFilename():
    text = "".join(input.fileDisplay for input in inputBuffer)
    return text

def generateText():
    if len(inputBuffer) == 0:
        comboText.set("Combo Output")
    else:
        comboText.set("".join(input.display for input in inputBuffer))

def addInput(input):
    # 선택된 이미지 옆에 추가
    index = len(inputBuffer) if not focused else current_input_index + 1
    inputBuffer.insert(index, input)

    # Create image for preview
    image = proper_previews[input.name]
    photo = Utility.MakeTKImageWithImage(image)

    # Create label
    label = ttk.Label(comboFrame, image=photo, style='InputLabel.TLabel')
    label.image = photo

    def on_click(event, idx=index):
        global focused

        focused = False
        
        highlightInput(idx, current_input_index)

    label.bind("<Button-1>", on_click)
    label.pack(side='left', before=inputWidgets[index] if index < len(inputWidgets) else None)

    inputWidgets.insert(index, label)
    generateText()

    root.focus_set()

def clear():
    global current_input_index, focused

    root.focus_set()

    if len(inputBuffer) == 0:
        return

    inputBuffer.clear()
    current_input_index = None
    focused = False  # 포커싱 상태 초기화

    for label in inputWidgets:
        label.destroy()

    inputWidgets.clear()
    generateText()

    

def erase():
    global current_input_index, focused
    if current_input_index is None:
        return

    # 포커싱된 상태일 때만 삭제 가능
    if focused:
        inputBuffer.pop(current_input_index)
        label = inputWidgets.pop(current_input_index)
        label.destroy()

        # 포커싱된 이미지 왼쪽으로 이동
        if current_input_index > 0:
            current_input_index -= 1
        elif len(inputBuffer) > 0:
            current_input_index = 0
        else:
            current_input_index = None

    refreshInputs()
    generateText()

# Delete 키의 기능: 선택된 이미지의 오른쪽 요소 삭제
def delete_right():
    global current_input_index
    if current_input_index is None or current_input_index == len(inputBuffer) - 1:
        return

    # 오른쪽에 있는 이미지를 삭제
    if focused:
        next_index = current_input_index + 1
        inputBuffer.pop(next_index)
        label = inputWidgets.pop(next_index)
        label.destroy()

    refreshInputs()
    generateText()

def highlightInput(index, prev_index):
    global current_input_index

    # 이전 선택 해제
    if prev_index is not None and current_input_index is not None:
        prev_label = inputWidgets[prev_index]
        prev_label.configure(style='InputLabel.TLabel')

    current_input_index = index
    label = inputWidgets[current_input_index]
    label.configure(style='HighlightedInputLabel.TLabel')

def focusInput():
    global focused

    # 선택된 상태에서 포커스가 적용됨
    if current_input_index is not None:
        # 포커스 상태 전환
        focused = not focused

        # 포커스 상태에 따라 스타일 변경
        label = inputWidgets[current_input_index]
        if focused:
            label.configure(style='FocusedInputLabel.TLabel')
        else:
            label.configure(style='HighlightedInputLabel.TLabel')

def moveLeft():
    global current_input_index
    if current_input_index is None or current_input_index == 0:
        return

    index = current_input_index
    current_input_index -= 1
    highlightInput(current_input_index, index)

def moveRight():
    global current_input_index
    if current_input_index is None or current_input_index == len(inputBuffer) - 1:
        return

    index = current_input_index
    current_input_index += 1
    highlightInput(current_input_index, index)

def moveFocusedLeft():
    global current_input_index, focused
    if not focused or current_input_index == 0:
        return

    index = current_input_index
    inputBuffer[index - 1], inputBuffer[index] = inputBuffer[index], inputBuffer[index - 1]
    inputWidgets[index - 1], inputWidgets[index] = inputWidgets[index], inputWidgets[index - 1]
    current_input_index -= 1

    refreshInputs()
    generateText()

def moveFocusedRight():
    global current_input_index, focused
    if not focused or current_input_index == len(inputBuffer) - 1:
        return

    index = current_input_index
    inputBuffer[index], inputBuffer[index + 1] = inputBuffer[index + 1], inputBuffer[index]
    inputWidgets[index], inputWidgets[index + 1] = inputWidgets[index + 1], inputWidgets[index]
    current_input_index += 1
    refreshInputs()
    generateText()

def addSpace():
    if not focused:
        return

    # 공백 한 칸만 추가되도록 수정
    space_input = Data.Input('SPACE', r'\Images\Inputs\space.png', ' ', '_', (0, 0), None)
    addInput(space_input)

def refreshInputs():
    for widget in comboFrame.winfo_children():
        widget.destroy()

    for index, input in enumerate(inputBuffer):
        image = proper_previews[input.name]
        photo = Utility.MakeTKImageWithImage(image)
        label = ttk.Label(comboFrame, image=photo, style='InputLabel.TLabel')
        label.image = photo

        def on_click(event, idx=index):
            global focused
            
            focused = False
            
            highlightInput(idx, current_input_index)

        label.bind("<Button-1>", on_click)
        label.pack(side='left')
        inputWidgets[index] = label

    if current_input_index is not None and current_input_index < len(inputWidgets):
        label = inputWidgets[current_input_index]
        label.configure(style='HighlightedInputLabel.TLabel')

    if focused and current_input_index is not None:
        label.configure(style='FocusedInputLabel.TLabel')

######################## EVENT HANDLER FOR KEYBOARD ###############################

def on_key(event):
    global current_input_index, focused

    # 아무것도 선택되지 않은 상태에서 엔터를 눌렀을 때 오류 방지
    if event.keysym == 'Return' and current_input_index is None:
        return

    # 좌/우 방향키로 하이라이팅된 이미지 변경
    if event.keysym == 'Left' :
        moveLeft() if not focused else moveFocusedLeft()

    elif event.keysym == 'Right' :
        moveRight() if not focused else moveFocusedRight()

    # 엔터키로 포커싱 설정 또는 해제
    elif event.keysym == 'Return':
        focusInput()

    # 포커싱된 이미지를 삭제
    elif event.keysym == 'BackSpace' :
        erase()

    elif event.keysym == 'Delete' :
        delete_right()

    # 스페이스바로 공백 이미지 추가
    elif event.keysym == 'space' :
        addSpace()
    
    if len(inputBuffer) <= 0:
        focused = False
    

root.bind("<KeyPress>", on_key)

######################## SCROLLCANVAS FUNCTION ###############################

def scrollCanvas(event):
    comboCanvas.configure(scrollregion=comboCanvas.bbox("all"))

######################## MISSING FUNCTION: updateSelection ###############################

def updateSelection():
    for button in buttons:
        button.btn.grid()

######################## MISSING FUNCTION: updateSelectionCallback ###############################

def updateSelectionCallback(event):
    updateSelection()

######################## GUI COMPONENTS ###############################

# Tekinput Graphic Image Label
photo = Utility.MakeTKImage(r'\..\Images\Logo\TKIG.png', 160, 90)
label = ttk.Label(DisplayFrame, image=photo)
label.grid(row=0, column=0)

comboPreviewFrame = ttk.LabelFrame(DisplayFrame, text="Combo Preview", width=1000, height=40)
comboPreviewFrame.grid(row=0, column=1)
comboPreviewFrame.grid_propagate(0)

comboCanvas = Canvas(comboPreviewFrame, width=1000, height=40)
comboFrame = Frame(comboCanvas)
myscrollbar = Scrollbar(comboPreviewFrame, orient="horizontal", command=comboCanvas.xview)
comboCanvas.configure(xscrollcommand=myscrollbar.set)
myscrollbar.pack(side="bottom", fill="x")
comboCanvas.pack(side="bottom")
comboCanvas.create_window((0, 0), window=comboFrame, anchor='nw')
comboFrame.bind("<Configure>", scrollCanvas)

# Styles
style.configure('InputLabel.TLabel', background='white')
style.configure('HighlightedInputLabel.TLabel', background='lightblue')
style.configure('FocusedInputLabel.TLabel', background='lightgreen')

# Combo letters display label
style.configure('comboDisplayLabel.TLabel', width=100, relief=SUNKEN, borderwidth=200,)
comboDisplay = ttk.Label(DisplayFrame, textvariable=comboText,
                         style='comboDisplayLabel.TLabel')
comboDisplay.grid(row=1, column=1)

# Print toggle
toggle = ttk.Checkbutton(DisplayFrame,
                         text="결과 이미지 표시", variable=displayFinalOutput)
toggle.grid(row=2, column=1)

######################## BUTTONS FOR GENERATE, CLEAR ###############################

generateBtn = ttk.Button(ControlsFrame, text="이미지 생성", command=generateImage)
generateBtn.grid(row=0, column=0, padx=5, pady=5)

clearBtn = ttk.Button(ControlsFrame, text="초기화", command=clear)
clearBtn.grid(row=0, column=1, padx=5, pady=5)

######################## KEYBOARD ACTIONS DESCRIPTION ###############################

keybindLabel = ttk.Label(ControlsFrame, text="\n\n키보드 동작:\n"
                                             "← → \t\t: 이미지 선택\n"
                                             "Enter \t\t: 포커싱 상태 활성화/비활성화\n"
                                             "Backspace, Delete\t: 포커싱 기준으로 이미지 삭제\n"
                                             "Space\t\t: 포커싱 기준으로 오른쪽에 공백 이미지 추가\n\n"
                                             "이미지를 포커싱하면, 포커싱의 오른쪽에 새 이미지가 추가됩니다.")
keybindLabel.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

######################## INPUT BUTTONS ###############################

class inputButton():
    def __init__(self, root, element):
        self.photo = Utility.MakeTKImageWithImage(preview_Images[element.name])
        self.btn = ttk.Button(root, text=element.name, image=self.photo,
                              command=lambda: addInput(element), style='InputButton.TButton')
        self.btn.grid(
            row=element.buttonLayout[0],
            column=element.buttonLayout[1],
            padx=3,
            pady=10)

        self.characterList = element.characterList

for element in Data.Inputs:
    buttons.append(inputButton(InputFrame, element))

# Character Selection widgets and functions
charSelectLabel = ttk.Label(InputFrame, text="캐릭터 선택").grid(row=0, column=20)

myCombo = ttk.Combobox(InputFrame, value=Data.characters)
updateSelection()
myCombo.bind("<<ComboboxSelected>>", updateSelectionCallback)
myCombo.grid(row=1, column=20)

root.mainloop()
