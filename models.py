#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#----------------------------------------------------------------------------#
# setup_db(app) binds a flask application and a SQLAlchemy service
#----------------------------------------------------------------------------#

db = SQLAlchemy()

def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    genres=Column(ARRAY(String()),nullable=False)
    address = Column(String(120))
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    website = Column(String(120),nullable=True)
    facebook_link = Column(String(120))
    seeking_talent=Column(Boolean)
    seeking_description=Column(String(400))
    image_link = Column(String(500),nullable=True)
    show=db.relationship('Show',backref=db.backref('venue'), lazy=True)

    def __init__(self, name, genres, address, city, state, phone, facebook_link,seeking_talent=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.facebook_link = facebook_link
        self.seeking_description = seeking_description
        self.seeking_talent=seeking_talent

    def __repr__(self):
        return f'<Venue {self.id} name: {self.name}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
         db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return{
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state':self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image-link': self.image_link
        }

class Artist(db.Model):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    genres=Column(ARRAY(String()),nullable=False)
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    facebook_link = Column(String(120))
    image_link=Column(String(120))
    seeking_venue=Column(Boolean)
    seeking_description=Column(String(400))
    show=db.relationship('Show',backref=db.backref('artist'), lazy=True)

    def __init__(self, name, genres, city, state, phone, facebook_link,seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.facebook_link = facebook_link
        self.seeking_description = seeking_description
        self.seeking_venue=seeking_venue

    def __repr__(self):
        return f'<Artist {self.id} name: {self.name}>'

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
         db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return{
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state':self.state,
            'phone': self.phone,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image-link': self.image_link
        }

class Show(db.Model):
    __tablename__ = 'show'
    id = Column(Integer, primary_key=True)
    venue_id=Column(Integer,ForeignKey('venue.id'),nullable=False)
    artist_id=Column(Integer,ForeignKey('artist.id'),nullable=False)
    date=Column(DateTime)
    
    
    def __init__(self, venue_id, artist_id, date):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.date = date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



#     def short(self):
#         return{
#             'id': self.id,
#             'name': self.name,
#         }

#     def long(self):
#         print(self)
#         return{
#             'id': self.id,
#             'name': self.name,
#             'city': self.city,
#             'state': self.state,
#         }