import requests


response = requests.get(
    "/".join([
        "https://icite.od.nih.gov/api",
        "pubs",
        "23456789",
    ]),
)
pub = response.json()
print(pub)
print(pub['references'])
