from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, RadioField, SelectField, SubmitField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(message="Please insert a valid username!")], render_kw={"placeholder": "Insert your username", "autocomplete": "off"})
    name = StringField(label="Name", validators=[DataRequired(message="Please insert a valid name!")], render_kw={"placeholder": "Insert your name", "autocomplete": "off"})
    surname = StringField(label="Surname", validators=[DataRequired(message="Please insert a valid surname!")], render_kw={"placeholder": "Insert your surname", "autocomplete": "off"})
    password = PasswordField(label="New Password", validators=[DataRequired(message="Please insert a valid password!"), Length(min=6, message="Password must be at least six characters long!")], render_kw={"placeholder": "Insert a password of minimum six characters", "autocomplete": "off"})
    confirm  = PasswordField(label="Repeat Password", validators=[EqualTo(fieldname="password", message="Passwords don't match, please try again!")], render_kw={'placeholder': "Confirm your password", "autocomplete": "off"})
    type = RadioField(label="Choose the type you prefer!", choices=["Listener", "Creator"])
    submit = SubmitField(label="Sign up")

class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(message="Please insert a valid username!")], render_kw={"placeholder": "Insert your username", "autocomplete": "off"})
    password = PasswordField(label="Password", validators=[DataRequired(message="Please insert a valid password!")], render_kw={"placeholder": "Insert your password", "autocomplete": "off"})
    submit = SubmitField(label="Log in")

class SeriesForm(FlaskForm):
    title = StringField(label="Title",  validators=[DataRequired(message="Please insert a valid title!")], render_kw={"placeholder": "Insert the series' title", "autocomplete": "off"})
    description = TextAreaField(label="Description",  validators=[DataRequired(message="Please insert a valid description!")], render_kw={"placeholder": "Insert a brief description of the series", "autocomplete": "off"})
    category = SelectField(label="Category", choices=[("default", "Select a category"), ("arts-crafts", "Arts & Crafts"), ("audiobooks", "Audiobooks"), ("cooking", "Cooking"), ("education", "Education"), ("economy-finance", "Economy & Finance"), ("games-videogames", "Games & Videogames"), ("health-fitness", "Health & Fitness"), ("movies-entertainment", "Movies & Entertainment"), ("music", "Music"), ("news", "News"), ("science-technology", "Science & Technology"), ("sport", "Sport"), ("travelling", "travelling"), ("trending-topics", "Trending Topics")])
    image = FileField(label="Image", validators=[FileRequired(message="Please choose an image!"), FileAllowed(upload_set=["jpg", "png"], message="Invalid file extension: use .jpg or .png")], render_kw={"placeholder": "Choose an image for the series"}, description="Accepted file extensions are .jpg or .png. Tip: choose an horizontal image with aspect ratio 16:9 to avoid unwanted resizing.")
    submit_close = SubmitField(label="Save and go back")
    submit_addep = SubmitField(label="Save and upload an episode")

class EpisodeForm(FlaskForm):
    title = StringField(label="Title",  validators=[DataRequired(message="Please insert a valid title!")], render_kw={"placeholder": "Insert the episode's title", "autocomplete": "off"})
    description = TextAreaField(label="Description",  validators=[DataRequired(message="Please insert a valid description!")], render_kw={"placeholder": "Insert a brief description of the episode", "autocomplete": "off"})
    date = DateField(label="Date")
    audiofile = FileField(label="Audio file", validators=[FileRequired(message="Please choose an audio file!"), FileAllowed(upload_set=["mp3", "m4a", "wav"], message="Invalid file extension: use .mp3, .m4a or .wav")], render_kw={"placeholder": "Pick the audio file for the episode"}, description="Accepted file extensiona are .mp3, .m4a or .wav")
    submit_close = SubmitField(label="Save and go back")
    submit_addep = SubmitField(label="Save and upload another episode")

class CommentForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired(message="Please insert a valid comment!")], render_kw={"placeholder": "Leave a comment...", "autocomplete": "off"})
    submit = SubmitField(label="Send")
