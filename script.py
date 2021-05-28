"""Extract data from JSON and export to CSV"""

#import
import json

########################################################

# Opening JSON file and loading the data into the variable data
with open('myFile.json') as json_file:
    data = json.load(json_file)

o = open("myFile.csv", "w")
headers = list(data[0]["YOUR_PARAMETERS"].keys())

o.write(",".join(headers) + "\n")

for client_data in data:
    list_data = []
    for val in client_data["YOUR_PARAMETERS"].values():
        print(val)
        list_data.append(str(val))
    print(list_data)
    o.write(",".join(list_data) + "\n")

o.close()
