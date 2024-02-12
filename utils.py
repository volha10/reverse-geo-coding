import csv
import ssl
from itertools import combinations

import certifi
import geopy.geocoders
from geopy.distance import geodesic
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def read_csv(file_path):
    points = []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            points.append(
                {
                    "name": row["Point"],
                    "latitude": float(row["Latitude"]),
                    "longitude": float(row["Longitude"]),
                }
            )
    return points


def calculate_distances(points):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geopy.geocoders.options.default_timeout = 10

    geolocator = Nominatim(user_agent="reverse-geo-app", scheme="http")
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    data = {"points": [], "links": []}

    for point in points:
        try:
            print(f"Find address from {point['latitude']} and {point['longitude']}..")

            location = reverse((point["latitude"], point["longitude"]))

            address = location.address if location else "Address not found"
            data["points"].append({"name": point["name"], "address": address})
        except geopy.exc.GeocoderTimedOut as e:
            print(str(e))

    geodesic_limited = RateLimiter(geodesic, min_delay_seconds=1)

    for pair in combinations(points, 2):
        print(pair)

        distance = geodesic_limited(
            (pair[0]["latitude"], pair[0]["longitude"]),
            (pair[1]["latitude"], pair[1]["longitude"]),
        ).meters

        link_name = f"{pair[0]['name']}{pair[1]['name']}"
        data["links"].append({"name": link_name, "distance": round(distance, 1)})

    return {"data": data}


if __name__ == "__main__":
    file_path = "./uploaded-files/sample-geo.csv"
    points = read_csv(file_path)
    result = calculate_distances(points)
    print(result)