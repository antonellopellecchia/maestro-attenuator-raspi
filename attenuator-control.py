#!/usr/bin/python3

import os, sys
import argparse

import maestro

ATT_MIN, ATT_MAX = 0.095255*100, 0.888113*100 # attenuator linearity range
CONSTANT, OFFSET = 7.20779e-04, -3.83299e+00 # servo calibration parameters

def CalculateServoPosition(attenuation):
    return int((attenuation-OFFSET)/CONSTANT)

def CalculateAttenuation(servoPosition):
    return CONSTANT*servoPosition+OFFSET

class AttenuatorController:

    def __init__(self, port=None, servoDevice=0, speed=5, accel=1):
        if port is None: self.servo = maestro.Controller() # Unix
        else: self.servo = maestro.Controller('COM'+port) # Windows
        self.servoDevice = servoDevice
        self.servo.setSpeed(servoDevice,speed)
        self.servo.setAccel(servoDevice,accel)

    def SetAttenuation(self, attenuationPerCent):
        servoPosition = CalculateServoPosition(attenuationPerCent/100)
        self.SetServo(servoPosition)

    def GetAttenuation(self):
        servoPosition = self.servo.getPosition(self.servoDevice)
        return CalculateAttenuation(servoPosition)

    def SetServo(self, servoPosition):
        self.servo.setTarget(self.servoDevice,servoPosition)

    def GetServo(self):
        return self.servo.getPosition(self.servoDevice)

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--port', type=int)
    ap.add_argument('--fullrange', action='store_true')
    options = ap.parse_args(sys.argv[1:])

    cmdlist = 'set get set-servo get-servo quit'

    if options.fullrange: attMin, attMax = -100, 100
    else: attMin, attMax = ATT_MIN, ATT_MAX

    print('Attenuator control')
    if options.port:
        controller = AttenuatorController(str(options.port))
        print('Controller connected on port', options.port)
    else:
        controller = AttenuatorController()
        print('Controller connected')

    while True:
        try:
            line = input('>>> ')
            commandWords = line.split(' ')
            command = commandWords[0]

            if command=='set':
                try: attenuationValue = float(commandWords[1])
                except (IndexError, ValueError):
                    print('Usage: set [attenuation]')
                    continue
                if attenuationValue==0.0:
                    controller.SetServo(5100) # not really zero, but close
                elif attenuationValue<attMin or attenuationValue>attMax:
                    print('Error: attenuation value outside linearity range')
                    continue
                else: controller.SetAttenuation(attenuationValue)
            elif command=='get': print('%1.2f%%'%(controller.GetAttenuation()*100))
            elif command=='set-servo':
                try: servoPosition = int(commandWords[1])
                except (IndexError, ValueError):
                    print('Usage: set-servo [position]')
                    continue
                controller.SetServo(servoPosition)
            elif command=='get-servo': print('%d'%(controller.GetServo()))
            elif command=='quit': break
            else:
                print('Commands:', cmdlist)
        except (EOFError,KeyboardInterrupt): break
    print('')

if __name__=='__main__': main()
