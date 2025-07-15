import requests
import time
import csv
from tqdm import tqdm

API_KEY = 'f31ce5f0b961c4d6d5bd8a5d53a8091e'
BASE_URL = 'https://api.themoviedb.org/3/discover/movie'

# Define language quotas
TARGET_COUNTS = {
    'en': 5000,  # English
    'hi': 400,  
    'te': 400, 
    'ta': 300,
    'ml': 200,
    'ka': 100, # Indian
    'fr': 1000,  # French
    'es': 1000,  # Spanish
    'ja': 1000,  # Japanese
    'ko': 1000,  # Korean
}

TOTAL_TARGET = sum(TARGET_COUNTS.values())
START_YEAR = 1950
END_YEAR = 2024

# Genre mapping helper
def get_genre_map():
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=en-US'
    response = requests.get(url).json()
    return {genre['id']: genre['name'] for genre in response['genres']}

GENRE_MAP = get_genre_map()

def fetch_movies(language, target_count):
    collected = []
    page = 1
    with tqdm(total=target_count, desc=f"Fetching {language}") as pbar:
        while len(collected) < target_count and page <= 500:
            params = {
                'api_key': API_KEY,
                'language': 'en-US',
                'sort_by': 'popularity.desc',
                'with_original_language': language,
                'page': page,
                'primary_release_date.gte': f"{START_YEAR}-01-01",
                'primary_release_date.lte': f"{END_YEAR}-12-31",
            }
            response = requests.get(BASE_URL, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch page {page} for {language}")
                break
            data = response.json()
            for movie in data.get('results', []):
                if movie.get('vote_count', 0) < 10:
                    continue  # skip less-rated movies
                title = movie.get('title')
                release_date = movie.get('release_date', '')
                year = int(release_date.split('-')[0]) if release_date else None
                genre_ids = movie.get('genre_ids', [])
                genres = ', '.join([GENRE_MAP.get(gid, '') for gid in genre_ids])
                rating = movie.get('vote_average')
                if year and title and genres:
                    collected.append({
                        'title': title,
                        'year': year,
                        'genre': genres,
                        'rating': rating,
                        'language': language
                    })
                    pbar.update(1)
                if len(collected) >= target_count:
                    break
            page += 1
            time.sleep(0.2)
    return collected

# Aggregate results
all_movies = []
for lang, count in TARGET_COUNTS.items():
    movies = fetch_movies(lang, count)
    all_movies.extend(movies)

# Save to CSV
with open('gmovies.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'year', 'genre', 'rating', 'language'])
    writer.writeheader()
    writer.writerows(all_movies)

print(f"Saved {len(all_movies)} movies to 'gmovies.csv'")
