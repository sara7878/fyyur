
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#SARA

import logging
import sys
from logging import FileHandler, Formatter
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

import babel
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


#define db object which links sql alchemy to our flask app
db = SQLAlchemy()

app = Flask(__name__)
moment = Moment(app)
#connect the application to the database 
app.config.from_object('config')


db.init_app(app)
#link the migrate object to the flask app and the sqlalchemy database
#this migrate let us initiate with the migration commends
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120))
    
    shows = db.relationship('Show', backref=('venues'))

    artists = db.relationship('Artist', secondary='shows')

  
    def __repr__(self):
      return f'''<Venue id: {self.id} , name: {self.name} , city:{self.city} , state: {self.state} , 
      address: {self.address} , phone: {self.phone} , genres :{self.genres} , image_link: {self.image_link} , 
      facebook_link: {self.facebook_link}>'''
    # TODO: implement any missing fields, as a database migration using Flask-Migrate yes

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website=db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship('Show', backref=('artists'))

    venues = db.relationship('Venue', secondary='shows')

    def __repr__(self):
      return f'''<Artist id: {self.id} , name: {self.name} , city:{self.city} , state: {self.state} , 
      address: {self.address} , phone: {self.phone} , genres :{self.genres} , image_link: {self.image_link} , 
      facebook_link: {self.facebook_link}>'''

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)

    artist = db.relationship('Artist')

    venue = db.relationship('Venue')

    def __repr__(self):
      return f'<Show Artist_ID: {self.artist_id} , Venue_ID: {self.venue_id} , start_time: {self.start_time}>'
      
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data. yes
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  all_areas_have_venues = Venue.query.order_by(Venue.city,Venue.state).all()
  data = []
  for area in all_areas_have_venues:
    venues_of_one_area = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in venues_of_one_area:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(),
                                                  venue.shows)))
      })
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": venue_data
    })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" yes
  search_term=request.form.get('search_term','')
  venues=Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data=[]
  for venue in venues:
    temp={}
    temp['name']=venue.name
    temp['id']=venue.id
    temp['num_upcoming_shows']=len(venue.shows)
    data.append(temp)

  response={}
  response['count']=len(data)
  response['data']=data
 

  return render_template('pages/search_venues.html', results=response,search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id yes
  venue = Venue.query.get(venue_id)
  data={
            'id': venue.id,
            'name': venue.name,
            'city': venue.city,
            'state': venue.state,
            'address': venue.address,
            'phone': venue.phone,
            'genres': venue.genres,  
            'image_link': venue.image_link,
            'facebook_link': venue.facebook_link,
            'website': venue.website,
            'seeking_talent': venue.seeking_talent,
            'seeking_description': venue.seeking_description,
            'past_shows': list(filter(lambda x: x.start_time < datetime.today(), venue.shows)),
            'upcoming_shows':list(filter(lambda x: x.start_time >= datetime.today(), venue.shows)),
            'past_shows_count':len(list(filter(lambda x: x.start_time <
                             datetime.today(), venue.shows))),
            'upcoming_shows_count':len(list(filter(lambda x: x.start_time >=
                                 datetime.today(), venue.shows))),

        }
  
  return render_template('pages/show_venue.html', venue=data)

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
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        temp_genres = request.form.getlist('genres')
        venue.genres = ','.join(temp_genres)
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.image_link=request.form['image_link']
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')   

        else:
            flash('Venue ' + request.form['name'] +' was successfully listed!')
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead. yes
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.') yes
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using yes
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return None
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database yes
  data=Artist.query.all()
  return render_template('pages/artists.html',
                           artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band". yes

  search_term=request.form.get('search_term','')
  artists=Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  data=[]
  for artist in artists:
    temp={}
    temp['name']=artist.name
    temp['id']=artist.id
    temp['num_upcoming_shows']=len(artist.shows)
    data.append(temp)

  response={}
  response['count']=len(data)
  response['data']=data

  return render_template('pages/search_artists.html',
   results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given venue_id
  # TODO: replace with real artist data from the artists table, using artist_id yes
    # shows the artist page with the given venue_id
  artist = Artist.query.get(artist_id)
  data={
            'id': artist.id,
            'name': artist.name,
            'city': artist.city,
            'state': artist.state,
            'address': artist.address,
            'phone': artist.phone,
            'genres': artist.genres,  
            'image_link': artist.image_link,
            'facebook_link': artist.facebook_link,
            'website': artist.website,
            'seeking_talent': artist.seeking_talent,
            'seeking_description': artist.seeking_description,
            'past_shows': list(filter(lambda x: x.start_time < datetime.today(), artist.shows)),
            'upcoming_shows':list(filter(lambda x: x.start_time >= datetime.today(), artist.shows)),
            'past_shows_count':len(list(filter(lambda x: x.start_time <
                             datetime.today(), artist.shows))),
            'upcoming_shows_count':len(list(filter(lambda x: x.start_time >=
                                 datetime.today(), artist.shows))),

        }
  
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id> yes
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes yes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.phone = request.form['phone']
    artist.facebook_link = request.form['facebook_link']
    artist.state = request.form['state']
    artist.seeking_description = request.form['seeking_description']
    artist.genres = request.form['genres']
    artist.website = request.form['website']
    artist.image_link = request.form['image_link']
    db.session.add(artist)
    db.session.commit()    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id> yes
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes  yes
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']    
    venue.phone = request.form['phone']
    venue.state = request.form['state']
    venue.facebook_link = request.form['facebook_link']
    venue.city = request.form['city']
    venue.address = request.form['address']
    venue.genres = request.form['genres']
    venue.seeking_description = request.form['seeking_description']
    venue.website = request.form['website']
    venue.image_link = request.form['image_link']
    db.session.add(venue)
    db.session.commit()
  except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
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
  # TODO: modify data to be the data object returned from db insertion yes
    error = False
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.address = request.form['address']
        artist.phone = request.form['phone']
        temp_genres = request.form.getlist('genres')
        artist.genres = ','.join(temp_genres)
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        artist.image_link=request.form['image_link']
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')   

        else:
            flash('Venue ' + request.form['name'] +' was successfully listed!')
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead. yes
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.') yes
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()

  data = []
  for show in shows:
    data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.isoformat()
        })
  

  return render_template('pages/shows.html', shows=data)

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
        show = Show()
        show.venue_id = request.form['venue_id']
        show.artist_id = request.form['artist_id']
        show.start_time = request.form['start_time']
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
        else:  # on successful db insert, flash success
            flash('successfully listed')
        return render_template('pages/home.html')
         # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Launch.
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
'''
