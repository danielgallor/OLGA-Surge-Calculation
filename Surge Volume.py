import pandas as pd
import numpy as np
import pyfas as fa
import json
import matplotlib.pyplot as plt

with open('main.json', 'r') as file:
    readjson = json.load(file)

working_location = readjson.get('Working Location')   
cases = readjson.get('Cases')
model_inputs = readjson.get("Model Inputs")
water_drain = readjson.get("Arrival Conditions")["Water Drain Rate (m3/h)"]
oil_drain = readjson.get("Arrival Conditions")["Oil Drain Rate (m3/h)"]


tpls = [fa.Tpl(f"{working_location}\\{case}.tpl") for case in cases]

def variables_index():
    indexes = {}
    if model_inputs['Pipe']:
        filtered_QLTWT = list(tpls[0].filter_trends('QLTWT ').items())
        for item in filtered_QLTWT:
            values = item[1].split("'")
            if values[0] == 'QLTWT ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate water'] = item [0]

        filtered_QLTHL = list(tpls[0].filter_trends('QLTHL ').items())
        for item in filtered_QLTHL:
            values = item[1].split("'")
            if values[0] == 'QLTHL ' and values[5] == model_inputs['Branch'].upper() and values[9] == model_inputs['Pipe'] and values[13] == model_inputs['Section']:
                indexes['Volumetric flow rate oil'] = item [0]
    elif model_inputs['Position']:
        filtered_QLTWT = list(tpls[0].filter_trends('POSITION:').items())
        for item in filtered_QLTWT:
            values = item[1].split("'")
            if values[0] == 'QLTWT ' and values[3] == model_inputs['Position']:
                indexes['Volumetric flow rate water'] = item [0]

        filtered_QLTHL = list(tpls[0].filter_trends('QLTHL ').items())
        for item in filtered_QLTHL:
            values = item[1].split("'")
            if values[0] == 'QLTHL ' and values[3] == model_inputs['Position']:
                indexes['Volumetric flow rate oil'] = item [0]



    return indexes
indexes = variables_index()

def extract_data(tpl):
    for fluid in  ['Volumetric flow rate water','Volumetric flow rate oil']:
        tpl.extract(indexes[fluid])
        if fluid == 'Volumetric flow rate water':
           QLTWT = tpl.data[indexes[fluid]]/3600
        else:
           QLTHL = tpl.data[indexes[fluid]]/3600

    return QLTWT,QLTHL


def organise_data(tpl):
    QLTWT, QLTHL = extract_data(tpl)
    time = tpl.time/3600
    trend_data = pd.DataFrame({"Time (h)": time, "Volumetric flow rate water (m3/h)": QLTWT/3600, "Water Drain Rate (m3/h)": water_drain})
    trend_data["Delta Time (h)"] = trend_data["Time (h)"] - trend_data["Time (h)"].shift(1)
    trend_data["Water Drained Flow"] =  trend_data["Volumetric flow rate water (m3/h)"] - trend_data["Water Drain Rate (m3/h)"]
    trend_data["Water Surge vol (m3)"] = trend_data["Delta Time (h)"] * trend_data["Water Drained Flow"]
    for i in range(len(trend_data)-1):
        if i == 0:
            trend_data["Water Cumm Surge (m3)"] = 0
        else:
            trend_data.loc[i, "Water Cumm Surge (m3)"] = np.where(trend_data["Water Surge vol (m3)"][i+1] + trend_data["Water Cumm Surge (m3)"][i] < 0, 0, trend_data["Water Surge vol (m3)"][i+1] + trend_data["Water Cumm Surge (m3)"][i])
    
    trend_data["Volumetric flow rate oil (m3/h)"] = QLTHL/3600
    trend_data["Oil Drain Rate (m3/h)"] = oil_drain
    trend_data["Oil Drained Flow"] =  trend_data["Volumetric flow rate oil (m3/h)"] - trend_data["Oil Drain Rate (m3/h)"]
    trend_data["Oil Surge vol (m3)"] = trend_data["Delta Time (h)"] * trend_data["Oil Drained Flow"]
    for i in range(len(trend_data)-1):
        if i == 0:
            trend_data["Oil Cumm Surge (m3)"] = 0
        else:
            trend_data.loc[i, "Oil Cumm Surge (m3)"] = np.where(trend_data["Oil Surge vol (m3)"][i+1] + trend_data["Oil Cumm Surge (m3)"][i] < 0, 0, trend_data["Oil Surge vol (m3)"][i+1] + trend_data["Oil Cumm Surge (m3)"][i])
    
    return time, trend_data[["Time (h)", "Volumetric flow rate water (m3/h)", "Water Drain Rate (m3/h)","Water Cumm Surge (m3)","Volumetric flow rate oil (m3/h)", "Oil Drain Rate (m3/h)", "Oil Cumm Surge (m3)"]]



case_surge_volume = {case: None for case in cases}
for tpl, case in zip(tpls, cases):
    time, trend_data = organise_data(tpl)
    case_surge_volume[case] = trend_data

with pd.ExcelWriter(f"{working_location}//Surge Volume.xlsx") as writer: 
    for case, df in  case_surge_volume.items():
         if df is not None:
            df.to_excel(writer, sheet_name = case, index=False)


fig, axes = plt.subplots(nrows = 2, ncols = 1)
x_time  = time
y_water = trend_data["Water Cumm Surge (m3)"]
y_oil = trend_data["Oil Cumm Surge (m3)"]  

axes[0].plot(x_time, y_oil, 'r')
axes[0].set(ylabel ="Oil Surge Volume (m3)", xlabel = None )
axes[1].plot(x_time, y_water, 'r')
axes[1].set(ylabel ="Water Surge Volume (m3)", xlabel = "Time (Hour)")
fig.tight_layout()

fig.savefig(f"{working_location}//Surge Volumes.png")







a=5