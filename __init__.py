from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passwordHasher import passwordHasher

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

username = None

# Define the database tables
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.password}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


def checkUser(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if passwordHasher.check(password, user.password):
            return True
        else:
            return False
    else:
        return False

@app.route("/")
def index():
    posts = Post.query.all()
    posts.reverse()

    if "user" in session:
        username = session["user"]
        return render_template("blog.html",title="Blog", posts=posts, username=username)
    return render_template("blog.html", title="Blog", posts=posts, username=None)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        if checkUser(name, password):
            session["user"] = name
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))


    else:
        if "user" in session:
            flash("You are already logged in", "info")
        return render_template("login.html", title="Login", username=session.get("user"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/user/<userinfo>", methods=["GET", "POST"])
def user(userinfo):
    if User.query.filter_by(username=userinfo).first():
        userid = User.query.filter_by(username=userinfo).first().id
        userposts = Post.query.filter_by(user_id=userid).all()
        username = session.get("user")

        return render_template("user.html", title="User", userinfo=userinfo, userid=userid, userposts=len(userposts), username=username)
    else:
        return render_template("error.html", title="404")

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if "user" in session:

        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            content = content.replace("\n", "<br>")

            if content == "" or title == "":
                flash("Please fill in all fields!", "error")
                return redirect(url_for("admin"))
            else:
                user = User.query.filter_by(username=session.get("user")).first()

                post = Post(title=title, content=content, user_id= user.id )
                db.session.add(post)
                db.session.commit()

                return redirect(url_for("index"))
        else:
            return render_template("admin.html", title="Admin")
    else:
        flash("You need to be logged in to view this page", "error")
        return redirect(url_for("login"))

@app.route("/settings")
def settings():
    if "user" in session:
        username = session.get("user")
        user = User.query.filter_by(username=username).first()

        return render_template("settings.html", title="Settings", username=username, posts_len=len(user.posts), user_posts=user.posts)

    else:
        flash("You need to be logged in to view this page", "error")
        return redirect(url_for("login"))


@app.route("/delete/<postid>")
def delete(postid):
    if "user" in session:
        try:
            post = Post.query.filter_by(id=postid).first()
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for("index"))
        except:
            return render_template("error.html", title="404")
    else:
        flash("You need to be logged in to view this page", "error")
        return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", title="404"), 404

if __name__ == "__main__":
    app.run(debug=True)
