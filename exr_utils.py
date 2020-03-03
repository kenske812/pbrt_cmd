# coding: utf-8

import OpenEXR, array
import Imath
import numpy as np


def exr2array(fname):
    """.exr to RGB numpy array whose shape is (3, h, w)"""
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    file = OpenEXR.InputFile(str(fname))
    dw = file.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    ch_strs = [file.channel(ch, pt) for ch in ['R','G', 'B']]
    rgb = [np.fromstring(ch_str, dtype = np.float32).reshape(size[1], size[0]) for ch_str in ch_strs]
    
    return np.array(rgb)


def write_rgb_array(fname, rgb_img):
    """
    write numpy array to exr file.
    Args:
        fname (Path or string): output filename.
        rgb_img (numpy.array): the shape should be (ch, h, w).
                               the channel should be 'r', 'g', 'b' order.
                               dtype must be float32 for now. 
    """
    if rgb_img.dtype != np.float32:
        raise TypeError("input image should be np.float32")
    
    n_ch, h, w = rgb_img.shape
    exr = OpenEXR.OutputFile(str(fname), OpenEXR.Header(w, h))

    channels = ['R', 'G', 'B']
    data = {ch: img.reshape(-1).tostring() 
                     for ch, img in zip(channels, rgb_img)}

    exr.writePixels(data)
    


def write_test():
    fname = "exr_write_test.exr"
    rgb = np.zeros((3, 480, 640)).astype(np.float32)
    rgb[0, :, :] = 1
    rgb[1, :10, :] = 1
    rgb[2, :, 10:20] = 1
    write_rgb_array(fname, rgb)

if __name__ == "__main__":
    write_test()

