from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
import operator
import os
import requests
import re
import nltk
from rq import Queue
from rq.job import Job
from worker import conn


#################
# configuration #
#################

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

q = Queue(connection=conn)

from models import *


##########
# helper #
##########

def count_and_save_words(url):

    errors = []

    try:
        print ("attempting to make request")
        r = requests.get(url)
    except:
        print ("unable to make request")
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    # text processing
    raw = BeautifulSoup(r.text).get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)

    # save the results
    try:
        print ("attempting to save to db")
        result = Result(
            url=url,
            result_all=raw_word_count,
            result_no_stop_words=no_stop_words_count
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        print ("failed to save to db")
        # this is where fail occurs
        errors.append("Unable to add item to database.")
        return {"error": errors}


##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        url = request.form['url']
        if 'http://' not in url[:7]:
            url = 'http://' + url
        job = q.enqueue(count_and_save_words, url)
        print(job.get_id())

    return render_template('index.html', results=results)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)
    # job = q.fetch_job(job_key)
    # print(job.get_id())

    if job.is_finished:
        print (str(job.result))
        return str(job.result), 200
    else:
        print ("not done")
        return "not done"


if __name__ == '__main__':
    app.debug = True
    app.run()