import os
from flask import (Flask, render_template, request, flash, get_flashed_messages, session, redirect, jsonify)
from model import connect_to_db, User, ArchitecturalStructure, Album
import crud
from jinja2 import StrictUndefined
import requests

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.jinja_env.undefined = StrictUndefined



#helper functions
def get_current_user():
    user_id = session.get("user_id")

    if user_id:
        user = crud.get_user_by_id(user_id)
    else:
        user = None
    
    return user


#index
@app.route('/')
def index():
    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    return render_template("index.html")


#user registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        if user:
            flash("Cannot create an account with that email address. Try again.")
        else:
            crud.create_user(email, password)
            flash("Account successfully created! Redirecting to the log in page...", "success")

        return redirect('/registration')

    return render_template("registration.html", messages=messages)


#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        while user:
            if email == user.email and password == user.password:
                session["email"] = user.email
                session["user_id"] = user.user_id
                return redirect(f'/dashboard/{user.user_id}')
            else:
                flash("Invalid email or password. Try again.")
                return redirect('/login')

    return render_template("login.html", messages=messages)


#user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()

    return redirect('/')


#unique user dashboard
@app.route('/dashboard/<user_id>', methods=['GET'])
def dashboard(user_id):
    user = get_current_user()

    return render_template("dashboard.html", user=user)


#structure library
@app.route('/library', methods=['GET'])
def library():
    user = get_current_user()
    structures = crud.get_all_structures()
    
    return render_template("library.html", user=user, structures=structures)


#structure details
@app.route('/structure-details/<structure_id>', methods=['GET'])
def structure_details(structure_id):
    user = get_current_user()
    structure = crud.get_structure_by_id(structure_id)

    return render_template("structure-details.html", user=user, structure=structure)


#submitted structures map
@app.route('/map', methods=['GET'])
def map_display():
    user = get_current_user()

    return render_template("map.html", user=user)


@app.route('/map-data', methods=['GET'])
def map_data():
    approved_structures = ArchitecturalStructure.query.all()
    locations = []
    
    for arch_structure in approved_structures:
        address = f"{arch_structure.structure_name}, {arch_structure.city}, {arch_structure.country}"
        if arch_structure.state:
            address += f", {arch_structure.state}"

        address = address.replace(" ", "%20")
        address = address.replace(",", "")
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyDSMrST6tA5LevywsZYvPXPsmIqhlbmRg4"
        response = requests.get(url)
        results = response.json()

        if results['status'] == 'OK':
            lat = results['results'][0]['geometry']['location']['lat']
            lng = results['results'][0]['geometry']['location']['lng']

            locations.append({
                'structure_name': arch_structure.structure_name,
                'lat': lat,
                'lng': lng,
                'img_path': arch_structure.img_path
            })
        else:
            print(f"Geocoding failed for address: {address}. Status: {results['status']}")

        print(results)
        
    print(f"Locations list: {locations}")

    return jsonify(locations)


#personalized album creation
@app.route('/albums/<user_id>', methods=['GET'])
def albums_display(user_id):
    user = get_current_user()
    albums = crud.get_albums_by_user(user_id)

    return render_template("albums.html", user=user, albums=albums)


@app.route('/albums/<user_id>', methods=['POST'])
def create_album(user_id):
    user = get_current_user()
    album_name = request.form.get('album-name')
    description = request.form.get('album-description')
    
    if album_name:
        album = crud.create_album(user_id=user.user_id, album_name=album_name, description=description)

        return jsonify({
            'album_id': album.album_id, 
            'album_name': album.album_name, 
            'description': album.description
        })
    else:
        return jsonify({'error': 'Album name is required'}), 400
    

@app.route('/add_to_album/<structure_id>', methods=['POST'])
def add_to_album(structure_id):
    
    user_id = session.get("user_id")
    album_id = request.form.get("album-id")
    
    crud.add_structure_to_album(album_id, structure_id)
    
    return redirect(f'/albums/{user_id}')


@app.route('/album-details/<album_id>', methods=['GET'])
def album_details(album_id):
    user = get_current_user()
    album = crud.get_album_by_id(album_id)
    structures = album.structures

    return render_template("album-details.html", user=user, album=album, structures=structures)


@app.route('/edit-album/<album_id>', methods=['POST'])
def edit_album(album_id):
    album_name = request.form['album-name']
    album_description = request.form['album-description']
    
    updated_album = crud.update_album(album_id, album_name, album_description)
    if updated_album:
        return jsonify({'success': 'Album updated successfully'})
    

@app.route('/delete-album/<album_id>', methods=['DELETE'])
def delete_album_route(album_id):
    success = crud.delete_album(album_id)
    if success:
        return jsonify({'success': 'Album deleted successfully'})



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)