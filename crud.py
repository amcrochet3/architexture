from model import connect_to_db, db, User, ArchitecturalStructure



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
                          header, summary,lat, lng, num_likes=0, featured=False, 
                          times_featured=0, user_id=None):
    new_structure = ArchitecturalStructure(structure_name=structure_name, structure_type=structure_type, 
                                           arch_style=arch_style, year_built=year_built, 
                                           arch_firm=arch_firm, architect_name=architect_name, street=street, 
                                           city=city, state=state, country=country, img_path=img_path, 
                                           img_path2=img_path2, header=header, summary=summary,
                                           lat=lat, lng=lng, num_likes=num_likes, featured=featured, 
                                           times_featured=times_featured, user_id=user_id)
    
    db.session.add(new_structure)
    db.session.commit()
    
    return new_structure


def get_structure_by_id(structure_id):
    
    return ArchitecturalStructure.query.get(structure_id)


def get_all_structures():
    
    return ArchitecturalStructure.query.order_by(ArchitecturalStructure.structure_id.asc())



if __name__ == "__main__":
    from server import app
    connect_to_db(app)