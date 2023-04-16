import os 
from flask import Flask,render_template,request,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pyshorteners
import validators

app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
path = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)


class ShortUrls(db.Model):
    __tablename__ = 'URLS'
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(20),unique=True, nullable=False)

    def __init__(self, original_url, short_url):
        self.original_url = original_url
        self.short_url = short_url
 
@app.route("/")
def home_page():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def result():
    if request.method == 'POST':
        url_received=request.form.get('url') 
        if validators.url(url_received):
            existing_url = ShortUrls.query.filter_by(original_url=url_received).first()
            if existing_url:
                return render_template("error.html", existing_url=existing_url.short_url)
            else:
                s = pyshorteners.Shortener()
                short_url = s.tinyurl.short(url_received)
                url = ShortUrls(original_url=url_received, short_url=short_url)
                db.session.add(url)
                db.session.commit()
                return render_template('result.html',short_url=short_url)
        else:
            flash('Please enter valid URL')
if __name__=='__main__':
    app.run(debug=True)
