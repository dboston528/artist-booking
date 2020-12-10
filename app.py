#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import  Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)



migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return f'id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website_link: {self.website_link},genres: {self.genres}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default = False)

    def __repr__(self):
      return f'id: {self.id}, name: {self.name}'
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
  start_time = db.Column(db.DateTime(), nullable = False)
  artist = db.relationship(Artist, backref=db.backref('shows', cascade='all, delete' ))
  venue = db.relationship(Venue, backref=db.backref('shows', cascade='all, delete'))

  def __repr__(self):
    return f'{self.id}, artist_id:{self.artist_id}, venue_id:{self.venue_id}, start_time:{self.start_time}'
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  for place in Venue.query.distinct(Venue.city, Venue.state).all():
    data.append({
      'city':place.city,
      'state':place.state,
      'venues':[{
        'id': venue.id,
        'name': venue.name,
      } for venue in venues if
          venue.city == place.city and venue.state == place.state]
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venueQuery = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  response2 = {}
  response2['count'] = len(venueQuery)
  #declare empty list
  response2['data']=[]
  # traverse through venueQuery and append to the list
  for venue in venueQuery:
    venue_dict = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda show: show.start_time> datetime.now(), venue.shows)))
    }
    response2['data'].append(venue_dict)
  return render_template('pages/search_venues.html', results=response2, search_term=request.form.get('search_term', ''))
  
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  upcomingShows = db.session.query(Artist,Shows).join(Shows).join(Venue).filter(Shows.venue_id == venue_id, Shows.artist_id == Artist.id, Shows.start_time > datetime.now()).all()
  pastShows = db.session.query(Artist,Shows).join(Shows).join(Venue).filter(Shows.venue_id == venue_id, Shows.artist_id == Artist.id, Shows.start_time < datetime.now()).all()
  data = Venue.query.get(venue_id)
  testData = {
    'id': data.id,
    'name': data.name,
    'city': data.city,
    'state': data.state,
    'address': data.address,
    'phone': data.phone,
    'image_link': data.image_link,
    'facebook_link': data.facebook_link,
    'website': data.website_link,
    'generes': data.genres,
    'seeking_talent': data.seeking_talent,
    'seeking_description': data.seeking_description,
    'past_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
      }for artist, shows in pastShows if shows.venue_id == data.id],
    'upcoming_shows': [{
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
    }for artist, shows in upcomingShows if shows.venue_id == data.id],   
    'upcoming_shows_count': len(upcomingShows),
    'past_shows_count': len(pastShows)
  }
  return render_template('pages/show_venue.html', venue=testData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    newVenue = Venue(
      name =request.form.get('name', ''),
      city =request.form.get('city', ''),
      state =request.form.get('state', ''),
      address =request.form.get('address', ''),
      phone =request.form.get('phone', ''),
      genres =request.form.getlist('genres'),
      facebook_link =request.form.get('facebook_link', '')
    )
    db.session.add(newVenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  deleted = Venue.query.get(venue_id)
  db.session.delete(deleted)
  db.session.commit()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database 
  data2= []
  artists = Artist.query.all()
  for composer in artists:
    data2.append({
      'id': composer.id,
      'name': composer.name
    })
  return render_template('pages/artists.html', artists=data2)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artistQuery= db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  response2 ={}
  response2['count'] = len(artistQuery)
  response2['data']= []
  for artist in artistQuery:
    artist_dict = {
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(list(filter(lambda artist: artist.start_time > datetime.now(), artist.shows)))
    }
    response2['data'].append(artist_dict)
  return render_template('pages/search_artists.html', results=response2, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  pastShows2 = db.session.query(Venue,Shows).join(Shows).filter(Shows.artist_id == artist_id, Shows.venue_id == Venue.id, Shows.start_time < datetime.now()).all()
  upcomingShows2 = db.session.query(Venue,Shows).join(Shows).filter(Shows.artist_id == artist_id, Shows.venue_id == Venue.id, Shows.start_time > datetime.now()).all()
  data2 = Artist.query.get(artist_id)
  testData = {
    'id' : data2.id,
    'name' : data2.name,
    'genres': data2.genres,
    "city": data2.city,
    "state":data2.state,
    "phone": data2.phone,
    "seeking_venue": data2.seeking_venue,
    "image_link":data2.image_link,
    "facebook_link": data2.facebook_link,
    "past_shows": [{
      'venue_id': shows.venue_id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
      }for venue, shows in pastShows2 if shows.artist_id == data2.id],
    "upcoming_shows": [{
      'venue_id': shows.venue_id,
      'venue_name': venue.name,
      'venue_image_link': venue.image_link,
      'start_time': shows.start_time.strftime("%m/%d/%Y, %H:%M")
      }for venue, shows in upcomingShows2 if shows.artist_id == data2.id],
    'upcoming_shows_count': len(upcomingShows2),
    'past_shows_count': len(pastShows2)
  }
  return render_template('pages/show_artist.html', artist=testData)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    editArtist = Artist.query.get(artist_id)
    editArtist.name = request.form.get('name', '')
    editArtist.genres = request.form.getlist('genres')
    editArtist.city = request.form.get('city', '')
    editArtist.state = request.form.get('state', '')
    editArtist.phone = request.form.get('phone', '')
    editArtist.facebook_link = request.form.get('facebook_link', '')
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist  could not be changed for some reason.')
  finally:
    db.session.close
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    editVenue = Venue.query.get(venue_id)
    editVenue.name = request.form.get('name', '')
    editVenue.genres = request.form.getlist('genres')
    editVenue.city = request.form.get('city', '')
    editVenue.state = request.form.get('state', '')
    editVenue.phone = request.form.get('phone', '')
    editVenue.facebook_link = request.form.get('facebook_link', '')
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist  could not be changed for some reason.')
  finally:
    db.session.close
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

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  try:
    newArtist = Artist(
      name =request.form.get('name', ''),
      city =request.form.get('city', ''),
      state =request.form.get('state', ''),
      phone =request.form.get('phone', ''),
      genres =request.form.getlist('genres'),
      facebook_link =request.form.get('facebook_link', '')
    )
    db.session.add(newArtist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  showQuery = db.session.query(Shows).all()
  data2=[{
    'venue_id': show.venue_id,
    'venue_name': show.venue.name,
    'artist_id': show.artist_id,
    'artist_name': show.artist.name,
    'artist_image_link': show.artist.image_link,
    'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
  } for show in showQuery]
  return render_template('pages/shows.html', shows=data2)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  try:
    newShow = Shows(
      artist_id = request.form.get('artist_id', ''),
      venue_id = request.form.get('venue_id', ''),
      start_time = request.form.get('start_time', ''),
    )
    db.session.add(newShow)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
