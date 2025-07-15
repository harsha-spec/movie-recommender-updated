from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

API_KEY = 'f31ce5f0b961c4d6d5bd8a5d53a8091e'
TMDB_API_URL = 'https://api.themoviedb.org/3'

# Map year range labels to actual values
YEAR_RANGES = {
    '1920s-1950s': (1920, 1959),
    '1950s-2000s': (1960, 1999),
    '2000s-2020s': (2000, 2020)
}

# Get genre list from TMDB API
def fetch_genres():
    response = requests.get(f'{TMDB_API_URL}/genre/movie/list', params={'api_key': API_KEY})
    genres = response.json().get('genres', [])
    return {str(g['id']): g['name'] for g in genres}

@app.route('/', methods=['GET', 'POST'])
def index():
    genres = fetch_genres()
    return render_template('index.html', genres=genres)

@app.route('/recommend', methods=['POST'])
def recommend():
    genre_id = request.form.get('genre')
    year_label = request.form.get('year_range')
    min_rating = float(request.form.get('min_rating', 0))
    max_rating = float(request.form.get('max_rating', 10))
    
    year_min, year_max = YEAR_RANGES.get(year_label, (2000, 2020))

    url = f'{TMDB_API_URL}/discover/movie'
    params = {
        'api_key': API_KEY,
        'with_genres': genre_id,
        'primary_release_date.gte': f'{year_min}-01-01',
        'primary_release_date.lte': f'{year_max}-12-31',
        'vote_average.gte': min_rating,
        'vote_average.lte': max_rating,
        'sort_by': 'popularity.desc',
        'page': random.randint(1, 5)
    }

    response = requests.get(url, params=params)
    movies = response.json().get('results', [])
    random.shuffle(movies)
    return render_template('results.html', movies=movies[:20])

if __name__ == '__main__':
    app.run(debug=True)
