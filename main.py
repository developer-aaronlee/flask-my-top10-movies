from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Float: Callable


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///my-top-10-movies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = MySQLAlchemy(app)

tmdb_api_key = "8c0bf74f3e2ad8fde17e6070d4058723"
search_movie_url = "https://api.themoviedb.org/3/search/movie"
movie_image_url = "https://image.tmdb.org/t/p/w500"


def search_movie(movie_name):
    params = {
        "api_key": tmdb_api_key,
        "query": movie_name
    }

    response = requests.get(url=search_movie_url, params=params)
    data = response.json()["results"]

    return data


def get_movie(movie_id):
    params = {
        "api_key": tmdb_api_key,
    }

    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{movie_id}", params=params)
    data = response.json()

    return data


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.title}>"


db.create_all()

# new_movie = Movie(title="Phone Booth",
#                   year=2002,
#                   description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by "
#                               "an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's "
#                               "negotiation with the caller leads to a jaw-dropping climax.",
#                   rating=7.3,
#                   ranking=10,
#                   review="My favourite character was the caller.",
#                   img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#
# db.session.add(new_movie)
# db.session.commit()
# print(new_movie)


class AddMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")


class RateMovieForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for x in range(len(all_movies)):
        all_movies[x].ranking = len(all_movies) - x
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        results = search_movie(form.title.data)
        return render_template("select.html", results=results)

    return render_template("add.html", form=form)


@app.route("/find")
def find():
    tmdb_id = request.args.get("movie_id")
    if tmdb_id:
        result = get_movie(tmdb_id)
        new_movie = Movie(title=result["title"],
                          year=result["release_date"].split("-")[0],
                          img_url=f"{movie_image_url}{result['poster_path']}",
                          description=result["overview"])
        db.session.add(new_movie)
        db.session.commit()
        movie_id = new_movie.id
        return redirect(url_for("edit", id=movie_id))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = float(form.rating.data)
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", form=form, movie=movie_to_update)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
