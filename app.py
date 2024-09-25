from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_session import Session
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import date
from PIL import Image
from models import User
from forms import *
import dao
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "d042d7b2aabe70231d9f21dd0fe0263a"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
bootstrap = Bootstrap5(app)

@app.route('/')
def home():
    session["url"] = request.path
    series_form, followed_series_ids = False, []
    if current_user.is_authenticated:
        series_form = SeriesForm()
        followed_series_ids = dao.get_all_followed_ids(current_user.username)
    return render_template("index.html", series=dao.get_all_elements("series", "series_id", "DESC"), episodes=dao.get_all_elements("episodes", "date", "ASC"), followed_series=followed_series_ids, series_form=series_form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You have to log out before creating a new account!", "warning")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        input_username = register_form.username.data
        input_name = register_form.name.data
        input_surname = register_form.surname.data
        input_password = generate_password_hash(register_form.password.data, method="sha256")  
        input_type = register_form.type.data        
        user_already_exists = dao.element_already_in_db("users", "username", input_username)
        if user_already_exists:
            register_form.username.errors.append("Username already taken, please try again!")
            return render_template("register.html", form=register_form)
        new_user = {"username": input_username, "name": input_name, "surname": input_surname, "password": input_password, "type": input_type}
        new_user_registered = dao.add_user(new_user)
        if new_user_registered:
            user_in_db = dao.element_already_in_db("users", "username", input_username)
            new_logged_in = User(id=user_in_db["id"], username=user_in_db["username"], name=user_in_db["name"], surname=user_in_db["surname"], type=user_in_db["type"])
            login_user(new_logged_in)
            flash("Your account has successfully been created!", "success")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("home"))
        register_form.type.errors.append("Registration failed, please try again!")
    return render_template("register.html", form=register_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in!", "warning")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        input_username = login_form.username.data
        input_password = login_form.password.data
        user_in_db = dao.element_already_in_db("users", "username", input_username)
        if not user_in_db or not check_password_hash(user_in_db['password'], input_password):
            login_form.username.errors.append("Incorrect username or password, please try again!")
            login_form.password.errors.append("Incorrect username or password, please try again!")
            return render_template("login.html", form=login_form)
        new_logged_in = User(id=user_in_db["id"], username=user_in_db["username"], name=user_in_db["name"], surname=user_in_db["surname"], type=user_in_db["type"])
        login_user(new_logged_in)
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    return render_template("login.html", form=login_form)

@login_manager.user_loader
def load_user(user_id):
    user_in_db = dao.element_already_in_db("users", "id", user_id)
    if user_in_db:
        user = User(id=user_in_db["id"], username=user_in_db["username"], name=user_in_db["name"], surname=user_in_db["surname"], type=user_in_db["type"])
    else:
        user = None
    return user

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("home"))

@app.route("/create-series", methods=['GET', 'POST'])
def create_series():
    session["url"] = request.path
    if not current_user.is_authenticated:
        flash("You need to be logged in as a Creator to upload a series of podcasts!", "warning")
        return redirect(url_for("login"))
    if current_user.type != "Creator":
        flash("Only Creators can upload a series of podcasts!", "warning")
        if "url" in session:
            return redirect(url_for("home"))
    series_form = SeriesForm()    
    if series_form.validate_on_submit():
        input_title = series_form.title.data
        input_description = series_form.description.data
        input_category = series_form.category.data
        if input_category == "default":
            series_form.category.errors.append("Please insert a valid category!")
            return render_template("create_series.html", form=series_form)
        input_image = series_form.image.data
        filename = secure_filename(input_image.filename)
        imagefile_in_db = dao.element_already_in_db("series", "image", filename)
        if imagefile_in_db:
            series_form.image.errors.append("This image file has already been used, please try again!")
            return render_template("create_series.html", form=series_form)
        input_image = Image.open(input_image)
        input_image = input_image.resize((int(input_image.width), int(input_image.width * 0.5625)))
        input_image.save(f"static\images\series\{filename}")
        new_series = {"title": input_title, "description": input_description, "category": input_category, "image": filename, "username": current_user.username}
        new_series_added = dao.add_series(new_series)
        if new_series_added and series_form.submit_close.data:
            flash(f'The series "{series_form.title.data}" has been created successfully!', "success")
            return redirect(url_for("uploads"))
        if new_series_added and series_form.submit_addep.data:
            new_series_id = dao.get_latest_added_id()
            return redirect(url_for("upload_episode", series_id=new_series_id))
        series_form.title.errors.append("Series creation failed, please try again!")   
    return render_template("create_series.html", form=series_form)

@app.route("/<int:series_id>/upload-episode", methods=['GET', 'POST'])
def upload_episode(series_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in as a Creator to upload an episode to a series of podcasts!", "warning")
        return redirect(url_for("login"))
    if current_user.type != "Creator":
        flash("Only Creators can upload episodes to a series of podcasts!", "warning")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    series_in_db = dao.element_already_in_db("series", "series_id", series_id)
    if not series_in_db:
        flash("This series of podcasts does not exist!", "error")
        return redirect(url_for("create_series"))
    if current_user.username != series_in_db["username"]:
        flash("You can upload episodes only to your own series!", "error")
        return redirect(url_for("home"))
    episode_form = EpisodeForm()
    if episode_form.validate_on_submit():        
        if episode_form.date.data > date.today():
            episode_form.date.errors.append("You cannot set a date greater than today's!")
            return render_template("upload_episode.html", form=episode_form, series=series_in_db)
        input_date = episode_form.date.data.strftime("%d-%m-%Y")
        input_title = episode_form.title.data
        input_description = episode_form.description.data
        input_audio = episode_form.audiofile.data
        filename = secure_filename(input_audio.filename)
        audiofile_in_db = dao.element_already_in_db("episodes", "audiofile", filename)
        if audiofile_in_db:
            episode_form.audiofile.errors.append("This audio file has already been used, please try again!")
            return render_template("upload_episode.html", form=episode_form, series=series_in_db)
        input_audio.save(f"static\\audiofiles\episodes\{filename}")
        new_episode = {"title": input_title, "description": input_description, "date": input_date, "audiofile": filename, "series_id": series_id}
        new_episode_added = dao.add_episode(new_episode)
        if new_episode_added and episode_form.submit_close.data:
            flash(f'The episode "{episode_form.title.data}" has been uploaded successfully!', "success")
            return redirect(url_for("uploads"))
        if new_episode_added and episode_form.submit_addep.data:
            flash(f'The episode "{episode_form.title.data}" has been uploaded successfully!', "success")
            return redirect(url_for("upload_episode", series_id=series_id))
        episode_form.title.errors.append("Episode creation failed, please try again!")
    return render_template("upload_episode.html", form=episode_form, series=series_in_db)

@app.route("/<int:series_id>/follow")
def follow_series(series_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to follow a series of podcasts!", "warning")
        return redirect(url_for("login"))
    series_in_db = dao.element_already_in_db("series", "series_id", series_id)
    if not series_in_db:
        flash("This series of podcasts does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    if current_user.username == series_in_db["username"]:
        flash("You cannot follow your own series!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    already_following = dao.user_follows_series(current_user.username, series_id)
    if already_following:
        unfollow = dao.unfollow_series(current_user.username, series_id)
        if not unfollow:
            flash(f'The series {series_in_db["title"]} could not be unfollowed, please try again.', "error")
    else:
        follow = dao.follow_series(current_user.username, series_id)
        if not follow:
            flash(f'The series {series_in_db["title"]} could not be followed, please try again.', "error")
    if "url" in session:
        return redirect(session["url"])
    return redirect(url_for("home"))

@app.route("/following")
def following():
    session["url"] = request.path
    if not current_user.is_authenticated:
        flash("You need to be logged in to follow a series of podcasts!", "warning")
        return redirect(url_for("login"))
    follows_any = dao.get_any_by_username(current_user.username, "follows")
    if not follows_any:
        flash("Once you start following other users' series they'll appear here!", "info")
        return render_template("index.html", series=[], episodes=[])
    return render_template("index.html", series=dao.get_all_by_series_id(current_user.username, "series", "follows", "series_id", "DESC"), episodes=dao.get_all_by_series_id(current_user.username,"episodes", "follows", "date", "ASC"))

@app.route("/uploads")
def uploads():
    session["url"] = request.path
    if not current_user.is_authenticated:
        flash("You need to be logged in as a Creator to upload a series of podcasts!", "warning")
        return redirect(url_for("login"))
    if current_user.type != "Creator":
        flash("Only Creators can upload series of podcasts!", "warning")
        return redirect(url_for("home"))
    series_form = SeriesForm()
    created_any = dao.get_any_by_username(current_user.username, "series")
    if not created_any:
        flash("Once you start creating series of podcasts they'll appear here!", "info")
        return render_template("index.html", series=[], episodes=[])
    return render_template("index.html", series=dao.get_all_by_series_id(current_user.username, "series", "series", "series_id", "DESC"), episodes=dao.get_all_by_series_id(current_user.username,"episodes", "series", "date", "ASC"), series_form=series_form)

@app.route("/explore/<category>")
def explore(category):
    session["url"] = request.path
    series_form, followed_series_ids = False, []
    if current_user.is_authenticated:
        series_form = SeriesForm()
        followed_series_ids = dao.get_all_followed_ids(current_user.username)
    return render_template("index.html", series=dao.get_all_by_category(category, "series", "series_id", "DESC"), episodes=dao.get_all_by_category(category, "episodes", "date", "ASC"), followed_series=followed_series_ids, series_form=series_form)

@app.route("/episode/<episode_id>", methods=['GET', 'POST'])
def episode(episode_id):    
    episode_in_db = dao.element_already_in_db("episodes", "episode_id", episode_id)
    if not episode_in_db:
        flash("This podcast episode does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    session["url"] = request.path
    followed, comment_form, episode_form = False, False, False
    episode_series = dao.get_series_by_episode_id(episode_id)
    if current_user.is_authenticated:
        if current_user.username == episode_series["username"]:
            episode_form = EpisodeForm()
            episode_form.title.data = episode_in_db["title"]
            episode_form.description.data = episode_in_db["description"]
        followed = dao.user_follows_series_by_episode_id(episode_id, current_user.username)
        comment_form = CommentForm()
        if comment_form.validate_on_submit():
            input_text = comment_form.text.data
            comment_form.text.data = None
            new_comment = {"text": input_text, "episode_id": episode_id, "series_id": episode_series["series_id"], "username": current_user.username}
            new_comment_added = dao.add_comment(new_comment)
            if new_comment_added:
                return redirect(session["url"])
            comment_form.text.errors.append("Comment creation failed, please try again!")           
    episode_comments = dao.get_comments_by_episode_id(episode_id)
    return render_template("episode.html", e=episode_in_db, s=episode_series, followed=followed, comment_form=comment_form, episode_form=episode_form, comments=episode_comments)

@app.route("/<int:comment_id>/delete-comment")
def delete_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to leave and delete comments!", "warning")
        return redirect(url_for("login"))
    comment_in_db = dao.element_already_in_db("comments", "comment_id", comment_id)
    if not comment_in_db:
        flash("This comment does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    if current_user.username != comment_in_db["username"]:
        flash("You cannot delete someone else's comment!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    comment_deleted = dao.delete_from_table_by_id("comments", "comment_id", comment_id)
    if not comment_deleted:
        flash(f'The comment {comment_in_db["text"]} could not be deleted, please try again.', "error")
    if "url" in session:
        return redirect(session["url"])
    return redirect(url_for("home"))

@app.route("/<int:episode_id>/delete-episode")
def delete_episode(episode_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to upload and delete podcast episodes!", "warning")
        return redirect(url_for("login"))
    episode_in_db = dao.element_already_in_db("episodes", "episode_id", episode_id)
    if not episode_in_db:
        flash("This podcast episode does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    episode_series = dao.get_series_by_episode_id(episode_id)
    if current_user.username != episode_series["username"]:
        flash("You cannot delete someone else's episode!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    comments_deleted = dao.delete_from_table_by_id("comments", "episode_id", episode_id)
    if not comments_deleted:
        flash(f'The episode {episode_in_db["title"]} could not be deleted, please try again.', "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("uploads"))
    try:
        os.remove(f"static\\audiofiles\episodes\{episode_in_db['audiofile']}")    
    except:
        flash(f'The episode {episode_in_db["title"]} could not be deleted, please try again.', "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("uploads"))
    episode_deleted = dao.delete_from_table_by_id("episodes", "episode_id", episode_id)
    if not episode_deleted:
        flash(f'The episode {episode_in_db["title"]} could not be deleted, please try again.', "error")
        if "url" in session:
            return redirect(session["url"])
    else:
        flash(f'The episode {episode_in_db["title"]} has been deleted successfully!', "success")
    return redirect(url_for("uploads"))

@app.route("/<int:series_id>/delete-series")
def delete_series(series_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to create and delete series of podcasts!", "warning")
        return redirect(url_for("login"))
    series_in_db = dao.element_already_in_db("series", "series_id", series_id)
    if not series_in_db:
        flash("This series of podcasts does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    if current_user.username != series_in_db["username"]:
        flash("You cannot delete someone else's series!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    comments_deleted = dao.delete_from_table_by_id("comments", "series_id", series_id)
    if not comments_deleted:
        flash(f'The series {series_in_db["title"]} could not be deleted, please try again.', "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("uploads"))
    audiofiles = dao.get_audiofiles_by_series_id(series_id)
    for file in audiofiles:
        try:
            os.remove(f"static\\audiofiles\episodes\{file}")    
        except:
            flash(f'The series {series_in_db["title"]} could not be deleted, please try again.', "error")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("uploads"))
    episodes_deleted = dao.delete_from_table_by_id("episodes", "series_id", series_id)
    if not episodes_deleted:
        flash(f'The series {series_in_db["title"]} could not be deleted, please try again.', "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("uploads"))
    try:
        os.remove(f"static\images\series\{series_in_db['image']}")    
    except:
        flash(f'The eseries {series_in_db["title"]} could not be deleted, please try again.', "error")
        return redirect(url_for("uploads"))
    followed_series_deleted = dao.delete_from_table_by_id("follows", "series_id", series_id)
    episodes_deleted = dao.delete_from_table_by_id("series", "series_id", series_id)
    if not followed_series_deleted or not episodes_deleted:
        flash(f'The series {series_in_db["title"]} could not be deleted, please try again.', "error")
    else:
        flash(f'The series {series_in_db["title"]} has been deleted successfully!', "success")
    return redirect(url_for("uploads"))

@app.route("/<int:comment_id>/edit-comment", methods=['GET', 'POST'])
def edit_comment(comment_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to leave and edit comments!", "warning")
        return redirect(url_for("login"))
    comment_in_db = dao.element_already_in_db("comments", "comment_id", comment_id)
    if not comment_in_db:
        flash("This comment does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    if current_user.username != comment_in_db["username"]:
        flash("You cannot edit someone else's comment!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        input_text = comment_form.text.data
        comment_edited = dao.edit_comment(comment_id, input_text)
        if not comment_edited:
            flash("Comment modification failed, please try again!", "error")
    else:
        flash("Please insert a valid comment!", "error")
    if "url" in session:
        return redirect(session["url"])
    return redirect(url_for("home"))

@app.route("/<int:episode_id>/edit-episode", methods=['GET', 'POST'])
def edit_episode(episode_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to upload and edit podcast episodes!", "warning")
        return redirect(url_for("login"))
    episode_in_db = dao.element_already_in_db("episodes", "episode_id", episode_id)
    if not episode_in_db:
        flash("This podcast episode does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    episode_series = dao.get_series_by_episode_id(episode_id)
    if current_user.username != episode_series["username"]:
        flash("You cannot edit someone else's episode!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    episode_form = EpisodeForm()
    if episode_form.validate_on_submit():
        if episode_form.date.data > date.today():
            flash("You cannot set a date greater than today's, please try again!", "error")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("uploads"))
        input_date = episode_form.date.data.strftime("%d-%m-%Y")
        input_title = episode_form.title.data
        input_description = episode_form.description.data
        input_audio = episode_form.audiofile.data
        filename = secure_filename(input_audio.filename)
        try:
            os.remove(f"static\\audiofiles\episodes\{episode_in_db['audiofile']}")    
        except:
            flash(f'The episode {episode_in_db["title"]} could not be modified, please try again.', "error")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("uploads"))
        input_audio.save(f"static\\audiofiles\episodes\{filename}")
        new_episode = {"title": input_title, "description": input_description, "date": input_date, "audiofile": filename, "episode_id": episode_id}
        new_episode_edited = dao.edit_episode(new_episode)
        if not new_episode_edited:
            flash(f'The episode {episode_in_db["title"]} could not be modified, please try again.', "error")
    else:
        flash(f'Invalid data submitted, please try again.', "error")
    if "url" in session:
        return redirect(session["url"])
    return redirect(url_for("home"))

@app.route("/<int:series_id>/edit-series", methods=['GET', 'POST'])
def edit_series(series_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to create and edit series of podcasts!", "warning")
        return redirect(url_for("login"))
    series_in_db = dao.element_already_in_db("series", "series_id", series_id)
    if not series_in_db:
        flash("This series of podcasts does not exist!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    if current_user.username != series_in_db["username"]:
        flash("You cannot delete someone else's series!", "error")
        if "url" in session:
            return redirect(session["url"])
        return redirect(url_for("home"))
    series_form = SeriesForm()
    if series_form.validate_on_submit():
        input_title = series_form.title.data
        input_description = series_form.description.data
        input_category = series_form.category.data
        if input_category == "default":
            flash("Please insert a valid category!", "error")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("home"))
        input_image = series_form.image.data
        filename = secure_filename(input_image.filename)
        try:
            os.remove(f"static\images\series\{series_in_db['image']}")    
        except:
            flash(f'The eseries {series_in_db["title"]} could not be deleted, please try again.', "error")
            if "url" in session:
                return redirect(session["url"])
            return redirect(url_for("uploads"))
        input_image = Image.open(input_image)
        input_image = input_image.resize((int(input_image.width), int(input_image.width * 0.5625)))
        input_image.save(f"static\images\series\{filename}")
        new_series = {"title": input_title, "description": input_description, "category": input_category, "image": filename, "series_id": series_id}
        new_series_edited = dao.edit_series(new_series)
        if not new_series_edited:
            flash(f'The series {series_in_db["title"]} could not be modified, please try again.', "error")
    else:
        flash(f'Invalid data submitted, please try again.', "error")
    if "url" in session:
        return redirect(session["url"])
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)  
