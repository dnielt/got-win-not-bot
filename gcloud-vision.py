import io
import os
import re
from datetime import datetime

# Imports the Google Cloud client library
from google.cloud import vision

# export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/users/daniel/desktop/2021-05-22 telegram bot - GWN/google-api-key/google-key.json"

# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.abspath(
    "/mnt/c/users/daniel/desktop/"
    "2021-05-22 telegram bot - GWN/images/img10.jpg")

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Performs label detection on the image file
response = client.text_detection(image=image)
text = response.text_annotations

# print('Text:')
# for i in text:
    # print(i.description)

test = text[0].description
lines = test.split("\n")

result = []
date = []

for line in lines:
    if re.findall("([0-9]{2} ){5,}", line):
        result.append(line)
    elif re.findall("(DRAW: [A-Z]{3} ([0-9]{2}\/[0-9]{2}\/[0-9]{2}))", line):
        date.append(line)

result
"""
['A. 03 12 27 44 45 49', 'B.01 06 11 21 30 34', 'C. 19 23 24 26 31 44', 'D.02 04 17 29 32 43', 'E. 05 10 13 21 36 46', 'F. 03 09 11 15 17 37'] 
into
"03 12 27 \n12 12 31"
"""
result2 = []
for string in result:
    result2.append(re.sub("(^[A-Z]\.( )?)", "", string))
result3 = "\n".join(result2)
# test_numbers = [2, 19, 22, 30, 31, 32, 5]


date
#['DRAW: THU 20/05/21']
# ticket_date = date_reader("2021-04-29")
date = re.sub("[^0-9\/]", "", date[0])
date = datetime.strptime(date, "%d/%m/%y")
date = date.strftime("%Y-%m-%d")