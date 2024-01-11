import os
import json
import requests

import model
import server
import crud

os.system("dropdb architexture")
os.system("createdb architexture")

model.connect_to_db(server.app)
model.db.create_all()


#mock user data
for n in range(5):
    email = f"user{n}@test.com"
    password = f"test{n}"

    user = crud.create_user(email, password)

    model.db.session.add(user)
    model.db.session.commit()


#mock library data and geolocation code
with open("data/library.json") as file:
    library_data = json.loads(file.read())

db_structures = []

for structure in library_data:
    address = f"{structure['street']} {structure['city']}"
    if structure['state']:
        address += f" {structure['state']}"
    address += f" {structure['country']}"
    address = address.replace(" ", "%20")
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=<AIzaSyDSMrST6tA5LevywsZYvPXPsmIqhlbmRg4>"

    response = requests.get(url)
    results = response.json()

    if results['status'] == 'OK':
        structure['latitude'] = results['results'][0]['geometry']['location']['lat']
        structure['longitude'] = results['results'][0]['geometry']['location']['lng']

    user_id = 1

    structure = crud.create_structure(
        structure_name=structure["name"],
        structure_type=structure["type"],
        arch_style=structure["style"],
        year_built=structure["year_built"],
        architect_name=structure["architect"],
        arch_firm=structure["firm"],
        street=structure["street"],
        city=structure["city"],
        state=structure["state"],
        country=structure["country"],
        img_path=structure["img_path"],
        img_path2=structure["img_path2"],
        header=structure["header"],
        summary=structure["summary"],
        lat=structure.get("latitude"),
        lng=structure.get("longitude"),
        user_id=user_id,
    )
    
    db_structures.append(structure)