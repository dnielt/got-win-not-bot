import cv2
import pytesseract
import os
import re
from image_preprocessing import (
    get_grayscale,
    thresholding,
    opening,
    canny)

os.chdir("images")
files = os.listdir()
results = {}

for i, file in enumerate(files):
    #print(f"in {i}")
    image = cv2.imread(file)
    #gray = get_grayscale(image)
    open_img = opening(image)
    results[i] = {"text": pytesseract.image_to_string(open_img)}



actual = {
    0: [[1, 21, 23, 28, 29, 38, 45], 
        [10, 15, 21, 23, 24, 40, 43]],
    1: [[5, 17, 20, 36, 40, 41],
        [4, 5, 17, 26, 30, 44],
        [4, 8, 9, 32, 37, 45],
        [5, 9, 14, 20, 25, 36],
        [17, 22, 24, 30, 33, 41],
        [6, 26, 30, 31, 40, 42]],
    2: [[15, 18, 25, 39, 46, 49],
        [3, 13, 26, 38, 39, 41],
        [28, 32, 36, 38, 46, 47],
        [1, 3, 4, 5, 40, 47],
        [9, 15, 22, 28, 31, 36],
        [1, 13, 25, 39, 44, 45]],
    3: [[1, 3, 4, 11, 38, 41],
        [4, 10, 20, 28, 45, 48],
        [2, 17, 20, 32, 34, 48],
        [7, 23, 30, 32, 43, 48],
        [2, 3, 4, 15, 28, 47],
        [3, 9, 14, 25, 29, 31]],
    4: [[4, 7, 22, 24, 41, 42],
        [27, 35, 37, 41, 45, 46],
        [3, 9, 10, 22, 33, 48],
        [4, 7, 17, 23, 37, 49],
        [7, 9, 17, 24, 26, 44]],
    5: [[3, 6, 10, 28, 39, 48],
        [3, 18, 22, 31, 38, 39]],
    6: [[13, 19, 20, 26, 30, 37],
        [4, 6, 8, 27, 34, 48],
        [10, 25, 27, 32, 38, 43],
        [8, 14, 15, 28, 33, 42],
        [8, 17, 21, 35, 39, 41],
        [3, 8, 14, 28, 31, 38]],
    7: [[2, 11, 15, 32, 39, 47],
        [2, 3, 14, 27, 32, 48],
        [15, 17, 30, 33, 35, 44],
        [1, 6, 15, 25, 32, 43],
        [19, 28, 32, 39, 41, 42]],
    8: [[10, 11, 12, 26, 34, 48],
        [9, 21, 26, 28, 34, 49],
        [7, 21, 28, 29, 32, 46],
        [7, 8, 10, 15, 27, 41],
        [10, 12, 33, 37, 39, 44],
        [3, 5, 12, 22, 24, 46]]
    }

