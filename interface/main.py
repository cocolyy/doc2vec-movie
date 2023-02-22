from flask import Flask, render_template, request
import pickle
from scipy.spatial import distance

def return_rank_list(embeds: dict, mov_title: str) -> list:
    selected_vector = embeds[mov_title]
    similarities = []
    for movie_title, vector in embeds.items():
        cos_sim = 1 - distance.cosine(selected_vector, vector)
        similarities.append((movie_title, cos_sim))

    ranked_movies = sorted(similarities, key=lambda x: x[1], reverse=True)
    ranked_movies = [x for x in ranked_movies if x[0] != mov_title]

    dct = {}
    for index, item in enumerate(ranked_movies):
        itemlist = list(item)
        dct[itemlist[0]] = index+1

    return dct


with open('mov_embeds_avg_new.pickle', 'rb') as f_1:
    embeddings = pickle.load(f_1, encoding='utf-8')

guess_movie = 'Hababam Sınıfı'.lower()
valid_movies = [movie.lower() for movie in list(embeddings.keys())]
embeddings = dict((k.lower(), v) for k, v in embeddings.items()) 
sim_movies_list = return_rank_list(embeddings, guess_movie)
sorted_sim_movies_list = dict(sorted(sim_movies_list.items(), key=lambda x: x[1]))
total_movies = len(valid_movies)

app = Flask(__name__)
previous_guesses = []

@app.route("/", methods=["GET", "POST"])
def index(name=None):
    result = ""
    sorted_guesses = sorted(previous_guesses, key=lambda x: x[1])
    guess = None
    if request.method == "POST":
        guess = (request.form["guess"]).lower()
        if guess in valid_movies:
            sim_score = sim_movies_list[guess]
            if guess not in [prev[0] for prev in previous_guesses]:
                previous_guesses.insert(0, (guess.title(), sim_score))
            sorted_guesses = sorted(previous_guesses, key=lambda x: x[1])
            result = "The similarity ranking for '{}' is {}".format(guess.title(), sim_score)
        else:
            pass

    if guess_movie not in sim_movies_list:
        sim_movies_list[guess_movie] = 1

    if guess == guess_movie:
        return game_over(previous_guesses)

    lowest_score = None
    lowest_guess = None
    for guess, score in previous_guesses:
        if lowest_score is None or score < lowest_score:
            lowest_score = score
            lowest_guess = guess

    return render_template("index.html", previous_guesses=sorted_guesses, result=result, lowest_guess=lowest_guess, total_movies=total_movies)

def game_over(previous_guesses):
    sorted_guesses = sorted(previous_guesses, key=lambda x: x[1])
    lowest_score_guess = sorted_guesses[0][0]
    return render_template("game_over.html", previous_guesses=previous_guesses, lowest_score_guess=lowest_score_guess)

# @app.route('/game')
# def hello(name=None):
#     return render_template('hello.html', name=name)

# @app.route('/hello')
# def hello(name=None):
#     return 'Hello, World'


if __name__ == "__main__":
    app.run(debug=True)
