#!/usr/bin/python3

import os, sys
import numpy as np
import ROOT as rt
import pandas as pd
import argparse
import time, datetime
import re

import scope
from physlibs.root import root_style_ftm
from physlibs.root import functions

def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--input')
    ap.add_argument('--cache')
    ap.add_argument('--output')
    ap.add_argument('-b', help='Ignored', action='store_true')
    options = ap.parse_args(sys.argv[1:])

    for d in [options.output, options.output+'/ChargeSpectra/']:
        try: os.makedirs(d)
        except FileExistsError: pass

    if options.input:
        cacheDict = { 'step':list(), 'charge':list(), 'error':list() }

        signalDirectories = sorted(os.listdir(options.input))
        for indexPosition,signalDirectory in enumerate(signalDirectories):
            servoPosition = float(signalDirectory)
            servoPositionDirectory = '%s/%s/'%(options.input, signalDirectory)
            print('Servo position', servoPosition)

            servoPositionFiles = os.listdir(servoPositionDirectory)
            chargeSpectrum = rt.TH1F('h'+str(servoPosition), ';Charge (pC);', 100, 0, 50)
            for signalFile in servoPositionFiles:
                signalFilePath = servoPositionDirectory+'/'+signalFile
                scopeSignal = scope.ScopeSignal(signalFilePath)
                try: scopeSignal.ReadSignal()
                except:
                    print('Skipping', signalFile)
                    continue
                charge = scopeSignal.GetChargeBetween(-20, 40)
                chargeSpectrum.Fill(charge)
            chargeCanvas = rt.TCanvas('ChargeCanvas'+str(servoPosition), '', 800, 600)
            chargeSpectrum.Draw()
            chargeCanvas.SaveAs('%s/ChargeSpectra/%s.eps'%(options.output,servoPosition))

            charge = chargeSpectrum.GetMean()
            chargeError = chargeSpectrum.GetRMS()/(chargeSpectrum.GetEntries())**0.5
            calibrationPlot.SetPoint(indexPosition, servoPosition, charge)
            calibrationPlot.SetPointError(indexPosition, 0, chargeError)

            cacheDict['step'].append(servoPosition)
            cacheDict['charge'].append(charge)
            cacheDict['error'].append(chargeError)

        cacheDict['step'] = np.array(cacheDict['step'])
        cacheDict['charge'] = np.array(cacheDict['charge'])
        cacheDict['error'] = np.array(cacheDict['error'])
        cacheDf = pd.DataFrame.from_dict(cacheDict)
        cacheDf.to_csv('cache.csv')

    elif options.cache:
        cacheDf = pd.read_csv(options.cache, index_col=0, dtype='float64')
        cacheDict = dict(cacheDf)

    npoints = len(cacheDict['step'])
    chargePlot = rt.TGraphErrors(npoints,
        np.array(cacheDict['step']), np.array(cacheDict['charge']),
        np.zeros(npoints), np.array(cacheDict['error']))
    chargeCanvas = rt.TCanvas('ChargeCanvas', '', 800, 600)
    chargePlot.SetTitle(';Servo position;APD charge (pWb)')
    #fitSigmoid = functions.GetSigmoid(6300, 7000, 2000, 50, 6000, 0)
    fitSaturation = rt.TF1('f', '[0]+[1]/(x-[2])', 6450, 7000)
    fitSaturation.SetParameters(2000, 1)
    chargePlot.Draw('AP')
    chargePlot.Fit(fitSaturation, 'R')
    chargeMax = fitSaturation.GetParameter(0)
    chargeCanvas.Update()
    chargeCanvas.Draw()
    fitBox = chargePlot.FindObject('stats')
    fitBox.SetTextColor(rt.kRed+2)
    fitBox.SetX1NDC(0.2)
    fitBox.SetY1NDC(0.75)
    fitBox.SetX2NDC(0.5)
    fitBox.SetY2NDC(0.9)
    chargeCanvas.SaveAs('%s/Charge.eps'%(options.output))


    stepMin = 5450
    stepMax = 6550 # highest point for fit
    #chargeMax = cacheDict['charge'][-5:].mean() # unused, recovered from previous fit instead
    pol = rt.TF1('p', '[0]+[1]*x', stepMin, stepMax)
    #pol = rt.TF1('p', '[0]+[1]*x', stepMin, stepMax)
    pol.SetParameters(-4, 7e-4)
    attenuation = np.array(cacheDict['charge']/chargeMax)
    attenuationError = np.array(cacheDict['error']/chargeMax)

    calibrationPlot = rt.TGraphErrors(npoints,
        np.array(cacheDict['step']), attenuation,
        np.zeros(npoints), attenuationError)
    calibrationCanvas = rt.TCanvas('CalibrationCanvas', '', 800, 600)
    calibrationPlot.SetTitle(';Servo position;Attenuation')
    calibrationPlot.Draw('AP')
    calibrationPlot.Fit(pol, 'R')

    calibrationCanvas.Update()
    calibrationCanvas.Draw()
    fitBox = calibrationPlot.FindObject('stats')
    fitBox.SetTextColor(rt.kRed+2)
    fitBox.SetX1NDC(0.2)
    fitBox.SetY1NDC(0.75)
    fitBox.SetX2NDC(0.5)
    fitBox.SetY2NDC(0.9)

    attMinLinear = pol.Eval(stepMin)
    attMaxLinear = pol.Eval(stepMax)
    print('Attenuator is linear between attenuation %1f and %1f'%(attMinLinear, attMaxLinear))

    calibrationCanvas.SaveAs('%s/Calibration.eps'%(options.output))

if __name__=='__main__': main()