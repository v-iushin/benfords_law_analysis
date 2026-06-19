import requests
import matplotlib.pyplot as plt
#import json
#from pathlib import Path


def data(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    #print(r.status_code)
    resp = r.json()
    assert resp[0]["pages"] == 1, f"paginated: {resp[0]}"
    return resp



def lead_digit(x):
    x = abs(x)
    while x < 1:
        x *= 10
    while x >= 10:
        x /= 10
    return int(x)



def values_list(response, digits):
    values_digit = []
    for i in range(len(response[1])):
        value = response[1][i]["value"]
        if value is None or value == 0:
            continue
        values_digit.append(lead_digit(value))
    #print(values_digit)
    #print(len(values_digit))
    values = [values_digit.count(i) for i in digits]
    print(values)
    return values



#BASE = Path(__file__).parent
#path_gdp = BASE/"data/gdp.json"
#path_pop = BASE/"data/pop.json"

url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000&date=1960:2025"
response_gdp = data(url_gdp)
#readable_response_gdp = json.dumps(response_gdp, indent=4)
#path_gdp.write_text(readable_response_gdp)

url_pop = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=1960:2025"
response_pop = data(url_pop)
#readable_response_pop = json.dumps(response_pop, indent=4)
#path_pop.write_text(readable_response_pop)



digits = list(range(1, 10))
values_list_gdp = values_list(response_gdp, digits)
values_list_pop = values_list(response_pop, digits)



fig, ax = plt.subplots()
width = 0.3
ax.bar([d + width/2 for d in digits], values_list_gdp, width, label="GDP")
ax.bar([d - width/2 for d in digits], values_list_pop, width, label="Population")
ax.legend()
plt.show()
