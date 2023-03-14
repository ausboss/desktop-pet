import random
import pyttsx3
import os
import threading






def normalize(list):
    mag = sum(list)
    return [v / mag for v in list]

def make_cum(list):
    acc = 0
    for i in range(len(list)):
        temp = list[i]
        list[i] = acc
        acc += temp
    return list

class WeightedRandomMap:
    def __init__(self, list):
        self.names = [obj["name"] for obj in list]
        self.P = make_cum(normalize([obj["probability"] for obj in list]))
        assert len(self.names) == len(self.P)
    def get_rand(self):
        val = random.random()
        for i, p in enumerate(self.P):
            if p > val:
                return self.names[i - 1]
        return self.names[-1] 




def speak(message, callback):
    engine = pyttsx3.init()
    engine.setProperty("pitch", 300)
    engine.say(message)
    def f():
        engine.runAndWait()
        callback()
    threading.Thread(target=f).start()