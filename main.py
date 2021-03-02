import os
from datetime import datetime as dt

from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


from forms import CreatePostForm, CreateUserForm, LoginForm, CommentForm
from models import db, BlogPost, Users, Comments

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

##Initialise Fask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#Create custom decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function

##Initialise Bootstrap & ckeditor
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
file_path = os.path.abspath(os.getcwd()) + "\posts.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# Instead of using db = SQLAlchemy(app), becos models are placed in separate module, code below used instead
db.init_app(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = CreateUserForm()
    if form.validate_on_submit():
        if Users.query.filter_by(email=form.email.data).first():
            flash("You have already registered. Please login instead.")
            return redirect(url_for("login"))
        else:
            user_hash = generate_password_hash(form.password.data,
                        method='pbkdf2:sha256', salt_length=8)

            new_user = Users(email=form.email.data,
                                password=user_hash,
                                name=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = Users.query.filter_by(email=email).first()

        if not user:
            flash("You have entered an invalid email. Try again, or register as a new user.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("You have entered an invalid password")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("get_all_posts"))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:index>", methods=["GET", "POST"])
@login_required
def show_post(index):
    form = CommentForm()
    requested_post = BlogPost.query.get(index)
    if form.validate_on_submit():
        new_text = Comments(body=form.body.data,
                         user_id=current_user.id,
                         post_id=requested_post.id)
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for('show_post', index=requested_post.id))
    return render_template("post.html", post=requested_post, logged_in=current_user.is_authenticated, form=form)


@app.route('/new-post', methods=["GET", "POST"])
@admin_only
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post_date = dt.today().strftime("%B %d, %Y")
        new_post = BlogPost(title=form.title.data,
                            subtitle=form.subtitle.data,
                            date=post_date,
                            author=current_user.name,
                            user_id=current_user.id,
                            img_url=form.img_url.data,
                            body=form.body.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form=form, title="New Post",
                           submit="Submit Post", logged_in=current_user.is_authenticated)


@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    edit_post = BlogPost.query.get(post_id)
    #this populates the form with the post to be edited data
    form = CreatePostForm(
        title=edit_post.title,
        subtitle=edit_post.subtitle,
        img_url=edit_post.img_url,
        body=edit_post.body)
    if form.validate_on_submit():
        edit_post.title = form.title.data
        edit_post.subtitle = form.subtitle.data
        edit_post.img_url = form.img_url.data
        edit_post.body = form.body.data
        db.session.commit()
        return redirect(url_for("show_post", index=edit_post.id))
    return render_template("make-post.html", submit="Edit Post",
                           form=form, title="Edit Post", is_edit=True, index=edit_post.id,
                           logged_in=current_user.is_authenticated)


@app.route("/delete/<int:index>")
@admin_only
def delete_post(index):
    requested_post = BlogPost.query.get(index)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)