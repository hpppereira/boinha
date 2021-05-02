# -*- coding: utf-8 -*-
import numpy as np
from scipy.integrate import cumtrapz
import pandas as pd
import math

def accZ2accV (accX, accY, accZ, roll, pitch):
    accV = (accX*np.sin(pitch)) + (accY * (np.sin(roll)*np.cos(pitch))) + (accZ * (np.cos(roll)*np.cos(pitch)))
    return accV


def acc2heave (accX, accY, accZ, roll, pitch, yaw, dt):

    # Filtrar sinais - retirar ruido

    # rad 2 degrees

    # Retirar gravidade - tirar média
    accX = accX - accX.mean()
    accY = accY - accX.mean()
    accZ = accZ - accX.mean()

    # AccZ 2 Acc Vertical
    accV = accZ2accV(accX, accY, accZ, roll, pitch)
    # Integral AccV -> Heave

    # Filtrar accV
    # cumpraz accV -> velZ
    velZ = cumtrapz(accV, dx=dt)
    # cumpraz velZ -> heave
    heave = cumtrapz(velZ, dx=dt)

    return accX, accY, accZ, accV, velZ, heave


