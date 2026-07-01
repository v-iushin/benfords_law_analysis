import benford

import requests
import matplotlib.pyplot as plt
import math as m
from pathlib import Path
import csv
import json



def data_api(url):
    """Fetch data usging URL"""
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    resp = r.json()
    assert resp[0]["pages"] == 1, f"paginated: {resp[0]}"
    return resp

def data_api_cache(url, path):
    """
    Use cached file if exists
    Fetch if doesnt exist
    Manually delete file to refetch
    """
    if path.exists():
        resp = json.loads(path.read_text())
        return resp
    resp = data_api(url)
    path.write_text(json.dumps(resp, indent=4))
    return resp

def data_csv(path):
    """Fetch data from CSV file"""
    lines = path.read_text(encoding="utf-8").splitlines()
    reader = csv.reader(lines)
    return reader

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



digits = list(range(1, 10))
crit_v_005 = 15.507



BASE = Path(__file__).parent

output_dir = BASE/"output"
output_dir.mkdir(exist_ok=True)

data_dir = BASE/"data"
data_dir.mkdir(exist_ok=True)

url_gdp = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000&date=1960:2025"
path_gdp = data_dir/"gdp.json"
response_gdp = data_api_cache(url_gdp, path_gdp)

url_pop = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=20000&date=1960:2025"
path_pop = data_dir/"pop.json"
response_pop = data_api_cache(url_pop, path_pop)

url_area = "https://api.worldbank.org/v2/country/all/indicator/AG.LND.TOTL.K2?format=json&per_page=300&date=2020"
path_area = data_dir/"area.json"
response_area = data_api_cache(url_area, path_area)

path_cities = data_dir/"worldcities.csv"
reader_cities = data_csv(path_cities)

url_exclude = "https://api.worldbank.org/v2/country/all?format=json&per_page=400"
path_exclude = data_dir/"exclude.json"
response_exclude = data_api_cache(url_exclude, path_exclude)
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
    name: benford.analyze(name, values[0], digits, values[1]) for name, values in datasets.items()
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
    else:
        print(f"\tRejected for alpha = 0.05 (critical value: {crit_v_005})")
    chi_sqs.append(results[i]["chi_sq"])
    print(f"Sigma: {results[i]['sigma']}")
    sigmas.append(results[i]["sigma"])
    print()
    print(f"Magnitudes: {results[i]['magnitudes']}")
    print(f"Magnitude counts: {results[i]['magnitude_counts']}")
    print()
    print()
    print()



fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(11,7))
fig.suptitle("Benford's law vs observation")
for ax, i in zip(axs.flat, results.keys()):
    ax.bar(digits, results[i]["counts"], width=0.5, color=results[i]["color"], alpha=0.5, label=results[i]["name"])
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
    ax.set_xticks(results[i]["magnitudes"])
    ax.text(0.05, 0.8, f"Sigma: {results[i]['sigma']}", transform=ax.transAxes)
fig.savefig(output_dir/"magnitudes.png", bbox_inches="tight")
plt.show()

fig, ax = plt.subplots()
for log_chi_sq, sigma, color, name in zip([m.log10(chi_sq_) for chi_sq_ in chi_sqs], sigmas, colors, names):
    ax.scatter(log_chi_sq, sigma, color=color, label=name)
ax.set_title("Relationship between Sigma and Chi-square")
ax.set_xlabel("Log_10 ( Chi-square )")
ax.set_ylabel("Sigma")
ax.legend()
ax.grid(True)
fig.savefig(output_dir/"sigma-chi.png", bbox_inches="tight")
plt.show()



print()
