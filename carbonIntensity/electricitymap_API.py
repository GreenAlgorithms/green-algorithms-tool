import requests
import json
import pandas as pd
import os
import pprint
import time
import numpy as np

#############
# LOAD DATA #
#############

choiceMethod = 'custom' # pycountry or custom

print("## Loading data\n")
data_dir = os.path.join(os.path.abspath(''), 'carbonIntensity')

## Download private access token
with open(os.path.join(data_dir, 'access_tokens.json')) as f:
    tokens = json.load(f)
print("Downloaded private token")

print()

################
# API REQUESTS #
################

## Using pycountry for broad search

if choiceMethod == 'pycountry':
    import pycountry
    import pycountry_convert as pc

    print("Using pycountry\n")

    print("Number of countries: {}".format(len(pycountry.countries)))
    continentMapping = {
        'EU': 'Europe',
        'NA': 'North America',
        'SA': 'South America',
        'AF': 'Africa',
        'OC': 'Oceania',
        'AS': 'Asia'
    }

    # data_dict = countriesISO.set_index('Code').astype(str).to_dict('index')

    data_dict2 = dict()
    data_dict2['countryCode'] = []
    data_dict2['carbonIntensity'] = []
    data_dict2['countryName'] = []
    data_dict2['continentName'] = []

    # Only used temporarily, to deal with the query rate limit.
    countries2search = []
    countries2search_old = ['PS', 'PF']

    for country in list(pycountry.countries):

        if country.alpha_2 in countries2search_old:
            response = requests.get(
                'https://api.co2signal.com/v1/latest',
                headers={'auth-token': tokens['electricitymapAPI_token']},
                params={
                    "countryCode": country.alpha_2
                }
            )

            if response.status_code == 200:
                response2 = response.json()
                if 'carbonIntensity' in response2['data']:
                    print(country.alpha_2)
                    data_dict2['countryCode'].append(country.alpha_2)
                    data_dict2['countryName'].append(country.name)
                    data_dict2['carbonIntensity'].append(response2['data']['carbonIntensity'])
                    data_dict2['continentName'].append(continentMapping[pc.country_alpha2_to_continent_code(country.alpha_2)])
                else:
                    print("{} not found".format(country.alpha_2))

            elif response.status_code == 429:
                print('------ Too many requests')
                countries2search.append(country.alpha_2)

            else:
                print("{} not found".format(country.alpha_2))

            time.sleep(80) # Necessary to not be blocked (too much) by the API

    data_df = pd.DataFrame.from_dict(data_dict2)

    print()
    print()

    print("Export")
    data_df.to_csv(os.path.join(data_dir, "electricitymapData2.csv"), sep="|", index=False)

    print()

    print(data_dict2)
    print(data_df)
    print(countries2search)

elif choiceMethod == 'custom':

    with open(os.path.join(data_dir, 'logFile.txt'), 'w') as f:

        locationData = pd.read_csv(os.path.join(data_dir, 'locations_electricitymap.csv'))
        locationData['carbonIntensity'] = np.nan

        n_requests = 0

        time.sleep(3600)

        for locationCode in set(locationData.API_code):

            response = requests.get(
                'https://api.co2signal.com/v1/latest',
                headers={'auth-token': tokens['electricitymapAPI_token']},
                params={
                    "countryCode": locationCode
                }
            )

            n_requests += 1

            if response.status_code == 200:
                response2 = response.json()
                if 'carbonIntensity' in response2['data']:
                    f.write("{}\n".format(locationCode))
                    locationData.loc[locationData.API_code == locationCode, 'carbonIntensity'] = response2['data']['carbonIntensity']
                else:
                    f.write("{} not found\n".format(locationCode))
                    print("{} not found\n".format(locationCode))

            elif response.status_code == 429:
                f.write('------ Too many requests -> {}\n'.format(locationCode))
                break

            else:
                f.write("{} not found\n".format(locationCode))
                print("{} not found\n".format(locationCode))

            # API rate limit is 1 request per second and 30 requests per hour.
            if n_requests < 30:
                time.sleep(2)  # Necessary to not be blocked (too much) by the API
            else:
                f.write("{} - pause for 1 hour\n".format(time.time()))
                print("{} - pause for 1 hour\n".format(time.time()))
                time.sleep(3700)
                n_requests = 0

        f.write("\n\nExport")
        print("\n\nExport")
        locationData.drop(['API_code'],
                          axis=1).to_csv(os.path.join(data_dir, "electricitymapData.csv"),
                                         sep="|", index=False)

elif choiceMethod == 'just1':

    locationCode = 'US-NY'

    response = requests.get(
        'https://api.co2signal.com/v1/latest',
        headers={'auth-token': tokens['electricitymapAPI_token']},
        params={
            "countryCode": locationCode
        }
    )

    print(response.status_code)
    print()
    pprint.pprint(response.json())

else:
    print('Wrong method')