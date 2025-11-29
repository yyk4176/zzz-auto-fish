"""
基于图像识别的绝区零赛博钓鱼脚本
Author:     SmallHappyJerry
Version:    v1.0
Date:       2025-2-23
"""

import pygetwindow as gw
import pyautogui
import cv2
import numpy as np
from PIL import Image
import pydirectinput
import threading
from pynput import keyboard
import sys, time, ctypes

INTERVAL = 0.01
EXIT_KEY = keyboard.Key.esc
SWITCH_KEY = keyboard.KeyCode.from_char("k")

running = False
xoffset=0
yoffset=0


# 查找窗口
def find_window(window_name):
    windows = gw.getWindowsWithTitle(window_name)
    if windows:
        return windows[0]  # 返回找到的第一个窗口
    else:
        print(f"窗口'{window_name}'未找到")
        return None


# 截取指定区域的截图（减少频繁截图）
def capture_window_area(window, left, top, right, bottom):
    # 获取窗口的屏幕坐标
    window_left, window_top = window.topleft
    window_left += xoffset
    window_top += yoffset
    # 调整截图区域的坐标
    capture_area = (window_left + left, window_top + top,  right - left,  bottom - top)

    # 截图
    screenshot = pyautogui.screenshot(region=capture_area)
    return np.array(screenshot)


def save_image(image, file_path):
    image.save(file_path)


# 模板匹配
def match_template(screenshot, template):
    # 转为灰度图
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配
    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 返回最大相似度和匹配位置
    return max_val, max_loc


# 快速连点函数
def rapid_click(key, times, interval):
    for _ in range(times):
        pydirectinput.press(key)  # 按下并释放按键
        time.sleep(interval)  # 控制连点的速度


# 主程序
def mainloop():
    window_name = "绝区零"
    window = find_window(window_name)

    if window:
        # 确保窗口在最前面
        window.activate()

        # 设置钓鱼按钮图标的区域范围
        left, top, right, bottom = 2060, 1100, 2210, 1250
        
        # 加载模板图像
        template = cv2.imread('images/yuanhaif.png')
        shou = cv2.imread('images/yuanshou.png')
        rightshort = cv2.imread('images/rightshort1.png')
        rightlong = cv2.imread('images/rightlong1.png')
        leftshort = cv2.imread('images/leftshort1.png')
        leftlong = cv2.imread('images/leftlong1.png')
        f1 = template
        num = 0

        while True:
            # 截取多个区域的截图
            # 钓鱼按钮范围截图
            screenshot1 = capture_window_area(window, left, top, right, bottom)
            # 右侧按钮位置
            screenshot2 = capture_window_area(window, 1600, 400, 1780, 490)
            # 左侧按钮位置
            screenshot3 = capture_window_area(window, 1500, 400, 1680, 480)

            # 模板匹配
            max_val, max_loc = match_template(screenshot1, f1)
            print(f"匹配相似度：{max_val}")

            if max_val > 0.96:  # 设置阈值
                print("相似度高，点击 F 键")
                pydirectinput.press('f')  # 模拟按下 F 键
                f1 = shou if num == 0 else template  # 根据 num 来切换模板
                num = 1 - num  # 切换 num

            # 右短/长的模板匹配
            rightshort_val, _ = match_template(screenshot2, rightshort)
            rightlong_val, _ = match_template(screenshot2, rightlong)
            leftshort_val, _ = match_template(screenshot3, leftshort)
            leftlong_val, _ = match_template(screenshot3, leftlong)
            if rightshort_val > 0.7:
                pydirectinput.press('space')
                print("右短匹配相似度：连点D键")
                rapid_click('d', 6, 0.15)

            if rightlong_val > 0.7:
                print("右长匹配相似度：长按D键")
                pydirectinput.keyDown('d')  # 长按 'D' 键
                time.sleep(1.7)  # 按住的时间
                pydirectinput.keyUp('d')  # 释放 'D' 键
                pydirectinput.press('space')

            if leftshort_val > 0.7:
                print("左短匹配相似度：连点A键")
                rapid_click('a', 6, 0.15)
                pydirectinput.press('space')
            if leftlong_val > 0.7:
                print("左长匹配相似度：长按A键")
                pydirectinput.keyDown('a')
                time.sleep(1.7)
                pydirectinput.keyUp('a')
                pydirectinput.press('space')
            if window.isActive:
                print("窗口最前，点击")
                pydirectinput.click(
                    x=window.left + 2000,
                    y=window.top + 900
                )
            # 尝试减少每次的 sleep，使程序更加灵活
            screenshot_pil = Image.fromarray(screenshot1)
            save_image(screenshot_pil, "images/screenshot1.png")
            screenshot_pil = Image.fromarray(screenshot2)
            save_image(screenshot_pil, "images/screenshot2.png")
            screenshot_pil = Image.fromarray(screenshot3)
            save_image(screenshot_pil, "images/screenshot3.png")
            time.sleep(0.1)  # 每次迭代稍微睡眠一下，减轻 CPU 压力


def toggle_running(key):
    global running
    if key == SWITCH_KEY:
        running = not running
        if running:
            print("Started")
        else:
            print("Stopped")


def mymain():
    listener = keyboard.Listener(on_press=toggle_running)
    listener.start()

    # 启动线程运行主程序
    thread = threading.Thread(target=mainloop)
    thread.daemon = True
    thread.start()

    print(f"按{SWITCH_KEY}启动或停止转圈圈功能，在其他应用中也可以使用。")
    print(f"按{EXIT_KEY}退出程序。")

    # 保持主线程运行直到按下Esc键
    with keyboard.Listener(on_press=lambda key: key != EXIT_KEY) as esc_listener:
        esc_listener.join()


if __name__ == '__main__':
    # 判断当前进程是否以管理员权限运行
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('当前已是管理员权限')
        print('是否是2560*1440的有边框窗口模式？')
        print("1. 有边框窗口 2. 2560*1440全屏 3.其他")
        choice = input("请选择：")
        if choice == '1':
            xoffset = 11
            yoffset = 45
        if choice == '3':
            print('其他分辨率请修改识别区域的坐标再使用')
            time.sleep(3)
        mymain()


    else:
        print('当前不是管理员权限，以管理员权限启动新进程...')
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
