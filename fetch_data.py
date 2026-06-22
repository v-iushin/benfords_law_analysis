import requests
import matplotlib.pyplot as plt
import math as m
from pathlib import Path
import csv
#import json



def data_api(url):
    """Fetch data usgin URL"""
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    resp = r.json()
    assert resp[0]["pages"] == 1, f"paginated: {resp[0]}"
    return resp



def data_csv(path):
    lines = path.read_text().splitlines()
    reader = csv.reader(lines)
    return reader



def lead_digit(x):
    """Leading digit of number x"""
    x = abs(x)
    while x < 1:
        x *= 10
    while x >= 10:
        x /= 10
    return int(x)

def get_values_api(response):
    """Collect values from response"""
    values = []
    for i in range(len(response[1])):
        value = response[1][i]["value"]
        values.append(value)
    return values



def get_values_csv(reader):
    header_row = next(reader)
    values = []
    pop_index = header_row.index("population")
    '''
    for i, value in enumerate(header_row):
        if value == "population":
            pop_index = i
    '''
    for row in reader:
        if row[pop_index] == "" or int(float(row[pop_index])) == 0:
            continue
        values.append(int(float(row[pop_index])))
    return values



def values_list(values, digits):
    """Make list using values for each leading digit"""
    values_digit = []
    for value in values:
        if value is None or value == 0:
            continue
        values_digit.append(lead_digit(value))
    N = len(values_digit)
    print(f"Valid values N: {N}")
    counts = [values_digit.count(i) for i in digits]
    print(f"Counts: {counts}")
    return counts, N

def benford(digits, N):
    """Theoretical Benford's value for specific total number of counts"""
    ben = [N * m.log10(1 + 1/d) for d in digits]
    return ben

def chi_sq(values, ben, digits):
    """Pearson chi-square statistic"""
    crit_v_005 = 15.507
    crit_v_0025 = 17.535
    chi = sum([(values[d-1] - ben[d-1])**2 / ben[d-1] for d in digits])
    chi = round(chi, 3)
    print(f"Chi-square: {chi}")
    if chi < crit_v_005:
        print(f"\tPassed for alpha = 0.05 (critical value: {crit_v_005})")
    elif chi < crit_v_0025:
        print(f"\tRejected for alpha = 0.05 (critical value: {crit_v_005}) \n\tPassed for alpha = 0.025 (critical value: {crit_v_0025})")
    else:
        print(f"\tRejected for both alpha = 0.05 (critical value: {crit_v_005}) and alpha = 0.025 (critical value: {crit_v_0025})")
    return chi



BASE = Path(__file__).parent
path_cities = BASE/"data/worldcities.csv"
reader_cities = data_csv(path_cities)

#path_gdp = BASE/"data/gdp.json"
#path_pop = BASE/"data/pop.json"

url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000&date=1960:2025"
response_gdp = data_api(url_gdp)
#readable_response_gdp = json.dumps(response_gdp, indent=4)
#path_gdp.write_text(readable_response_gdp)

url_pop = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=1960:2025"
response_pop = data_api(url_pop)
#readable_response_pop = json.dumps(response_pop, indent=4)
#path_pop.write_text(readable_response_pop)



digits = list(range(1, 10))

values_cities = get_values_csv(reader_cities)
values_list_cities, N_cities = values_list(values_cities, digits)
benford_cities = benford(digits, N_cities)
chi_cities = chi_sq(values_list_cities, benford_cities, digits)
print()

values_gdp = get_values_api(response_gdp)
values_list_gdp, N_gdp = values_list(values_gdp, digits)
benford_gdp = benford(digits, N_gdp)
chi_gdp = chi_sq(values_list_gdp, benford_gdp, digits)
print()

values_pop = get_values_api(response_pop)
values_list_pop, N_pop = values_list(values_pop, digits)
benford_pop = benford(digits, N_pop)
chi_pop = chi_sq(values_list_pop, benford_pop, digits)
print()



fig, ax = plt.subplots()
width = 0.3
ax.bar([d + width/2 for d in digits], values_list_gdp, width, color="blue", alpha=0.5, label="GDP")
ax.bar([d - width/2 for d in digits], values_list_pop, width, color="orange", alpha=0.5, label="Population")
ax.plot(digits, benford_gdp, marker="o", color="blue", label="GDP (benford)")
ax.plot(digits, benford_pop, marker="o", color="orange", label="Population (benford)")
ax.set_xlabel("Leading digit")
ax.set_ylabel("Counts")
ax.set_title("Benford's law vs observation")
ax.set_xticks(digits)
ax.legend()
plt.show()

# NO PLOT FOR CITIES FOR NOW
