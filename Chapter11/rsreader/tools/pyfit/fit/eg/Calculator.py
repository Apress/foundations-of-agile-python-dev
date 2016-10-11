"""
Python translation of fit..
which is copyright (c) 2002 Cunningham & Cunningham, Inc.
Released under the terms of the GNU General Public License version 2 or later.
"""

import math
from types import *
from fit.ColumnFixture import ColumnFixture

class _HP35:
    r = [0.0, 0.0, 0.0, 0.0]
    s = 0.0
    flash = False

    def key(self,key):
        # added for python auto-parsing variant: let key be a number
        self.flash = False
        if (type(key) in (IntType, LongType, FloatType, ComplexType) or
            self.numeric(key)):self.push(float(key))
        elif key=="enter":   self.push()
        elif key=="+":       self.push(self.pop()+self.pop())
        elif key=="-":       t=self.pop(); self.push(self.pop()-t)
        elif key=="*":       self.push(self.pop()*self.pop())
        elif key=="/":
            try:
                t=self.pop()
                self.push(self.pop()/t)
            except ZeroDivisionError:
                self.flash = True
                raise
        elif key=="x^y":     self.push(math.exp(math.log(self.pop())*\
                                                self.pop()))
        elif key=="clx":     self.r[0]=0
        elif key=="clr":     self.r[0]=self.r[1]=self.r[2]=self.r[3]=0
        elif key=="chs":     self.r[0]=-self.r[0]
        elif key=="x<>y":    t=self.r[0]; self.r[0]=self.r[1]; self.r[1]=t
        elif key=="r!":      self.r[3]=self.pop()
        elif key=="sto":     self.s=self.r[0]
        elif key=="rcl":     self.push(self.s)
        elif key=="sqrt":    self.push(math.sqrt(self.pop()))
        elif key=="ln":      self.push(math.log(self.pop()))
#            elif key=="sin":     self.push(math.sin(math.toRadians(self.pop())))
#            elif key=="cos":     self.push(Math.cos(Math.toRadians(self.pop())))
        elif key=="sin":     self.push(math.sin(self.pop()*math.pi/180))
        elif key=="cos":     self.push(math.cos(self.pop()*math.pi/180))
        elif key=="tan":     self.push(math.tan(self.pop()))
        else: raise Exception("can't do key: "+key)

    def numeric(self, key):
        return (len(key) >= 1 and
                (key[0].isdigit() or
                 (len(key) >= 2 and key[0] == '-' and key[1].isdigit())))

    def push(self, value=None):
        for i in (3,2,1):
            self.r[i] = self.r[i-1]
        if value != None:
            self.r[0] = value

    def pop(self):
        result = self.r[0]
        for i in (0,1,2):
            self.r[i] = self.r[i+1]
        return result

class Calculator(ColumnFixture):
    volts = 0.0
    key = ''
    hp = _HP35()

    _typeDict = {"volts": "Float", "key": "String"}    

    _typeDict["points"] = "Boolean"
    def points(self):
        return 0

    _typeDict["flash"] = "Boolean"
    def flash(self):
        return self.hp.flash

    _typeDict["watts"] = "Float"
    def watts(self):
        return 0.5

    _typeDict["x"] = "Float"
    _typeDict["x.precision"] = 4
    def x(self):
        self.hp.key(self.key)
        return self.hp.r[0]

    _typeDict["y"] = "Float"
    _typeDict["y.precision"] = 4
    def y(self):
        return self.hp.r[1]

    _typeDict["z"] = "Float"
    _typeDict["z.precision"] = 4
    def z(self):
        return self.hp.r[2]

    _typeDict["t"] = "Float"
    _typeDict["t.precision"] = 4
    def t(self):
        return self.hp.r[3]
