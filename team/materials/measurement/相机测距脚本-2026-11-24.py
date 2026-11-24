import csv
import os
import time
import tkinter as tk
from tkinter import messagebox
import cv2
import depthai as dai
import numpy as np
from PIL import Image, ImageTk

WIDTH, HEIGHT = 640, 400
SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'distance_measurements.csv')

pipeline = dai.Pipeline()
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
rgb = pipeline.create(dai.node.ColorCamera)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
left.setBoardSocket(dai.CameraBoardSocket.LEFT)
right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
rgb.setPreviewSize(WIDTH, HEIGHT)
rgb.setInterleaved(False)
rgb.setFps(30)
out_rgb = pipeline.create(dai.node.XLinkOut)
out_depth = pipeline.create(dai.node.XLinkOut)
out_rgb.setStreamName('rgb')
out_depth.setStreamName('depth')
rgb.preview.link(out_rgb.input)
stereo.depth.link(out_depth.input)

try:
    device = dai.Device(pipeline)
except Exception as exc:
    err_root = tk.Tk(); err_root.title('相机距离测量'); tk.Label(err_root, text=f'未检测到相机或相机被占用：{exc}', padx=30, pady=20).pack(); tk.Button(err_root, text='关闭', command=err_root.destroy).pack(pady=(0,20)); err_root.mainloop(); raise SystemExit
rgb_q = device.getOutputQueue('rgb', maxSize=2, blocking=False)
depth_q = device.getOutputQueue('depth', maxSize=2, blocking=False)
cal = device.readCalibration()
intr = cal.getCameraIntrinsics(dai.CameraBoardSocket.RGB, WIDTH, HEIGHT)
fx, fy, cx, cy = intr[0][0], intr[1][1], intr[0][2], intr[1][2]

root = tk.Tk()
root.title('相机距离测量')
root.resizable(False, False)
selected = None
latest = None
last_measurement = None
image_ref = None

bar = tk.Frame(root)
bar.pack(fill='x', padx=8, pady=8)
tk.Label(bar, text='实际距离(mm)').pack(side='left')
actual_var = tk.StringVar(value='1500')
tk.Entry(bar, textvariable=actual_var, width=10).pack(side='left', padx=6)
status_var = tk.StringVar(value='请在画面中单击物体')
tk.Label(root, textvariable=status_var, anchor='w').pack(fill='x', padx=8)
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0)
canvas.pack(padx=8, pady=6)
canvas_image = canvas.create_image(0, 0, anchor='nw')
buttons = tk.Frame(root)
buttons.pack(fill='x', padx=8, pady=(0, 8))
tk.Button(buttons, text='保存当前记录', command=lambda: save_record()).pack(side='left')
tk.Button(buttons, text='清除选择', command=lambda: clear_selection()).pack(side='left', padx=8)
tk.Button(buttons, text='退出', command=root.destroy).pack(side='right')


def actual_value():
    try:
        v = float(actual_var.get())
        return v if v > 0 else None
    except ValueError:
        return None


def click(event):
    global selected
    selected = (max(0, min(WIDTH - 1, event.x)), max(0, min(HEIGHT - 1, event.y)))
    status_var.set(f'已选择像素 ({selected[0]}, {selected[1]})，正在测量')


def clear_selection():
    global selected, last_measurement
    selected = None
    last_measurement = None
    status_var.set('请在画面中单击物体')


def save_record():
    if last_measurement is None:
        messagebox.showinfo('提示', '请先单击物体并等待测量值出现')
        return
    actual = actual_value()
    if actual is None:
        messagebox.showerror('输入错误', '实际距离必须是大于 0 的数字')
        return
    row = [time.strftime('%Y-%m-%d %H:%M:%S'), *last_measurement[:4], f'{actual:.2f}', f'{last_measurement[4]-actual:.2f}', f'{abs(last_measurement[4]-actual):.2f}']
    new_file = not os.path.exists(SAVE_PATH) or os.path.getsize(SAVE_PATH) == 0
    with open(SAVE_PATH, 'a', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(['时间','像素X','像素Y','深度Z_mm','测量距离_mm','实际距离_mm','误差_mm','绝对误差_mm'])
        w.writerow(row)
    status_var.set(f'已保存：测量 {last_measurement[4]:.0f} mm，误差 {last_measurement[4]-actual:+.0f} mm')


def update():
    global latest, image_ref, last_measurement
    packet = rgb_q.tryGet()
    depth_packet = depth_q.tryGet()
    if packet is not None and depth_packet is not None:
        frame = packet.getCvFrame()
        depth = depth_packet.getFrame()
        if selected is not None:
            x, y = selected
            roi = depth[max(0, y-4):min(HEIGHT, y+5), max(0, x-4):min(WIDTH, x+5)]
            valid = roi[(roi > 0) & (roi < 30000)]
            if valid.size:
                z = float(np.median(valid))
                xx, yy = (x-cx)*z/fx, (y-cy)*z/fy
                distance = float(np.sqrt(xx*xx + yy*yy + z*z))
                last_measurement = (x, y, z, distance, distance)
                actual = actual_value()
                err_text = f'，误差 {distance-actual:+.0f} mm' if actual else ''
                status_var.set(f'测量距离 {distance:.0f} mm，深度 {z:.0f} mm{err_text}')
                cv2.drawMarker(frame, (x, y), (0, 255, 0), cv2.MARKER_CROSS, 24, 2)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_ref = ImageTk.PhotoImage(Image.fromarray(rgb))
        canvas.itemconfig(canvas_image, image=image_ref)
    root.after(30, update)

canvas.bind('<Button-1>', click)
root.protocol('WM_DELETE_WINDOW', root.destroy)
root.after(30, update)
root.mainloop()
device.close()

