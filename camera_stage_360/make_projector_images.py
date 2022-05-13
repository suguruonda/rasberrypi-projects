import numpy as np
import math
from PIL import Image

pixels = 433
hd_pixels = (1080,1920)
img_num = math.ceil(math.log(pixels,2))
x = np.zeros((pixels,pixels,3))
y = np.zeros((pixels,pixels,3))
canvas = np.zeros((hd_pixels[0],hd_pixels[1],3))
for i in range(img_num):
    for j in range(pixels):
        val = ((j >> i) & 1) * 255
        x[:,j,:] = [val, 0, 0]
        y[j,:,:] = [val, 0, 0]
    x_p = hd_pixels[0]//2-pixels//2
    y_p = hd_pixels[1]//2-pixels//2
    canvas[x_p:x_p + pixels,y_p:y_p + pixels] = x
    x_img = Image.fromarray(canvas.astype(np.uint8))    
    canvas[x_p:x_p + pixels,y_p:y_p + pixels] = y
    y_img = Image.fromarray(canvas.astype(np.uint8)) 
    x_img.save("x_" + str(i) + ".png")   
    y_img.save("y_" + str(i) + ".png")   
