import itertools
import inspect
import image_preprocessing as ip
import cv2
import pytesseract
import os
import re
from image_reader import actual

# load images
os.chdir("/mnt/c/Users/Daniel/Desktop/2021-05-02 sg pools results/images")
files = os.listdir()
results = {}

for i, file in enumerate(files):
    #print(f"in {i}")
    image = cv2.imread(file)
    #gray = get_grayscale(image)
    open_img = ip.opening(image)
    results[i] = {"text": pytesseract.image_to_string(open_img)}

os.chdir("/mnt/c/Users/Daniel/Desktop/2021-05-02 sg pools results")

#################################################

# List of all functions in CV2 optimiser
func_list = [
    ip.get_grayscale,
    ip.thresholding,
    ip.opening,
    ip.canny,
    ip.remove_noise,
    ip.dilate,
    ip.erode,
    ip.deskew,
    ip.match_template
    ]

# create all combinations of optimisation functions
test = "abcde"
result = [list(itertools.combinations(test, i)) for i in range(len(test)+1)]
result = [list(itertools.combinations(func_list, i)) for i in range(len(func_list)+1)]

result2 = [i for element in result for i in element if i]

# create all permutations from all combinations
result3 = [list(itertools.permutations(i, len(i))) for i in result2]

#################################################

# use_funcs TEST
def multiply_two(i):
    return i*2

def add_three(i):
    return i+3

test_a = [multiply_two, add_three]

def use_funcs(list_of_funcs, start):
    result = start
    for i in list_of_funcs:
        result = i(result)
    return result

use_funcs(test_a, 3)

#################################################

# recording accuracy of each function
