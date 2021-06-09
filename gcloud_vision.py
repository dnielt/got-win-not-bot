import io
import os
import re
from datetime import datetime

# Imports the Google Cloud client library
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/mnt/c/users/daniel/desktop/2021-05-22 telegram bot - GWN/google-api-key/google-key.json"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./google-key.json"

def test():
    return read_image(
        "/mnt/c/users/daniel/desktop/"
        "2021-05-22 telegram bot - GWN/images/img10.jpg")

def read_image(path_to_file):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    
    # The name of the image file to annotate
    # file_name = os.path.abspath(
        # "/mnt/c/users/daniel/desktop/"
        # "2021-05-22 telegram bot - GWN/images/img10.jpg")
    
    file_name = os.path.abspath(path_to_file)
    
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # Performs label detection on the image file
    response = client.text_detection(image=image)
    text = response.text_annotations

    #Isolate whole text, which is stored in text[0]
    temp = text[0].description
    lines = temp.split("\n")
    
    result = []
    date = []
    
    for line in lines:
        #Find relevant rows with at least 5 sets of XX characters
        if re.findall("([0-9]{2} ){5,}", line):
            result.append(line)
        #Find draw date
        elif re.findall("(DRAW: [A-Z]{3} ([0-9]{2}\/[0-9]{2}\/[0-9]{2}))", line):
            date.append(line)
    
    result2 = []
    for string in result:
        result2.append(re.sub("(^[A-Za-z][\.-]( )?)", "", string))
    result3 = "\n".join(result2)

    try:
        date = re.sub("[^0-9\/]", "", date[0])
        date = datetime.strptime(date, "%d/%m/%y")
        date = date.strftime("%Y-%m-%d")
    except:
        date = None
    
    return {"date": date, "result": result, "parsed": result3}


def parse_raw_numbers(ticket_numbers):
    """
    Parse string of text, into list/list of lists of ticket numbers
    "1 2 3 4 5 6\n1 2 3 4 5 6" into
    [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]]
    """
    #if there are multiple lines in the raw text, then split the list
    if re.findall("\n", ticket_numbers):
        ticket_numbers = re.split("\n", ticket_numbers)
        ticket_numbers = [re.split(" ", i) for i in ticket_numbers]
    
    #if only a single line, no need to split the string
    else:
        ticket_numbers = re.split(" ", ticket_numbers)
    
    return ticket_numbers