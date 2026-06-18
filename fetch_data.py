import requests
import matplotlib.pyplot as plt
#import json
#from pathlib import Path



def lead_digit(x):
    x = abs(x)
    while x < 1:
        x *= 10
    while x >= 10:
        x /= 10
    return int(x)



#BASE = Path(__file__).parent
#path_gdp = BASE/"data/gdp.json"
#path_pop =  BASE/"data/pop.json"

url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000&date=1960:2025"
r_gdp = requests.get(url_gdp, timeout=15)
r_gdp.raise_for_status()
#print(r_gdp.status_code)

url_pop = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=1960:2025"
r_pop = requests.get(url_pop, timeout=15)
r_pop.raise_for_status()
#print(r_pop.status_code)

response_gdp = r_gdp.json()
assert response_gdp[0]["pages"] == 1
#readable_response_gdp = json.dumps(response_gdp, indent=4)
#path_gdp.write_text(readable_response_gdp)

response_pop = r_pop.json()
assert response_pop[0]["pages"] == 1
#readable_response_pop = json.dumps(response_pop, indent=4)
#path_pop.write_text(readable_response_pop)



digits = list(range(1, 10))

values_digit_gdp = []
for i in range(len(response_gdp[1])):
    value = response_gdp[1][i]["value"]
    if value is None:
        continue
    else:
        values_digit_gdp.append(lead_digit(value))
#print(values_digit_gdp)
#print(len(values_digit_gdp))
values_list_gdp = [values_digit_gdp.count(i) for i in digits]
print(values_list_gdp)

values_digit_pop = []
for i in range(len(response_pop[1])):
    value = response_pop[1][i]["value"]
    if value is None:
        continue
    else:
        values_digit_pop.append(lead_digit(value))
#print(values_digit_pop)
#print(len(values_digit_pop))
values_list_pop = [values_digit_pop.count(i) for i in digits]
print(values_list_pop)



fig, ax = plt.subplots()
width = 0.3
ax.bar([d + width/2 for d in digits], values_list_gdp, width, label="GDP")
ax.bar([d - width/2 for d in digits], values_list_pop, width, label="Population")
ax.legend()
plt.show()
