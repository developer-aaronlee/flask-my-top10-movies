import requests

tmdb_api_key = "8c0bf74f3e2ad8fde17e6070d4058723"
search_movie_url = "https://api.themoviedb.org/3/search/movie"
movie_image_url = "https://image.tmdb.org/t/p/w500"

# params = {
#     "api_key": tmdb_api_key,
#     "query": "phone booth"
# }
#
# response = requests.get(url=search_movie_url, params=params)
# data = response.json()["results"]
# print(data)

# for x in data:
#     print(f"{x['title']} - {x['release_date']}")


response = requests.get(url="https://api.themoviedb.org/3/movie/1817", params={"api_key": tmdb_api_key})
data = response.json()
# print(data)

movie = {
    "title": data["title"],
    "year": data["release_date"].split("-")[0],
    "img_url": movie_image_url + data["poster_path"],
    "description": data["overview"]
}

print(movie)




