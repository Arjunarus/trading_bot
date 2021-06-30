import pyautogui
import time

while True:
    currentMouseX, currentMouseY = pyautogui.position() # Получаем XY координаты курсора.
    print(currentMouseX, currentMouseY)
    time.sleep(1)
