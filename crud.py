from model import connect_to_db, db, User, ArchitecturalStructure, Album



#CRUD operations for User
def create_user(email, password):
    new_user = User(email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def get_user_by_id(user_id):

    return User.query.get(user_id)


def get_user_by_email(email):

    return User.query.filter_by(email=email).first()


def get_all_users():

    return User.query.all()


#CRUD operations for ArchitecturalStructure
def create_structure(structure_name, structure_type, arch_style, year_built, arch_firm, 
                          architect_name, street, city, state, country, img_path, img_path2, 
                          header, summary,lat, lng, featured=False, 
                          times_featured=0, user_id=None):
    new_structure = ArchitecturalStructure(structure_name=structure_name, structure_type=structure_type, 
                                           arch_style=arch_style, year_built=year_built, 
                                           arch_firm=arch_firm, architect_name=architect_name, street=street, 
                                           city=city, state=state, country=country, img_path=img_path, 
                                           img_path2=img_path2, header=header, summary=summary,
                                           lat=lat, lng=lng, featured=featured, 
                                           times_featured=times_featured, user_id=user_id)
    
    db.session.add(new_structure)
    db.session.commit()
    
    return new_structure


def get_structure_by_id(structure_id):
    
    return ArchitecturalStructure.query.get(structure_id)


def get_all_structures():
    
    return ArchitecturalStructure.query.order_by(ArchitecturalStructure.structure_id.asc())


#CRUD operations for Album
def create_album(album_name, description=None, user_id=None):
    default_thumbnail = '/static/img/album thumbnail placeholder.jpg'
    new_album = Album(user_id=user_id, album_name=album_name, description=description, thumbnail_path=default_thumbnail)

    db.session.add(new_album)
    db.session.commit()

    return new_album


def get_album_by_id(album_id):

    return Album.query.get(album_id)


def get_albums_by_user(user_id):

    return Album.query.filter_by(user_id=user_id).all()


def add_structure_to_album(album_id, structure_id):
    album = Album.query.get(album_id)
    structure = ArchitecturalStructure.query.get(structure_id)

    if structure not in album.structures:
        album.structures.append(structure)

        if len(album.structures) == 1:
            album.thumbnail_path = structure.img_path
            
            db.session.commit()
        
    return album


def update_album(album_id, new_name, new_description):
    album = Album.query.get(album_id)
    if album:
        album.album_name = new_name
        album.description = new_description
        
        db.session.commit()
    
    return album


def delete_album(album_id):
    album = Album.query.get(album_id)

    if album:
        db.session.delete(album)
        db.session.commit()

        return True
    else:
        return False



if __name__ == "__main__":
    from server import app
    connect_to_db(app)