#!/usr/bin/env python3

# A proof of concept spline drawing and exporting app

import sys
import random
import functools
import json
from dataclasses import dataclass


from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDesktopWidget


@dataclass
class Point:
    x : float
    y : float

def ExportToJson(ControlPoints, ScreenWidth, ScreenHeight):
    
    data = {}
    data['points'] = []

    for Point in ControlPoints:
        x = (Point[0] - ControlPoints[0][0]) / ScreenWidth
        y = (Point[1] - ControlPoints[0][1]) / ScreenHeight
        data['points'].append({'x' : x, 'y' : y})

    with open('ControlPoints.json', 'w') as outfile:
        json.dump(data, outfile)


@functools.lru_cache(maxsize=100)
def factorial(n):
    prod = 1
    for i in range(1,n+1):
        prod *= i
    return prod

def randPt(minv, maxv):
    return (random.randint(minv, maxv), random.randint(minv, maxv))

def B(i,n,u):
    val = factorial(n)/(factorial(i)*factorial(n-i))
    return val * (u**i) * ((1-u)**(n-i))

def C(u, pts):
    x = 0
    y = 0
    n = len(pts)-1
    for i in range(n+1):
        binu = B(i,n,u)
        x += binu * pts[i][0]
        y += binu * pts[i][1]
    return (x, y)

class BezierDrawer(QtWidgets.QMainWindow):
  
    def __init__(self):
        super(BezierDrawer, self).__init__()

        self.setGeometry(0, 0, 1080, 720)
        self.setWindowTitle('Spline tool')
        self.controlPts = [] # [(100,100), (600,100), (600,600), (100,600)]
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHints(QtGui.QPainter.Antialiasing, True)
        self.doDrawing(qp)        
        qp.end()
        
    def doDrawing(self, qp):
        blackPen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        redPen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        greenPen = QtGui.QPen(QtCore.Qt.green, 1, QtCore.Qt.DashLine)
        redBrush = QtGui.QBrush(QtCore.Qt.red)

        steps = 600
        min_t = 0.0
        max_t = 1.0

        dt = (max_t - min_t)/steps
        # controlPts = [randPt(0,1000) for i in range(6)]
        # controlPts.append(controlPts[1])
        # controlPts.append(controlPts[0])
        if(len(self.controlPts)):
            oldPt = self.controlPts[0]
            pn = 1
            qp.setPen(redPen)
            qp.setBrush(redBrush)
            qp.drawEllipse(oldPt[0]-3, oldPt[1]-3, 6,6)

            qp.drawText(oldPt[0]+5, oldPt[1]-3, '{}'.format(pn))
            for pt in self.controlPts[1:]:
                pn+=1
                qp.setPen(blackPen)
                qp.drawLine(oldPt[0],oldPt[1],pt[0],pt[1])

                qp.setPen(redPen)
                qp.drawEllipse(pt[0]-3, pt[1]-3, 6,6)

                qp.drawText(pt[0]+5, pt[1]-3, '{}'.format(pn))
                oldPt = pt

            qp.setPen(bluePen)
            oldPt = self.controlPts[0]
            for i in range(steps+1):
                t = dt*i
                pt = C(t, self.controlPts)
                qp.drawLine(oldPt[0],oldPt[1], pt[0],pt[1])
                oldPt = pt
        self.update()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.buttons() == QtCore.Qt.LeftButton:
                position = event.pos()
                if(position.x() in self.controlPts or position.y() in self.controlPts):
                    return 1
                else:
                    self.controlPts.append([position.x(), position.y()])
                    return 1
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Control:
                ExportToJson(self.controlPts, self.width(), self.height())
            

        return super().eventFilter(source, event)

app = QtWidgets.QApplication(sys.argv)
ex = BezierDrawer()
ex.show()
app.installEventFilter(ex)
app.exec_()
