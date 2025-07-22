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

a=5