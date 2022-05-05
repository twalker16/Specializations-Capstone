from flaskStash import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(1000), unique=True, nullable=False)
    birth_month = db.Column(db.Integer, nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    user_catalog = db.relationship('User_Catalogs', backref='author', lazy=True)
    user_wishlist = db.relationship('User_Wishlists', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

class Genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50), nullable=False, unique=True)
    catalog_genre = db.relationship('Catalog_Genres', backref='genre', lazy=True)
    subgenre = db.relationship('Subgenres', backref='genre', lazy=True)

    def __repr__(self):
        return f"Genres('{self.id}', '{self.name})"

class Subgenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    genre_id = db.Column(db.Integer, db.ForeignKey(Genres.id), nullable=False)
    catalog_genre = db.relationship('Catalog_Genres', backref='subgenre', lazy=True)

    def __repr__(self):
        return f"Subgenres('{self.id}', '{self.name})"   

class Artists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    albums = db.relationship('Albums', backref='artist', lazy=True)

    def __repr__(self):
        return f"Albums('{self.id}', '{self.name})"

class Albums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    image_file=db.Column(db.String(1000), unique=False, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artists.id), nullable=False)
    user_catalog = db.relationship('User_Catalogs', backref='album', lazy=True)
    user_wishlist = db.relationship('User_Wishlists', backref='album', lazy=True)
    tracklist = db.relationship('Tracklists', backref='album', lazy=True)
    formats = db.relationship('Formats', backref='album', lazy=True)

    def __repr__(self):
        return f"Albums('{self.id}', '{self.name})"

class Tracklists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_id=db.Column(db.Integer, db.ForeignKey(Albums.id), nullable=False)
    track_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Tracklists('{self.id}', '{self.name})"

class Formats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    album_id=db.Column(db.Integer, db.ForeignKey(Albums.id), nullable=False)
    user_catalog = db.relationship('User_Catalogs', backref='catalog_format', lazy=True)
    user_wishlist = db.relationship('User_Wishlists', backref='wishlist_format', lazy=True)
    
    def __repr__(self):
        return f"Formats('{self.id}', '{self.name})"

class User_Wishlists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    album_id= db.Column(db.Integer, db.ForeignKey(Albums.id), nullable=False)
    format = db.Column(db.String(20), db.ForeignKey(Formats.id), nullable=True)
    purchase_priority= db.Column(db.Integer)

    def __repr__(self):
        return f"Wishlist('{self.user_id}', '{self.album_id})"

class User_Catalogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    album_id= db.Column(db.Integer, db.ForeignKey(Albums.id), nullable=False)
    format = db.Column(db.String(20), db.ForeignKey(Formats.id), nullable=True)
    package_condition = db.Column(db.String(20), nullable=False)
    media_condition = db.Column(db.String(20), nullable=False)
    approx_resale_value = db.Column(db.Integer, nullable=False)
    overall_rating = db.Column(db.Float)
    production_rating = db.Column(db.Float)
    musicianship_rating = db.Column(db.Float)
    songwriting_rating = db.Column(db.Float)
    vocals_rating = db.Column(db.Float)
    lyrics_rating = db.Column(db.Float)
    catalog_genre = db.relationship('Catalog_Genres', backref='catalog_item', lazy=True)

    def __repr__(self):
        return f"Catalogs('{self.user_id}', '{self.album_id})"

class Catalog_Genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_catalog_id = db.Column(db.Integer, db.ForeignKey(User_Catalogs.id), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey(Genres.id))
    subgenre_id = db.Column(db.Integer, db.ForeignKey(Subgenres.id))

    def __repr__(self):
        return f"CGs('{self.id}', '{self.user_catalog_id})"


def createDummy():
    db.create_all()
    user=Users(username='Test User', password='password', birth_month='04', birth_year='2022')
    # genre=Genres(name='Test')
    # subgenre=Subgenres(name='Test', genre_id=1)
    # artist=Artists(name='Test')
    # album=Albums(name='Test', year=2022, artist_id=1, image_file='default.jpg')
    # track=Tracklists(album_id=1, track_number=1, name='Test')
    # wishlist=User_Wishlists(user_id=1, album_id=1, format='cd')
    # catalog=User_Catalogs(user_id=1, album_id=1, format='cd', package_condition='fair', media_condition='fair', approx_resale_value=12)
    # cg=Catalog_Genres(user_catalog_id=1, genre_id=1, subgenre_id=1)
    db.session.add(user)
    # db.session.add(genre)
    # db.session.add(subgenre)
    # db.session.add(artist)
    # db.session.add(album)
    # db.session.add(track)
    # db.session.add(wishlist)
    # db.session.add(catalog)
    # db.session.add(cg)
    db.session.commit()
