#!/usr/bin/python3

import os, sys
import argparse

import numpy as np
import ROOT as rt
import pandas as pd

from physlibs.root import root_style_cms

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('-b', action='store_true', help='ROOT batch mode')
    options = ap.parse_args(sys.argv[1:])

    attenuations = np.linspace(10, 100, 10)
    servoPositionsMaestro = np.array([1375, 1413.50, 1444.75, 1472.75, 1500, 1527, 1555, 1586.25, 1624.25, 1710.50])

    maestroCalibrationPlot = rt.TGraph(len(attenuations), servoPositionsMaestro, attenuations)
    maestroCalibrationCanvas = rt.TCanvas('MaestroCalibrationCanvas', '', 800, 600)
    maestroCalibrationPlot.SetTitle(';Servo position (a.u.);Attenuation (%)')
    maestroCalibrationPlot.Draw('AP')
    maestroCalibrationCanvas.SaveAs('plots/MaestroCalibration.eps')

if __name__=='__main__': main()
