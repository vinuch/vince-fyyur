#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func, distinct
import logging
import sys
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://mac@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    upcoming_shows = db.relationship('Show', primaryjoin="and_(Venue.id==Show.venue_id, func.date(Show.start_time) >  str(func.now()) )", backref="venue_upcoming_shows)", lazy=True)
    past_shows = db.relationship('Show', primaryjoin="and_(Venue.id==Show.venue_id, func.date(Show.start_time) <  str(func.now()) )", backref="venue_past_shows)", lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    upcoming_shows = db.relationship('Show', primaryjoin="and_(Artist.id==Show.artist_id, func.date(Show.start_time) >  str(func.now()) )", backref="artist_upcoming_shows)", lazy=True)
    past_shows = db.relationship('Show', primaryjoin="and_(Artist.id==Show.artist_id, func.date(Show.start_time) <  str(func.now()) )", backref="artist_past_shows)", lazy=True)
                        
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer(), default=0)


class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.String, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  artist_name = db.Column(db.String(120), nullable=False)
  venue_name = db.Column(db.String(120), nullable=False)
  venue_image_link = db.Column(db.String(), nullable=False)
  artist_image_link = db.Column(db.String(), nullable=False)

 

migrarte = Migrate(app, db)

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
  venues = db.session.query(Venue, Venue.id,  Venue.city, Venue.state).group_by(Venue.city, Venue.state, Venue, Venue.id).all()
  cities = db.session.query(Venue.city).group_by(Venue.city).all()
  formatted = []
  for city in cities:
    recordObject = {'city': city.city,
                    'state': '',
                    'venues': []
                    }
    for venue in venues:
        
      venueObject = {'id': venue.Venue.id, 'name': venue.Venue.name} 
      if city.city == venue.Venue.city:
          recordObject['venues'].append(venueObject)
          recordObject['state'] = venue.Venue.state
    formatted.append(recordObject)

  return render_template('pages/venues.html', areas=formatted)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  searchTerm = request.form.get('search_term', '')

  searchResult = Venue.query.filter(Venue.name.ilike('%' + searchTerm + '%')).order_by(Venue.id).all()

  resultObject = {
    'count': len(searchResult),
    'data': searchResult
  }


  return render_template('pages/search_venues.html', results=resultObject, search_term=searchTerm)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue_data = Venue.query.get(venue_id)
  genres_sorted = venue_data.genres.strip('{}').replace('\'', '').replace(' ', '').split(',')
  venue_data.genres = genres_sorted
  all_shows = Show.query.filter_by(venue_id=venue_id).all()
  upcoming_shows = []
  past_shows = []
  for show in all_shows:
    if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > datetime.now():
      upcoming_shows.append(show)
    elif datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < datetime.now():
      past_shows.append(show)
    
  venue_data.upcoming_shows = upcoming_shows
  venue_data.past_shows = past_shows
  venue_data.num_upcoming_shows = len(upcoming_shows)
  venue_data.num_past_shows = len(past_shows)

  return render_template('pages/show_venue.html', venue=venue_data)

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

  data = VenueForm().data

  error = False
  try:
    venue = Venue(name=data['name'], city=data['city'], state=data['state'], phone=data['phone'], genres=data['genres'], image_link=data['image_link'], facebook_link=data['facebook_link'])
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    else:
      flash('Venue ' + data['name'] + ' was successfully listed!')
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['post'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue_shows = Show.query.filter_by(venue_id=venue_id).delete()
  venue = Venue.query.filter_by(id=venue_id).delete()
  db.session.commit()
  
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.with_entities(Artist.id, Artist.name))

@app.route('/artists/search', methods=['POST'])
def search_artists():
  searchTerm = request.form.get('search_term', '')

  searchResult = Artist.query.filter(Artist.name.ilike('%' + searchTerm + '%')).order_by(Artist.id).all()

  resultObject = {
    'count': len(searchResult),
    'data': []
  }

  for item in searchResult:
    dataObj = {
      'id': item.id,
      'name': item.name,
    }
    resultObject['data'].append(dataObj)
  return render_template('pages/search_artists.html', results=resultObject, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  data = Artist.query.get(artist_id)
  genres_sorted = data.genres.strip('{}').replace('\'', '').replace(' ', '').split(',')
  data.genres = genres_sorted
  all_shows = Show.query.filter(Show.artist_id == artist_id).all()
  upcoming_shows = []
  past_shows = []
  for show in all_shows:
    if datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > datetime.now():
      upcoming_shows.append(show)
    elif datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') < datetime.now():
      past_shows.append(show)
    
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
  print(data.past_shows)
  return render_template('pages/show_artist.html', artist=data)



#  Delete
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>', methods=['POST'])
def delete_artist(artist_id):
  try:
    artist_shows = Show.query.filter_by(artist_id=artist_id).delete()
    artist = Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    flash('an error occured artist couldnt be deleted ')
  finally:
    flash('artist deleted successfully')
    db.session.close()
  
  return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  updateData = ArtistForm().data
  # data = request.form.data
  artist = Artist.query.filter_by(id = artist_id).update({ Artist.name: updateData['name'], Artist.city: updateData['city'], Artist.state: updateData['state'], Artist.phone: updateData['phone'], Artist.image_link: updateData['image_link'], Artist.genres: updateData['genres'], Artist.facebook_link: updateData['facebook_link'],})
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  updateData = VenueForm().data
  # data = request.form.data
  venue = Venue.query.filter_by(id = venue_id).update({ Venue.name: updateData['name'], Venue.city: updateData['city'], Venue.state: updateData['state'], Venue.address: updateData['address'], Venue.phone: updateData['phone'], Venue.image_link: updateData['image_link'], Venue.genres: updateData['genres'], Venue.facebook_link: updateData['facebook_link'],})
  venue_shows = Show.query.filter_by(venue_id = venue_id).update({Show.venue_name: updateData['name'], Show.venue_image_link : updateData['image_link']})
  db.session.commit()
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
  data = {
    'artist_name': request.form['name'],
    'artist_city': request.form['city'],
    'artist_state': request.form['state'],
    'artist_phone': request.form['phone'],
    'artist_genres': request.form['genres'],
    'artist_image': request.form['image_link'],
    'artist_facebook': request.form['facebook_link']
  }
  print(ArtistForm().data)

  try:
    artist = Artist(name=data['artist_name'], city=data['artist_city'], state=data['artist_state'], phone=data['artist_phone'], genres=data['artist_genres'], image_link=data['artist_image'], facebook_link=data['artist_facebook'])
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + data['artist_name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows_list = Show.query.all()

  return render_template('pages/shows.html', shows=shows_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  
  error = False
  show_artist_id = request.form.get('artist_id')
  show_venue_id = request.form.get('venue_id')
  show_time = request.form.get('start_time')
  try:
    artist = Artist.query.get(show_artist_id)
    venue = Venue.query.get(show_venue_id)
    show = Show(start_time=show_time, venue_id=show_venue_id, artist_id=show_artist_id, venue_image_link=venue.image_link, artist_name = artist.name, artist_image_link=artist.image_link, venue_name=venue.name)

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
