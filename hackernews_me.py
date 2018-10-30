from bottle import route, run, template, request, redirect
from scraputils_me import get_news
from db_me import News, session
from bayes_me import NaiveBayesClassifier
import string


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    label, id = request.query.label, request.query.id
    s = session()
    s.query(News).filter(News.id == id).update({'label': label})
    s.commit()
    redirect("/news")


@route("/update")
def update_news():

    news = get_news('https://news.ycombinator.com')
    s = session()

    for post in news:
        if s.query(News).filter(News.title == post['title'],
                                News.author == post['author']).first():
            break
        else:
            s.add(News(**post))
    s.commit()
    redirect("/news")


@route('/recomendations')
def recomendations():
    rows = s.query(News).filter(News.label == None).all()
    good_news = []
    for row in rows:
        [prediction] = model.predict([clean(row.title).lower()])
        if prediction == 'good':
            good_news.append(row)
    maybe_news = []
    for row in rows:
        [prediction] = model.predict([clean(row.title).lower()])
        if prediction == 'maybe':
            maybe_news.append(row)
    never_news = []
    for row in rows:
        [prediction] = model.predict([clean(row.title).lower()])
        if prediction == 'never':
            never_news.append(row)
    return template('news_recomendation', good_rows=good_news, maybe_rows=maybe_news, never_rows=never_news)

def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)


if __name__ == "__main__":
    s = session()
    rows = s.query(News).filter(News.label != None).all()
    X_train = [clean(row.title).lower() for row in rows]
    y_train = [row.label for row in rows]
    model = NaiveBayesClassifier()
    model.fit(X_train, y_train)
    run(host="localhost", port=8080)