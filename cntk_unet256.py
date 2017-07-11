# -*- coding: utf8 -*-
import numpy as np
import sys
import os
import cntk as C
import cntk
from cntk.layers import Convolution, MaxPooling, Dense
from cntk.initializer import glorot_uniform
from cntk.ops import relu, sigmoid, input_variable

from cntk.io import transforms


# https://github.com/usuyama/cntk_unet/blob/master/cntk_unet.py

# https://stackoverflow.com/questions/43079648/cntk-how-to-define-upsampling2d
def UpSampling2D(x):
    xr = C.reshape(x, (x.shape[0], x.shape[1], 1, x.shape[2], 1))
    xx = C.splice(xr, xr, axis=-1)  # axis=-1 refers to the last axis
    xy = C.splice(xx, xx, axis=-3)  # axis=-3 refers to the middle axis
    r = C.reshape(xy, (x.shape[0], x.shape[1] * 2, x.shape[2] * 2))
    '''
    print ("upsampling")
    print(xr.shape)
    print(xx.shape)
    print(xy.shape)
    print(r.shape)
    '''
    return r


def create_model(input):
    # print (input.shape)
    conv1 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(input)
    conv1 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(conv1)
    pool1 = MaxPooling((2, 2), strides=(2, 2))(conv1)

    conv2 = Convolution((3, 3), 128, init=glorot_uniform(), activation=relu, pad=True)(pool1)
    conv2 = Convolution((3, 3), 128, init=glorot_uniform(), activation=relu, pad=True)(conv2)
    pool2 = MaxPooling((2, 2), strides=(2, 2))(conv2)

    conv3 = Convolution((3, 3), 256, init=glorot_uniform(), activation=relu, pad=True)(pool2)
    conv3 = Convolution((3, 3), 256, init=glorot_uniform(), activation=relu, pad=True)(conv3)

    up8 = C.splice(UpSampling2D(conv3), conv2, axis=0)
    conv8 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(up8)
    conv8 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(conv8)

    up9 = C.splice(UpSampling2D(conv8), conv1, axis=0)
    conv9 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(up9)
    conv9 = Convolution((3, 3), 64, init=glorot_uniform(), activation=relu, pad=True)(conv9)

    conv10 = Convolution((1, 1), 1, init=glorot_uniform(), activation=sigmoid, pad=True)(conv9)

    print("conv1" + str(conv1.shape))
    print("pool1" + str(pool1.shape))
    print("conv2" + str(conv2.shape))
    print("pool2" + str(pool2.shape))
    print("conv3" + str(conv3.shape))
    print("conv8" + str(conv8.shape))
    print("up9" + str(up9.shape))
    print("conv9" + str(conv9.shape))
    print("conv10" + str(conv10.shape))

    return conv10


def dice_coefficient(x, y):
    # https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient
    intersection = C.reduce_sum(x * y)

    return 2 * intersection / (C.reduce_sum(x) + C.reduce_sum(y))


