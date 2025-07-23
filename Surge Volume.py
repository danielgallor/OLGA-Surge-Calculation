import pandas as pd
import numpy as np
import pyfas as fa
import json

with open('main.json', 'r') as file:
    readjson = json.load(file)

working_location = readjson.get('Working Location')   
cases = readjson.get('Cases')
model_inputs = readjson.get("Model Inputs")


tpl = [fa.Tpl(f"{working_location}\\{case}.tpl") for case in cases]

def variables_index():
    indexes = {}
    if model_inputs['Pipe']:
        filtered_QLTWT = list(tpl[0].filter_trends('QLTWT ').items())
        for item in filtered_QLTWT:
            values = item[1].split("'")
            if values[0] == 'QLTWT ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate water'] = item [0]

        filtered_QLTHL = list(tpl[0].filter_trends('QLTHL ').items())
        for item in filtered_QLTHL:
            values = item[1].split("'")
            if values[0] == 'QLTHL ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate oil'] = item [0]
    elif model_inputs['Position']:
        filtered_QLTWT = list(tpl[0].filter_trends('POSITION:').items())
        for item in filtered_QLTWT:
            values = item[1].split("'")
            if values[0] == 'QLTWT ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate water'] = item [0]

        filtered_QLTHL = list(tpl[0].filter_trends('QLTHL ').items())
        for item in filtered_QLTHL:
            values = item[1].split("'")
            if values[0] == 'QLTHL ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate oil'] = item [0]



    return indexes
indexes = variables_index()


tpl.extract(indexes)




a=5