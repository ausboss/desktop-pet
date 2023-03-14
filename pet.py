from util import WeightedRandomMap, speak
from tkinter import simpledialog, messagebox
import tkinter as tk
from os.path import join
import requests
import json
import threading
ENDPOINT = "https://zshops-rj-staffing-chan.trycloudflare.com/"

model_config = {
    "use_story": False, "use_authors_note": False, "use_world_info": False, "use_memory": False,
    "max_context_length": 2400, "max_length": 80, "rep_pen": 1.02, "rep_pen_range": 1024,
    "rep_pen_slope": 0.9, "temperature": 0.70, "tfs": 0.9, "top_p": 0.9, "typical": 1,
    "sampler_order": [6, 0, 1, 2, 3, 4, 5]}
requests.put(f"{ENDPOINT}/config", json=model_config)

class Chatbot:
    def __init__(self, fn):
        with open(fn, "r") as f:
            d = json.load(f)
            self.char_name, self.char_persona = d["char_name"], d["char_persona"]
            self.char_greeting, self.world_scenario = d["char_greeting"], d["world_scenario"]
            self.example_dialogue = d["example_dialogue"]
        self.ep, self.conversation_history = ENDPOINT, f"<START>\n{self.char_name}: {self.char_greeting}\n"
        self.character_info = f"{self.char_name}'s Persona: {self.char_persona}\nScenario: {self.world_scenario}\n<START>{self.char_greeting}\n"
        self.num_lines_to_keep = 20

    def save_conversation_threaded(self, message, callback):
        def run():
            response_text = self.save_conversation(message)
            callback(response_text)
        threading.Thread(target=run).start()

    def save_conversation(self, message):
        self.conversation_history += f'You: {message}\n'
        prompt = {"prompt": self.character_info + '\n'.join(self.conversation_history.split('\n')[-self.num_lines_to_keep:]) + f'{self.char_name}:',}
        response = requests.post(f"{self.ep}/api/v1/generate", json=prompt)
        if response.status_code == 200:
            results = response.json()['results']
            response_list = [line for line in results[0]['text'][1:].split("\n")]
            result = [response_list[0]] + [item for item in response_list[1:] if self.char_name in item]
            response_text = ''.join([item.replace(self.char_name + ": ", '\n') for item in result])
            self.conversation_history += f'{self.char_name}: {response_text}\n'
            print(response_text)
            return response_text



def read_frames(impath):
        output = []
        i = 0
        while True:
            try:
                new_frame = tk.PhotoImage(file=join(impath),format=f'gif -index {i}')
                output.append(new_frame)
            except:
                break
            i += 1
        return output

class PetState:
    def __init__(self, json_obj, impath):
        self.name = json_obj['state_name']
        self.frames = read_frames(join(impath, json_obj['file_name']))
        self.ox, self.oy, self.w, self.h = json_obj['dims']
        if 'move' in json_obj:
            self.dx, self.dy = json_obj['move']
        else:
            self.dx, self.dy = 0, 0
        self.next_states = WeightedRandomMap(json_obj['transitions_to'])


class Pet:
    def __init__(self, states, window):
        self.chatbot = Chatbot('Tensor.json')
        self.states = states
        self.window = window
        self.current_state = list(states.values())[0]
        self.__current_frame = 0
        self.x, self.y = 45, 800

    def next_frame(self):
        output = self.current_state.frames[self.__current_frame]
        self.__current_frame += 1
        if self.__current_frame == len(self.current_state.frames):
            self.__state_change()
        self.x, self.y = (
            self.x + self.current_state.dx), (self.y + self.current_state.dy)
        return output

    def __state_change(self):
        self.set_state(self.current_state.next_states.get_rand())

    def set_state(self, name: str):
        self.current_state = self.states[name]
        self.__current_frame = 0
    

    def start_chat(self, prompt: str, listen_state: str, response_state: str, end_state: str, callback):
        self.set_state(listen_state)
        query = simpledialog.askstring("Input", "Send Message:", parent=self.window)
        
        if query:  # Check if the user provided any input
            def show_response(response_text):
                messagebox.showinfo("Response", response_text)
                callback(None)  # Pass a dummy argument

            self.chatbot.save_conversation_threaded(prompt % query, show_response)
            self.set_state(response_state)
        else:
            self.set_state(end_state)  # Set the end state if no input is provided
