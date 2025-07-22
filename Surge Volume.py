import pandas as pd
import numpy as np
import pyfas as fa
import json

with open('main.json', 'r') as file:
    readjson = json.load(file)

working_location = readjson.get('Working Location')   
cases = readjson.get('Cases')
branch = readjson.get('Branches') 

tpl = [fa.Tpl(f"{working_location}\\{case}.tpl") for case in cases]

def variables_index():
    indexes = {}
    filtered_tpl = list(tpl[0].filter_trends('QLTWT ').items())
    for item in filtered_tpl:
        values = item[1].split("'")
        if values[0] == 'QLTWT ' and values[5] == branch.upper():
            indexes[f"{values[17]}"] = item [0]

    return indexes
indexes = variables_index()





a=5