#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from models import *
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from flask_migrate import Migrate
from datetime import datetime
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


    


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value   
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  areas = Venue.query.distinct('city', 'state').order_by('state').all()
  for area in areas:
    area.venues = Venue.query.filter_by(city=area.city, state=area.state)
  
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  response = {}
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  for venue in venues:
      v = {}
      v['id'] = venue.id
      v['name'] = venue.name
      data.append(v)

  response['count'] = len(data)
  response['data'] = data
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.filter(Venue.id == venue_id).first()

    past = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
                                                                                                Artist.image_link,
                                                                                                Show.start_time).all()

    upcoming = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
                                                                                                Artist.image_link,
                                                                                                Show.start_time).all()

    upcoming_shows = []

    past_shows = []
    
    for i in upcoming:
        upcoming_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'artist_image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
          
            'artist_id': i[1],
            'artist_name': i[2],
            'artist_image_link': i[3],            
            'start_time': str(i[4])
        })
    if venue is None:
        abort(404)

    response = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      venue = Venue(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        address = request.form['address'],
        phone = request.form['phone'],
        genres = request.form.getlist('genres'),
        facebook_link = request.form['facebook_link'],
        image_link = request.form['image_link'],
        website_link=request.form['website_link'],
        seeking_description = request.form['seeking_description']
      )
      db.session.add(venue)
      db.session.commit()
      
  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
  else:
      # on successful db insert, flash success
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    return jsonify({ 'success': False })
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  response = {}
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  for artist in artists:
      a = {}
      a['id'] = artist.id
      a['name'] = artist.name
      data.append(a)

  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter(Artist.id == artist_id).first()

    past = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming_shows = []

    past_shows = []
    
    for i in upcoming:
        upcoming_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'venue_image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'venue_image_link': i[3],
            'start_time': str(i[4])
        })
    

    if artist is None:
        abort(404)

    response = {
        "id": artist.id,
        "name": artist.name,
        "genres": [artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Venue.query.get(artist_id)
  
  artist.name = request.form['name'],
  artist.city = request.form['city'],
  artist.state = request.form['state'],
  artist.phone = request.form['phone'],
  artist.genres = request.form['genres'],
  artist.facebook_link = request.form['facebook_link']
  
  db.session.add(artist)
  db.session.commit()
  db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_description.data = venue.seeking_description
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue.name = request.form['name'],
  venue.city = request.form['city'],
  venue.state = request.form['state'],
  venue.address = request.form['address'],
  venue.phone = request.form['phone'],
  venue.genres = request.form.getlist('genres'),
  venue.facebook_link = request.form['facebook_link'],
  venue.image_link = request.form['image_link'],
  venue.website_link = request.form['website_link'],
  venue.seeking_description = request.form['seeking_description']

  db.session.add(venue)
  db.session.commit()
  db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      artist = Artist(
        name = request.form['name'],
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        image_link = request.form['image_link'],
        genres = request.form.getlist('genres'),
        website_link=request.form['website_link'],
        facebook_link = request.form['facebook_link'],
        # seeking_venue = request.form['seeking_venue'],
        seeking_description = request.form['seeking_description']
      )
      db.session.add(artist)
      db.session.commit()
  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      # Always close the session
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      return render_template('pages/home.html')
  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = Show.query.join(Artist, Artist.id == Show.artist_id).join(
        Venue, Venue.id == Show.venue_id).all()

    response = []
    for show in data:
        response.append({
            "venue_id": show.venue_id,
            "venue_name": db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0],
            "artist_id": show.artist_id,
            "artist_name": db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0],
            "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0],
            "start_time": show.start_time
        })
    return render_template('pages/shows.html', shows=response)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
      show = Show(
        artist_id = request.form['artist_id'],
        venue_id = request.form['venue_id'],
        start_time = request.form['start_time'],
      )
      db.session.add(show)
      db.session.commit()
  except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # on successful db insert, flash success
      flash('An error occurred. Show could not be listed.')
      return render_template('pages/home.html')
  else:  
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('Show was successfully listed!')
  return render_template('pages/home.html')

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
    app.run(
        port=3000,
        debug=True,
        host='0.0.0.0'
        
    )

# Or specify port manually:
