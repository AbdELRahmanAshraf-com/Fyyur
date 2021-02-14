#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

#----------------------------------------------------------------------------#
# Helping Methods.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


def is_next(date):
    curr_date = datetime.now()
    if date > curr_date:
        return True
    else:
        return False

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#-------------------------------Venues---------------------------------------#

#  1-Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        # Get User Input
        req = request.form
        name = req['name']
        city = req['city']
        state = req['state']
        address = req['address']
        phone = req['phone']
        genres = req.getlist('genres')
        facebook_link = req['facebook_link']
        # Craete Instanse from Venue
        venue = Venue(name=name, genres=genres, address=address, city=city, state=state, phone=phone, facebook_link=facebook_link)
        # Insert Venue Instanse
        venue.insert()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if error:
        # on unsuccessful db insert
        flash('An error occurred. Venue could not be listed.')
        return render_template('pages/home.html')
    else:
        # on successful db insert, flash success
        flash('Venue' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

#  2-Read Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    error = False
    body = []
    try:
        # Filter & Group all venues by Location
        venues = Venue.query.all()
        locations = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
        for location in locations:
            body.append({
                "city": location.city,
                "state": location.state,
                "venues": []
            })

        for venue in venues:
            num_upcoming_shows = 0
            shows = Show.query.filter_by(venue_id=venue.id).all()

            # Calculate no. of coming shows
            for show in shows:
                if is_next(show.date):
                    num_upcoming_shows += 1

            # Add Venues to its location
            for v_location in body:
                if venue.state == v_location['state'] and venue.city == v_location['city']:
                    v_location['venues'].append({
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": num_upcoming_shows
                    })
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return render_template('pages/venues.html', areas=body)
    else:
        abort(500)

#  3-Delete Venues
#  ----------------------------------------------------------------


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        # Get Required Venue
        venue = Venue.query.get(venue_id)
        venue.delete()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    # Check Error Status
    if error:
        # on Error State
        flash('An error occurred. Venue could not be deleted.')
        return render_template('pages/home.html')
    else:
        return redirect(url_for('venues'))

#  4-Venues Search
#  ----------------------------------------------------------------


@app.route('/venues/search', methods=['POST'])
def search_venues():
    response = {}
    error = False
    try:
        search_term = request.form.get('search_term')
        search = f"%{search_term}%"
        venues = Venue.query.filter(Venue.name.ilike(f"%{search}%")).all()
        response['count'] = len(venues)
        data = []

        for venue in venues:
            num_upcoming_shows = 0
            shows = Show.query.filter_by(venue_id=venue.id).all()

            # Calculate no. of coming shows
            for show in shows:
                if is_next(show.date):
                    num_upcoming_shows += 1

            data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows,
            })
        response['data'] = data

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    else:
        abort(500)

#  5-Venues Details
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    data = venue.format()
    shows = Show.query.join(Venue, Show.venue_id == venue_id).all()
    upcoming_shows_count = 0
    past_shows_count = 0
    upcoming_shows = []
    past_shows = []
    for show in shows:
        if is_next(show.date):
            upcoming_shows_count += 1
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.date)
            })
        else:
            past_shows_count += 1
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.date)
            })
    data['upcoming_shows'] = upcoming_shows
    data['past_shows'] = past_shows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows_count'] = upcoming_shows_count
    return render_template('pages/show_venue.html', venue=data)

#  5-Edit Venue
#  ----------------------------------------------------------------


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm(request.form, obj=venue)
        form.populate_obj(venue)
        venue.update()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        abort(500)


#-------------------------------Artists---------------------------------------#

#  1-Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    body = {}
    try:
        # Get User Input
        req = request.form
        name = req['name']
        city = req['city']
        state = req['state']
        phone = req['phone']
        genres = req.getlist('genres')
        facebook_link = req['facebook_link']
        # Craete Instanse from Artist
        artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, facebook_link=facebook_link)
        # Insert Artist Instanse
        artist.insert()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if error:
        # on unsuccessful db insert
        flash('An error occurred. Artist could not be listed.')
        return render_template('pages/home.html')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

#  2-Read Artist
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    error = False
    data = []
    try:
        # Order all artists by name
        artists = Artist.query.order_by("name").all()
        for artist in artists:
            data.append({
                "id": artist.id,
                "name": artist.name
            })
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return render_template('pages/artists.html', artists=data)
    else:
        abort(500)

#  3-Delete Artist
#  ----------------------------------------------------------------


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error = False
    try:
        # Get Required Artist
        artist = Artist.query.get(artist_id)
        artist.delete()
        print(artist_id)
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    # Check Error Status
    if error:
        flash('An error occurred. Artist could not be deleted.')
        return render_template('pages/home.html')
    else:
        return redirect(url_for('artists'))

#  4-Artists Search
#  ----------------------------------------------------------------


@app.route('/artists/search', methods=['POST'])
def search_artists():
    response = {}
    error = False
    try:
        search_term = request.form.get('search_term')
        search = f"%{search_term}%"
        artists = Artist.query.filter(Artist.name.ilike(f"%{search}%")).all()
        response['count'] = len(artists)
        data = []

        for artist in artists:
            num_upcoming_shows = 0
            shows = Show.query.filter_by(artist_id=artist.id).all()

            # Calculate no. of coming shows
            for show in shows:
                if is_next(show.date):
                    num_upcoming_shows += 1

            data.append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming_shows,
            })
        response['data'] = data

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    else:
        abort(500)

#  5-Artist Details
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    data = artist.format()
    shows = Show.query.join(Artist, Show.artist_id == artist_id).all()
    upcoming_shows_count = 0
    past_shows_count = 0
    upcoming_shows = []
    past_shows = []
    for show in shows:
        if is_next(show.date):
            upcoming_shows_count += 1
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.date)
            })
        else:
            past_shows_count += 1
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.date)
            })
    data['upcoming_shows'] = upcoming_shows
    data['past_shows'] = past_shows
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows_count'] = upcoming_shows_count
    return render_template('pages/show_artist.html', artist=data)

#  6-Edit Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm(request.form, obj=artist)
        form.populate_obj(artist)
        artist.update()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        abort(500)

#-------------------------------Shows---------------------------------------#
#  1-Create Show
#  ----------------------------------------------------------------


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        req = request.form
        venue_id = req['venue_id']
        artist_id = req['artist_id']
        date = req['start_time']
        show = Show(venue_id=venue_id, artist_id=artist_id, date=date)
        show.insert()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if error:
        # on unsuccessful db insert
        flash('An error occurred. Show could not be listed.')
        return render_template('pages/home.html')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')

#  2-Read Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    error = False
    data = []
    try:
        # Order all shows by Time
        shows = Show.query.all()
        for show in shows:
            if is_next(show.date):
                data.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": str(show.date)
                })
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    # Check Error Status
    if not error:
        return render_template('pages/shows.html', shows=data)
    else:
        abort(500)


#-------------------------------Home Page---------------------------------------#
@app.route('/')
def index():
    return render_template('pages/home.html')

#-------------------------------App Handling---------------------------------------#


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

#-------------------------------Finish---------------------------------------#


#  Update
#  ----------------------------------------------------------------
