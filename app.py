from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import pandas as pd
import sys
import os
import collections
from contextlib import _RedirectStream
from typing import Collection
from pymongo.errors import DuplicateKeyError
from flask import Flask, jsonify, request,render_template,redirect,url_for,session,flash
from pymongo import MongoClient, errors
import logging
import certifi

# Add the models directory to the Python path
from models import movie_model

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace with a secure secret key

try:
    client = MongoClient('mongodb+srv://aliumu123:aliumut123@MoviePicker.zdjx97m.mongodb.net/',
                         tlsCAFile=certifi.where())
    db = client.mydatabase  # write your database name instead of 'mydatabase'
    users_collection = db.mycollection  # write your collection name instead of 'mycollection'

    logging.info("Connected to MongoDB successfully")
except errors.ConnectionError as e:
    logging.error(f"Could not connect to MongoDB:{e}")
    raise

# Configure server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

user_preferences = {}

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            print("Missing username or password")
            return render_template('signin.html', error="Username and password is required."), 400

        user_data = {
            'username': username,
            'password': password
        }

        try:
            users_collection.insert_one(user_data)
            return redirect(url_for('index'))
        except DuplicateKeyError:
            print("Duplicate username")
            return render_template('signin.html', error="This username is already in use."), 400
        except Exception as e:
            print(f"Error: {e}")
            return render_template('signin.html', error="Error"), 500

    # Render the signin page for GET request
    return render_template('signin.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/question')
def question():
    return render_template('question.html')

@app.route('/next_question', methods=['POST'])
def next_question():
    age_preference = request.form['age']
    user_preferences['age'] = age_preference
    return redirect(url_for('occasion'))

@app.route('/occasion')
def occasion():
    return render_template('occasion.html')

@app.route('/submit_occasion', methods=['POST'])
def submit_occasion():
    selected_occasion = request.form['occasion']
    user_preferences['occasion'] = selected_occasion
    return redirect(url_for('genres'))

@app.route('/genres')
def genres():
    return render_template('genres.html', genres=movie_model.genres_list)

@app.route('/submit_genres', methods=['POST'])
def submit_genres():
    selected_genres = request.form.getlist('genres')
    user_preferences['genres'] = selected_genres

      # Initialize the list of recommended movie IDs if not already done
    if 'recommended_ids' not in session:
        session['recommended_ids'] = []

    # Filter movies and store the filtered dataframe in session
    filtered_df = movie_model.filter_movies(user_preferences, session["recommended_ids"])
    session['filtered_df'] = filtered_df.to_dict('records')
    session['current_index'] = 0

    return redirect(url_for('recommendation'))

@app.route('/recommendation')
def recommendation():
    # Get the filtered dataframe from the session
    filtered_df = pd.DataFrame(session.get('filtered_df', []))
    
    # Handle case where filtered_df might be empty
    if filtered_df.empty:
        return render_template('recommendation.html', movie={
            'title': 'No more movies found',
            'description': 'No more movies match your preferences.',
            'image_url': '',
            'trailer_url': '#',
            'watch_url': '#'
        })

    # Get the recommendation from the model
    movie = movie_model.get_recommendation(filtered_df)


    # Add the recommended movie's ID to the session to avoid recommending it again
    recommended_ids = session.get('recommended_ids', [])
    recommended_ids.append(movie['id'])
    session['recommended_ids'] = recommended_ids


    # Debug print for image URL
    print(f"Image URL in Flask route: {movie['image_url']}")
    
    return render_template('recommendation.html', movie=movie)

@app.route('/next_recommendation')
def next_recommendation():
    # Increment the current index
    session['current_index'] = session.get('current_index', 0) + 1
    
    return redirect(url_for('recommendation'))

@app.route('/blog')
def blog():
    # Get the list of top 100 popular movies
    movies = movie_model.list_popular_movies()
    
    return render_template('blog.html', movies=movies)

@app.route('/movie')
def movie_picker():
    # Get the list of top 100 movies based on vote average
    movies = movie_model.list_top_rated_movies()
    
    return render_template('movie.html', movies=movies)


@app.route('/genres/<genre>')
def genre_movies(genre):
    # Get the list of movies for the selected genre
    movies = movie_model.list_movies_by_genre(genre)

    return render_template('genre_movies.html', genre=genre, movies = movies)

if __name__ == '__main__':
    app.run(debug=True)
