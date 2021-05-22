import json
# import pandas as pd
import re
from datetime import date, datetime

def date_reader(my_date):
    temp = datetime.strptime(my_date, "%Y-%m-%d")
    return date.strftime(temp, "%a, %d %b %Y")


prize_structure = {"[3, 0]": 7,
                   "[3, 1]": 6,
                   "[4, 0]": 5,
                   "[4, 1]": 4,
                   "[5, 0]": 3,
                   "[5, 1]": 2,
                   "[6, 0]": 1}


try:
    with open("data.txt") as file:
       results = json.load(file)
except:
    results = {}
    print("No results found")

# test values
# ticket_date = date_reader("2021-04-29")
# test_numbers = [2, 19, 22, 30, 31, 32, 5]

def calculate_winnings(input_date, input_numbers):
    """Calculate winnings for given input_date and input_numbers"""
    ticket_date = date_reader(input_date)
    input_numbers = [int(i) for i in input_numbers]
    
    winning_numbers = results.get(ticket_date)["winning_numbers"]
    winning_numbers = [int(i) for i in winning_numbers]
    additional = results.get(ticket_date)["additional_number"]
    additional = [int(i) for i in additional]
    
    ticket_win_group = [len(set(input_numbers) & set(winning_numbers)),
                        len((set(input_numbers) & set(additional)))]
    #returns ([# matches winning numbers, # matches addl number], # win group)
    return (ticket_win_group, prize_structure.get(str(ticket_win_group)))
