#!/usr/bin/env python
# coding: utf-8

import numpy as np
import cv
from collections import deque
from flask import Flask, render_template, Response

app = Flask(__name__)

def setValues(x):
    print("")

def generate_frames(colorIndex, paintWindow, colors, kernel, bpoints, gpoints, rpoints, ypoints, blue_index, green_index, red_index, yellow_index):
    cap = cv.VideoCapture(0)

    while True:    
        ret, frame = cap.read()
    
        frame = cv.flip(frame, 1)
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        u_hue = cv.getTrackbarPos("Upper Hue", "Color detectors")
        u_saturation = cv.getTrackbarPos("Upper Saturation", "Color detectors")
        u_value = cv.getTrackbarPos("Upper Value", "Color detectors")
        l_hue = cv.getTrackbarPos("Lower Hue", "Color detectors")
        l_saturation = cv.getTrackbarPos("Lower Saturation", "Color detectors")
        l_value = cv.getTrackbarPos("Lower Value", "Color detectors")
        Upper_hsv = np.array([u_hue, u_saturation, u_value])
        Lower_hsv = np.array([l_hue, l_saturation, l_value])

        frame = cv.rectangle(frame, (40,1), (140,65), (122,122,122), -1)
        frame = cv.rectangle(frame, (160,1), (255,65), colors[0], -1)
        frame = cv.rectangle(frame, (275,1), (370,65), colors[1], -1)
        frame = cv.rectangle(frame, (390,1), (485,65), colors[2], -1)
        frame = cv.rectangle(frame, (505,1), (600,65), colors[3], -1)
        cv.putText(frame, "CLEAR ALL", (49, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, "BLUE", (185, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, "GREEN", (298, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, "RED", (420, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        cv.putText(frame, "YELLOW", (520, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv.LINE_AA)

        Mask = cv.inRange(hsv, Lower_hsv, Upper_hsv)
        Mask = cv.erode(Mask, kernel, iterations=1)
        Mask = cv.morphologyEx(Mask, cv.MORPH_OPEN, kernel)
        Mask = cv.dilate(Mask, kernel, iterations=1)

        cnts, _ = cv.findContours(Mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        center = None

        if len(cnts) > 0:
            cnt = sorted(cnts, key=cv.contourArea, reverse=True)[0]        
            ((x, y), radius) = cv.minEnclosingCircle(cnt)
            cv.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            M = cv.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            if center[1] <= 65:
                if 40 <= center[0] <= 140: 
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]

                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0

                    paintWindow[67:,:,:] = 255
                elif 160 <= center[0] <= 255:
                        colorIndex = 0 
                elif 275 <= center[0] <= 370:
                        colorIndex = 1 
                elif 390 <= center[0] <= 485:
                        colorIndex = 2 
                elif 505 <= center[0] <= 600:
                        colorIndex = 3 
            else:
                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
                elif colorIndex == 3:
                    ypoints[yellow_index].appendleft(center)
        else:
            bpoints.append(deque(maxlen=512))
            blue_index += 1
            gpoints.append(deque(maxlen=512))
            green_index += 1
            rpoints.append(deque(maxlen=512))
            red_index += 1
            ypoints.append(deque(maxlen=512))
            yellow_index += 1

        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                    cv.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

        cv.imshow("Tracking", frame)
        cv.imshow("Paint", paintWindow)
        cv.imshow("mask", Mask)

        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    print("inside video --------------")
    cv.namedWindow("Color detectors")
    cv.createTrackbar("Upper Hue", "Color detectors", 162, 180, setValues)
    cv.createTrackbar("Upper Saturation", "Color detectors", 255, 255, setValues)
    cv.createTrackbar("Upper Value", "Color detectors", 255, 255, setValues)
    cv.createTrackbar("Lower Hue", "Color detectors", 88, 180, setValues)
    cv.createTrackbar("Lower Saturation", "Color detectors", 108, 255, setValues)
    cv.createTrackbar("Lower Value", "Color detectors", 76, 255, setValues)

    bpoints = [deque(maxlen=1024)]
    gpoints = [deque(maxlen=1024)]
    rpoints = [deque(maxlen=1024)]
    ypoints = [deque(maxlen=1024)]

    blue_index = 0
    green_index = 0
    red_index = 0
    yellow_index = 0

    kernel = np.ones((5,5),np.uint8)

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0

    paintWindow = np.zeros((471,636,3)) + 255
    paintWindow = cv.rectangle(paintWindow, (40,1), (140,65), (0,0,0), 2)
    paintWindow = cv.rectangle(paintWindow, (160,1), (255,65), colors[0], -1)
    paintWindow = cv.rectangle(paintWindow, (275,1), (370,65), colors[1], -1)
    paintWindow = cv.rectangle(paintWindow, (390,1), (485,65), colors[2], -1)
    paintWindow = cv.rectangle(paintWindow, (505,1), (600,65), colors[3], -1)

    cv.putText(paintWindow, "CLEAR", (49, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv.LINE_AA)
    cv.putText(paintWindow, "BLUE", (185, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
    cv.putText(paintWindow, "GREEN", (298, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
    cv.putText(paintWindow, "RED", (420, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
    cv.putText(paintWindow, "YELLOW", (520, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 2, cv.LINE_AA)
    cv.namedWindow('Paint', cv.WINDOW_AUTOSIZE)

    cap = cv.VideoCapture(0)
    print("going to generate frames function")
    return Response(generate_frames(colorIndex, paintWindow, colors, kernel, bpoints, gpoints, rpoints, ypoints, blue_index, green_index, red_index, yellow_index), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    print("inside main")
    app.run()
