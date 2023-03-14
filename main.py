import tkinter as tk
import json
from pet import Pet, PetState
from os.path import join
import sys

if len(sys.argv) >= 2:
    CONFIG_PATH = sys.argv[1]
else:
    CONFIG_PATH = "assets\\Tensor\\"

def create_event_func(event, pet):
    if event["type"] == "state_change":
        return lambda e: pet.set_state(event["new_state"])
    elif event["type"] == "chatgpt":
        return lambda e: pet.start_chat(event["prompt"], event["listen_state"], event["response_state"], event["end_state"], lambda _: None)


def update():
    frame = pet.next_frame()
    label.configure(image=frame)

    # Store the current window position
    current_x = window.winfo_x()
    current_y = window.winfo_y()

    window.geometry(
        f'{pet.current_state.w}x{pet.current_state.h}+{current_x}+{current_y}')
    window.after(100, update)


window = tk.Tk()

with open(join(CONFIG_PATH, "config.json")) as config:
    config_obj = json.load(config)
    states = {state['state_name']: PetState(state, CONFIG_PATH) for state in config_obj["states"]}

    for state in states.values():
        for state in state.next_states.names:
            assert state in states

    pet = Pet(states, window)

    for event in config_obj["events"]:
        event_func = create_event_func(event, pet)
        if event["trigger"] == "click":
            window.bind("<Button-3>", event_func)

window.config(highlightbackground='black')
label = tk.Label(window, bd=0, bg='black')
window.overrideredirect(True)
window.wm_attributes('-transparentcolor', 'black')
label.pack()

# Global variables to store the start_drag_x and start_drag_y
start_drag_x = 0
start_drag_y = 0
dragging = False

def on_start_drag(event):
    global start_drag_x, start_drag_y, dragging
    if event.state & 0x0004:  # Check if the CTRL key is pressed (0x0004 is the mask for the CTRL key)
        start_drag_x = event.x
        start_drag_y = event.y
        dragging = True

def on_drag(event):
    global start_drag_x, start_drag_y, dragging
    if dragging:
        x = window.winfo_x() - start_drag_x + event.x
        y = window.winfo_y() - start_drag_y + event.y
        window.geometry(f"+{x}+{y}")

def on_stop_drag(event):
    global dragging
    dragging = False

# Bind the drag events
window.bind('<ButtonPress-1>', on_start_drag)
window.bind('<B1-Motion>', on_drag)
window.bind('<ButtonRelease-1>', on_stop_drag)

window.after(100, update)
window.mainloop()
