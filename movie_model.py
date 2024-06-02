import pandas as pd

genres_list = ["Action", "Mystery", "Comedy", "Biography", "Drama", "History", "Adventure", "Animation", "Thriller", "Music", "Crime", "Sport", "Romance", "Disaster", "Science Fiction", "Western", "Fantasy", "War", "Family", "Horror"]


# Load the CSV file
file_path = '/Users/tufangur/Downloads/TMDB_movie_dataset_v11.csv'
df = pd.read_csv(file_path)

# Display the first few rows and the information of the dataframe
print(df.head())
print(df.info())

# Handle missing values
df = df.dropna(subset=['title', 'release_date'])
df['overview'] = df['overview'].fillna('')
df['genres'] = df['genres'].fillna('Unknown')

# Convert columns to appropriate data types
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

# Extract and transform relevant features
df['year'] = df['release_date'].dt.year

# Save the preprocessed data
df.to_csv('preprocessed_data.csv', index=False)
print("Preprocessed data saved to 'preprocessed_data.csv'.")


genres_list = ["Action", "Mystery", "Comedy", "Biography", "Drama", "History", "Adventure", "Animation", "Thriller", "Music", "Crime", "Sport", "Romance", "Disaster", "Science Fiction", "Western", "Fantasy", "War", "Family", "Horror"]

def filter_movies(preferences, excluded_ids):
    filtered_df = df.copy()
    

    # Exclude previously recommended movies
    filtered_df = filtered_df[~filtered_df['id'].isin(excluded_ids)]

     # Exclude movies with Japanese, Thai, and Korean languages/ Bad Sexual Pictures
    excluded_languages = ['ja', 'th', 'ko']
    filtered_df = filtered_df[~filtered_df['original_language'].isin(excluded_languages)]

    # Exclude specific movie titles Bad Movie Posters
    excluded_titles = ['Insatiable', 'The Altar of Aphrodite', 'Taboo', 'Taboo 1']
    filtered_df = filtered_df[~filtered_df['title'].isin(excluded_titles)]

    # Filter based on age preference
    if preferences.get('age'):
        current_year = pd.Timestamp.now().year
        if preferences['age'] == '3years':
            filtered_df = filtered_df[filtered_df['year'] >= (current_year - 3)]
        elif preferences['age'] == '5years':
            filtered_df = filtered_df[filtered_df['year'] >= (current_year - 5)]
        elif preferences['age'] == '10years':
            filtered_df = filtered_df[filtered_df['year'] >= (current_year - 10)]
        elif preferences['age'] == '20years':
            filtered_df = filtered_df[filtered_df['year'] >= (current_year - 20)]

    # Filter based on genres
    if preferences.get('genres'):
        filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: any(genre in x for genre in preferences['genres']))]

    # Filter based on occasion
    if preferences.get('occasion'):
        if preferences['occasion'] == 'Just watching a movie by myself.':
            pass  # No additional filtering
        elif preferences['occasion'] == 'Movie Date.':
            filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: 'Romance' in x)]
        elif preferences['occasion'] == 'Movie Night with friends.':
            filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: 'Comedy' in x or 'Action' in x)]
        elif preferences['occasion'] == 'Date Night with boyfriend or girlfriend.':
            filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: 'Romance' in x or 'Drama' in x)]
        elif preferences['occasion'] == 'Watching a movie with family or relatives.':
            filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: 'Family' in x or 'Animation' in x)]

    # Sort the filtered movies by popularity or vote average
    # Ensure movies have at least a 7.0 vote average and 100 popularity
    filtered_df = filtered_df[(filtered_df['vote_average'] >= 7.0) & (filtered_df['popularity'] >= 80)]

        
    return filtered_df

def get_recommendation(filtered_df):
    if not filtered_df.empty:
        movie = filtered_df.sample(n=1).iloc[0].to_dict()
        movie['image_url'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"  # Adjust URL based on your dataset
        movie['trailer_url'] = f"https://www.youtube.com/results?search_query={movie['title']}+trailer"  # Example trailer link
        movie['watch_url'] = movie['homepage'] if pd.notnull(movie['homepage']) else f"https://www.youtube.com/results?search_query={movie['title']}+watch"  # Example watch link
        movie['description'] = movie.get('overview', 'No description available.')  # Ensure description is set
        movie['title'] = movie.get('title', 'No title available')  # Ensure title is set

        # Debug print statements
        print(f"Title: {movie['title']}")
        print(f"Description: {movie['description']}")
    else:
        movie = {
            'title': 'No more movies found',
            'description': 'No more movies match your preferences.',
            'image_url': '',
            'trailer_url': '#',
            'watch_url': '#'
        }
    
    # Debug print for image URL
    print(f"Image URL: {movie['image_url']}")

    return movie

def list_popular_movies(limit=100):
    # Filter movies based on specific genres
    filtered_df = df[df['genres'].apply(lambda x: any(genre in x for genre in ["Action"]))]
    
    # Sort movies by popularity and return the top `limit` movies
    popular_movies = filtered_df.sort_values(by='popularity', ascending=False).head(limit)
    movies_list = popular_movies.to_dict('records')
    
    # Add image URLs
    for movie in movies_list:
        movie['image_url'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
        movie['trailer_url'] = f"https://www.youtube.com/results?search_query={movie['title']}+trailer"  # Example trailer link
        movie['watch_url'] = movie['homepage'] if pd.notnull(movie['homepage']) else f"https://www.youtube.com/results?search_query={movie['title']}"  # Example watch link
    
    return movies_list

def list_top_rated_movies(limit=100):
    # Filter movies based on specific genres
    filtered_df = df[df['genres'].apply(lambda x: any(genre in x for genre in ["Action", "Mystery", "Comedy", "Biography", "Drama", "History", "Adventure", "Animation", "Thriller", "Music", "Crime", "Sport"]))]

    # First filter movies with more than 1000 votes
    filtered_df = df[df['vote_count'] > 1000]

    # If the number of movies with more than 1000 votes is greater than 0, perform the sorting process
    if len(filtered_df) > 0:
        top_rated_movies = filtered_df.sort_values(by='vote_average', ascending=False).head(limit)
        # Sonuçları kullanın
        print(top_rated_movies)
    movies_list = top_rated_movies.to_dict('records')
    
    # Add image URLs
    for movie in movies_list:
        movie['image_url'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
        movie['trailer_url'] = f"https://www.youtube.com/results?search_query={movie['title']}+trailer"  # Example trailer link
        movie['watch_url'] = movie['homepage'] if pd.notnull(movie['homepage']) else f"https://www.youtube.com/results?search_query={movie['title']}"  # Example watch link

    
    return movies_list


def list_movies_by_genre(genre, limit=100):
    # Filter movies based on the selected genre
    filtered_df = df[df['genres'].apply(lambda x: genre in x)]

    # Sort movies by popularity and return the top limit movies
    genre_movies = filtered_df.sort_values(by='popularity', ascending=False).head(limit)
    movies_list = genre_movies.to_dict('records')

    # Add image URLs and other links
    for movie in movies_list:
        movie['image_url'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
        movie[
            'trailer_url'] = f"https://www.youtube.com/results?search_query={movie['title']}+trailer"  # Example trailer link
        movie['watch_url'] = movie['homepage'] if pd.notnull(
            movie['homepage']) else f"https://www.amazon.com/s?k={movie['title']}"  # Example watch link

    return movies_list