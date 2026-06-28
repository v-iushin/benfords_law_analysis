import requests
import matplotlib.pyplot as plt
import math as m
from pathlib import Path
import csv
import json



def data_api(url):
    """Fetch data usgin URL"""
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    resp = r.json()
    assert resp[0]["pages"] == 1, f"paginated: {resp[0]}"
    return resp

def data_csv(path):
    """Fetch data from CSV file"""
    lines = path.read_text().splitlines()
    reader = csv.reader(lines)
    return reader

def lead_digit(x):
    """Leading digit of number x"""
    x = abs(x)
    while x >= 10:
        x /= 10
    return int(x)

def exclude_data(response):
    """Exclude aggregated data"""
    exclude_list = []
    for i in range(len(response[1])):
        if response[1][i]["region"]["id"] == "NA":
            exclude_list.append(response[1][i]["id"])
    return exclude_list

def get_values_api(response, exclude_list):
    """Collect values from response (api), int list return"""
    values = []
    for i in range(len(response[1])):
        if response[1][i]["countryiso3code"] in exclude_list:
            continue
        value = response[1][i]["value"]
        if value is None or int(value) == 0:
            continue
        values.append(int(value))
    return values

def get_values_csv(reader):
    """Collect values from reader (csv), int list return"""
    header_row = next(reader)
    values = []
    pop_index = header_row.index("population")
    for row in reader:
        if row[pop_index] == "" or int(float(row[pop_index])) == 0:
            continue
        values.append(int(float(row[pop_index])))
    return values

def values_digit(values, digits):
    """Make list using values for each leading digit"""
    values_dig = [lead_digit(value) for value in values]
    N = len(values_dig)
    counts = [values_dig.count(i) for i in digits]
    return counts, N

def benford(digits, N):
    """Theoretical Benford's value for specific total number of counts"""
    #ben = [N * m.log10(1 + 1/d) for d in digits]
    ben = [round(N * m.log10(1 + 1/d), 3) for d in digits]
    return ben

def chi_sq(values_dig, ben, digits):
    """Pearson chi-square statistic"""
    chi2 = sum([(values_dig[d-1] - ben[d-1])**2 / ben[d-1] for d in digits])
    chi2 = round(chi2, 3)
    return chi2

def magn(x):
    """
    1-9: 0
    10-99: 1
    100-999: 2
    ...
    """
    return int(m.log10(x))

def magnitude_order(values):
    """Orders of magnitude"""
    values = [abs(value) for value in values]
    magn_min = int(magn(min(values)))
    magn_max = int(magn(max(values)))
    magnitudes = list(range(magn_min, magn_max+1))
    magns_count = []
    for magnitude in magnitudes:
        magn_count = 0
        for value in values:
            if magn(value) == magnitude:
                magn_count += 1
        magns_count.append(magn_count)
    return magnitudes, magns_count

def sigma_log10(values):
    """Standart deviation of log_10(x)"""
    logs = [m.log10(abs(value)) for value in values]
    mean = sum(logs) / len(logs)
    sig = m.sqrt(sum((log - mean)**2 for log in logs) / len(logs))
    sig = round(sig, 3)
    return sig

def analyze(name, values, digits):
    """Analyze pipeline"""
    values_dig, N = values_digit(values, digits)
    ben = benford(digits, N)
    chi2 = chi_sq(values_dig, ben, digits)
    sigma = sigma_log10(values)
    magns, magns_count = magnitude_order(values)
    return {
        "name": name, "counts": values_dig, "N": N, "benford": ben,
        "chi_sq": chi2, "sigma": sigma,
        "magnitudes": magns, "magnitude_counts": magns_count
    }



BASE = Path(__file__).parent

url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000&date=1960:2025"
response_gdp = data_api(url_gdp)
#readable_response_gdp = json.dumps(response_gdp, indent=4)
#path_gdp = BASE/"data/gdp.json"
#path_gdp.write_text(readable_response_gdp)

url_pop = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=1960:2025"
response_pop = data_api(url_pop)
#readable_response_pop = json.dumps(response_pop, indent=4)
#path_pop = BASE/"data/pop.json"
#path_pop.write_text(readable_response_pop)

url_area = "https://api.worldbank.org/v2/country/all/indicator/AG.LND.TOTL.K2?format=json&per_page=300&date=2020"
response_area = data_api(url_area)
#readable_response_area = json.dumps(response_area, indent=4)
#path_area = BASE/"data/area.json"
#path_area.write_text(readable_response_area)

path_cities = BASE/"data/worldcities.csv"
reader_cities = data_csv(path_cities)

url_exclude = "https://api.worldbank.org/v2/country/all?format=json&per_page=400"
response_exclude = data_api(url_exclude)
exclude_list = exclude_data(response_exclude)



digits = list(range(1, 10))
crit_v_005 = 15.507
crit_v_0025 = 17.535



values_gdp = get_values_api(response_gdp, exclude_list)
values_pop = get_values_api(response_pop, exclude_list)
values_area = get_values_api(response_area, exclude_list)
values_cities = get_values_csv(reader_cities)

datasets = {
    "GDP, countries": values_gdp, "Population, countries": values_pop, 
    "Area, countries": values_area, "Population, cities": values_cities
}
results = {
    name: analyze(name, values, digits) for name, values in datasets.items()
}
for i in results.keys():
    print(results[i]["name"])
    print()
    print(f"Valid values N: {results[i]["N"]}")
    print(f"Counts: {results[i]["counts"]}")
    print(f"Benford: {results[i]["benford"]}")
    print()
    chi2 = results[i]["chi_sq"]
    print(f"Chi-square: {results[i]["chi_sq"]}")
    if chi2 < crit_v_005:
        print(f"\tPassed for alpha = 0.05 (critical value: {crit_v_005})")
    elif chi2 < crit_v_0025:
        print(f"\tRejected for alpha = 0.05 (critical value: {crit_v_005}) \n\tPassed for alpha = 0.025 (critical value: {crit_v_0025})")
    else:
        print(f"\tRejected for both alpha = 0.05 (critical value: {crit_v_005}) and alpha = 0.025 (critical value: {crit_v_0025})")
    print(f"Sigma: {results[i]["sigma"]}")
    print()
    print(f"Magnitudes: {results[i]["magnitudes"]}")
    print(f"Magnitude counts: {results[i]["magnitude_counts"]}")
    print()
    print()
    print()

'''
"name": name, "counts": values_dig, "N": N, "benford": ben,
"chi_sq": chi2, "sigma": sigma,
"magnitudes": magns, "magnitude_counts": magns_count
'''



# GDP, countires
values_digit_gdp, N_gdp = values_digit(values_gdp, digits)
benford_gdp = benford(digits, N_gdp)

# Population, countries
values_digit_pop, N_pop = values_digit(values_pop, digits)
benford_pop = benford(digits, N_pop)

# Area, countries
values_digit_area, N_area = values_digit(values_area, digits)
benford_area = benford(digits, N_area)

# Population, cities
values_digit_cities, N_cities = values_digit(values_cities, digits)
benford_cities = benford(digits, N_cities)



fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(11,7))
width = 0.3

fig.suptitle("Benford's law vs observation")

ax0.bar(digits, values_digit_gdp, width, color="blue", alpha=0.5, label="GDP, countires")
ax0.plot(digits, benford_gdp, marker="o", color="blue", label="GDP, countries (benford)")
ax0.set_xlabel("Leading digit")
ax0.set_ylabel("Counts")
#ax0.set_title("Benford's law vs observation")
ax0.set_xticks(digits)
ax0.legend()

ax1.bar(digits, values_digit_pop, width, color="orange", alpha=0.5, label="Population, countries")
ax1.plot(digits, benford_pop, marker="o", color="orange", label="Population, countries (benford)")
ax1.set_xlabel("Leading digit")
ax1.set_ylabel("Counts")
#ax1.set_title("Benford's law vs observation")
ax1.set_xticks(digits)
ax1.legend()

ax2.bar(digits, values_digit_area, width, color="black", alpha=0.5, label="Area, countries")
ax2.plot(digits, benford_area, marker="o", color="black", label="Area, countries (benford)")
ax2.set_xlabel("Leading digit")
ax2.set_ylabel("Counts")
#ax2.set_title("Benford's law vs observation")
ax2.set_xticks(digits)
ax2.legend()

ax3.bar(digits, values_digit_cities, width, color="green", alpha=0.5, label="Population, cities")
ax3.plot(digits, benford_cities, marker="o", color="green", label="Population, cities (benford)")
ax3.set_xlabel("Leading digit")
ax3.set_ylabel("Counts")
#ax3.set_title("Benford's law vs observation")
ax3.set_xticks(digits)
ax3.legend()
plt.show()



magns_gdp, magns_count_gdp = magnitude_order(values_gdp)
magns_pop, magns_count_pop = magnitude_order(values_pop)
magns_area, magns_count_area = magnitude_order(values_area)
magns_cities, magns_count_cities = magnitude_order(values_cities)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=1, ncols=4, figsize=(16,4))
ax1.bar(magns_gdp, magns_count_gdp)
ax2.bar(magns_pop, magns_count_pop)
ax3.bar(magns_area, magns_count_area)
ax4.bar(magns_cities, magns_count_cities)
#plt.show()



print()
