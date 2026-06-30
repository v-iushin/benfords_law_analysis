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
    chi2 = round(chi2, 2)
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
    sig = round(sig, 2)
    return sig

def analyze(name, values, digits, color):
    """Analyze pipeline"""
    values_dig, N = values_digit(values, digits)
    ben = benford(digits, N)
    chi2 = chi_sq(values_dig, ben, digits)
    sigma = sigma_log10(values)
    magns, magns_count = magnitude_order(values)
    return {
        "name": name, "counts": values_dig, "N": N, "benford": ben,
        "chi_sq": chi2, "sigma": sigma,
        "magnitudes": magns, "magnitude_counts": magns_count,
        "color": color
    }



digits = list(range(1, 10))
crit_v_005 = 15.507
#crit_v_0025 = 17.535



BASE = Path(__file__).parent

output_dir = BASE/"output"
output_dir.mkdir(exist_ok=True)

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



values_gdp = get_values_api(response_gdp, exclude_list)
values_pop = get_values_api(response_pop, exclude_list)
values_area = get_values_api(response_area, exclude_list)
values_cities = get_values_csv(reader_cities)

datasets = {
    "GDP, countries": (values_gdp, "blue"), 
    "Population, countries": (values_pop, "orange"), 
    "Area, countries": (values_area, "black"), 
    "Population, cities": (values_cities, "green")
}

results = {
    name: analyze(name, values[0], digits, values[1]) for name, values in datasets.items()
}


sigmas, chi_sqs = [], []
colors, names = [], []
for i in results.keys():
    print(results[i]["name"])
    names.append(results[i]["name"])
    print(f"Color: {results[i]['color']}")
    colors.append(results[i]["color"])
    print()
    print(f"Valid values N: {results[i]['N']}")
    print(f"Counts: {results[i]['counts']}")
    print(f"Benford: {results[i]['benford']}")
    print()
    chi2 = results[i]["chi_sq"]
    print(f"Chi-square: {results[i]['chi_sq']}")
    if chi2 < crit_v_005:
        print(f"\tPassed for alpha = 0.05 (critical value: {crit_v_005})")
    #elif chi2 < crit_v_0025:
    #    print(f"\tRejected for alpha = 0.05 (critical value: {crit_v_005}) \n\tPassed for alpha = 0.025 (critical value: {crit_v_0025})")
    #else:
    #    print(f"\tRejected for both alpha = 0.05 (critical value: {crit_v_005}) and alpha = 0.025 (critical value: {crit_v_0025})")
    else:
        print(f"\tRejected for both alpha = 0.05 (critical value: {crit_v_005})")
    chi_sqs.append(results[i]["chi_sq"])
    print(f"Sigma: {results[i]['sigma']}")
    sigmas.append(results[i]["sigma"])
    print()
    print(f"Magnitudes: {results[i]['magnitudes']}")
    print(f"Magnitude counts: {results[i]['magnitude_counts']}")
    print()
    print()
    print()

'''
"name": name, "counts": values_dig, "N": N, "benford": ben,
"chi_sq": chi2, "sigma": sigma,
"magnitudes": magns, "magnitude_counts": magns_count
'''




fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(11,7))
width = 0.5
fig.suptitle("Benford's law vs observation")
for ax, i in zip(axs.flat, results.keys()):
    ax.bar(digits, results[i]["counts"], width, color=results[i]["color"], alpha=0.5, label=results[i]["name"])
    ax.plot(digits, results[i]["benford"], marker="o", color=results[i]["color"], label=results[i]["name"]+" (benford)")
    ax.set_xlabel("Leading digit")
    ax.set_ylabel("Counts")
    ax.set_xticks(digits)
    ax.legend()
    ax.text(0.5, 0.7, f"Chi-square: {results[i]['chi_sq']}", transform=ax.transAxes)
plt.savefig(output_dir/"benford.png", bbox_inches="tight")
plt.show()

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(11,7))
fig.suptitle("Order of magnitudes")
for ax, i in zip(axs.flat, results.keys()):
    ax.bar(results[i]["magnitudes"], results[i]["magnitude_counts"], color=results[i]["color"], alpha=0.5)
    ax.set_xlabel("Magnitude")
    ax.set_ylabel("Counts")
    ax.text(0.05, 0.8, f"Sigma: {results[i]['sigma']}", transform=ax.transAxes)
fig.savefig(output_dir/"magnitudes.png", bbox_inches="tight")
plt.show()



'''
print(sigmas)
print(chi_sqs)
print(colors)
'''


fig, ax = plt.subplots()

for chi_sq_, sigma, color, name in zip([m.log10(chi_sq_) for chi_sq_ in chi_sqs], sigmas, colors, names):
    ax.scatter(chi_sq_, sigma, color=color, label=name)
#ax.scatter([m.log10(chi_sq_) for chi_sq_ in chi_sqs], sigmas, color=colors)
ax.set_title("Relationship between Sigma and Chi-square")
ax.set_xlabel("Log_10 ( Chi-square )")
ax.set_ylabel("Sigma")
ax.legend()
ax.grid(True)
fig.savefig(output_dir/"sigma-chi.png", bbox_inches="tight")
plt.show()





print()
