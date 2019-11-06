import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
from wordcloud import STOPWORDS

#    app = Flask(__name__)

from flask import *
from flask import session
app = Flask(__name__)
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
#app.secret_key = 'shrenika'
tweets={}

class TwitterClient(object):
    def __init__(self):
        # keys and tokens from the Twitter Dev Console
        consumer_key = ''
        consumer_secret = ''
        access_token = '
        access_token_secret = ''

        # attempt authentication
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    # @app.after_request
    # def add_header(response):
    #     response.cache_control.max_age = 300
    #     return response

    def get_tweets(self, query, count):
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count, lang = 'en')

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

def visualize(p,hash):
    s = ['Positive', 'Negative', 'Neutral']
    piec = pd.Series(p, index=s, name="Sentimental Analysis")
    fig, ax = plt.subplots()
    piec.plot.pie(fontsize=14, autopct='%.2f', figsize=(6, 6));
    fig.savefig('static/'+hash+'.png')

def wordCloudGen(tweets,hash):
    comment_words = ' '
    stopwords = set(STOPWORDS)
    # iterate through the csv file
    for val in tweets:
        # typecaste each val to string
        val = str(val['text'])
        # split the value
        tokens = val.split()
        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()
        for words in tokens:
            comment_words = comment_words + words + ' '
    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=stopwords,
                          max_words=100,
                          min_font_size=10).generate(comment_words)
    # plot the WordCloud image
    fig, ax = plt.subplots()
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    #plt.show()
    wordcloud.to_file('static/word/'+hash+".png")

@app.route('/')
def main():
    app.config["CACHE_TYPE"] = "null"
    #cache.init_app(app)
    return render_template('home.html')

@app.route("/project", methods = ['POST', 'GET'])
def project():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    percent = []
    if request.method == 'POST':
        email = request.form['email']
    tweets = api.get_tweets(query = email , count = 25)
    # session[1] = "Shrenika Gada"
    # print(session[1])
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    nettweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    # percentage of positive tweets
    nums = 0
    percents = []
    str_data = "Positive = "
    data = (100*len(ptweets)/len(tweets))
    percents.append(data)
    nums+=data
    # picking negative tweets from tweets
    percent.append(str_data+str("{0:.2f}".format(data))+"%")
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    str_data = "Negative = "
    data = (100*len(ntweets)/len(tweets))
    percents.append(data)
    nums+=data
    percent.append(str_data + str("{0:.2f}".format(data))+"%")
    # percentage of neutral tweets
    str_data = "Neutral = "
    data1 = 100 - nums
    percent.append(str_data+str("{0:.2f}".format(data1))+"%")
    print(percent)
    percents.append(data1)
    visualize(percents,email)
    wordCloudGen(tweets,email)
    #img = os.path(app.config['UPLOAD_FOLDER'] + '/visualize.png')
    #return render_template("index.html", user_image=full_filename)
    return render_template('dest.html', percent = percent, hash=email+".png", name=email+"'s" , tweets = tweets)
#
# @app.route("/tweets")
# def tweets():
#     #if 'tweetsretrieved' in session:
#     tweet = session[1]
#     return render_template("tweets.html", tweets=tweet)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    #app.config['SESSION_TYPE'] = 'filesystem'
    #session.init_app(app)
    app.run(debug=True)
    main()
