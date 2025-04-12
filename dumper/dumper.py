from functools import reduce

import requests
from bs4 import BeautifulSoup
import json
import csv

filename = 'imdb_movies.csv'
reqd_data = ["titleText","titleId","releaseDate","parentalAdvisory","aggregateRating","voteCount","metascore","runtime","genres"]

# Function to scrape IMDb top movies from the JSON inside the script tag
def scrape_imdb_top_movies(url):
    # Send HTTP request to IMDb page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Fetch the page content
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for 4xx/5xx errors

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <script> tag with the id "__NEXT_DATA__" and type "application/json"
    script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    
    if not script_tag:
        print("Could not find the script tag with id '__NEXT_DATA__'")
        return []
    # Extract the JSON data inside the script tag
    json_data = json.loads(script_tag.string)
    # print(dict(json_data).keys())
    # Extract the movie data from the JSON structure
    movie_data = []
    
    # Adjust according to IMDb's JSON structure
    try:
        movies = json_data['props']['pageProps']['searchResults']['titleResults']['titleListItems']
        for movie in movies:
            title = movie['titleText']
            # print(title)
            imdbtitleId = movie['titleId']
            parentalAdvisory = movie.get('certificate',"NA")
            releasedata = movie.get('releaseDate',movie.get('releaseYear',"NA"))
            if releasedata is not None:
                dor = str(releasedata.get('day', "NA")) + "-" + str(releasedata.get('month', "NA")) + "-" + str(releasedata.get('year', "NA"))
            else:
                dor = "NA-NA-NA"  # Default value if releasedata is None
            imdbrating = movie['ratingSummary']['aggregateRating']
            totalRating = movie['ratingSummary'].get('voteCount',"NA")
            metascoreRating = movie.get("metascore","NA")
            runtimeMins = movie.get('runtime',60) / 60
            genres = reduce(lambda i,j : i + " / " + j, list(movie['genres']))
            movie_data.append([title, imdbtitleId, dor, parentalAdvisory, imdbrating, totalRating, metascoreRating, runtimeMins, genres])
    except KeyError as e:
        print(f"Error extracting data: {e}")
    
    return movie_data


def save_to_csv(movie_data, filename):
    # Define column headers (ensure this is defined)

    # Open the file in append mode ('a') to add new data without overwriting
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header row only if the file is empty (optional)
        # This check ensures headers are written only once

        writer.writerows(movie_data)  # Write the movie data

    print(f"Data saved to {filename}")

# Main function to run the script
if __name__ == '__main__':
    # IMDb URL (replace this with the page you want to scrape)
    start_year = 1960
    end_year = 2025
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(reqd_data)
    # Scrape the movie data from IMDb
    movie_data = []
    for year in range(start_year, end_year+1):
        for month in range(1, 12 + 1):
            imdb_url = f'https://www.imdb.com/search/title/?explore=genres&title_type=feature&release_date={year}-{month}-01,{year}-{month}-31&sort=num_votes,desc'
            print("\n\nScraping data for year :: ",year)
            movie_data = scrape_imdb_top_movies(imdb_url)
            if movie_data:
                save_to_csv(movie_data, filename)
        # print(movie_data)
    print("\n\nScraping done")
    # Save the scraped data to a CSV file
