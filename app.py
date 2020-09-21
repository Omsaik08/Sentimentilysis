from flask import Flask,render_template,request
import os
import smtplib
import string
import collections
import matplotlib.pyplot as plt
import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from csv import DictReader
plt.style.use('fivethirtyeight')
x=1

app=Flask(__name__)
@app.route('/')
def index():
    if os.path.isfile('D:/Flask/static/images/graph.png')==True:
        print("Yes")
        os.remove('D:/Flask/static/images/graph.png')
    return render_template('index.html',visitor_no=111111)

@app.route('/about')
def about():
    return render_template('about.html',visitor_no=111111)
   
@app.route('/classes')
def classes():
    return render_template('classes.html',visitor_no=111111,name="UserName",pos=0,neg=0,neu=0)
    
@app.route('/classes2')
def classes2():
    return render_template('classes2.html',no=1)
    
    
@app.route('/contact')
def contact():
    return render_template('contact.html',visitor_no=111111)
    
@app.route('/emotion',methods=['POST','GET'])
def emotion():
    
    if request.method=='POST':
        data=str(request.form['speech'].encode("utf-8"))
        lower_data=data.lower()
        cleaned_data=lower_data.translate(str.maketrans('','',string.punctuation))
        words=cleaned_data.split()
        
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
              "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
              "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these",
              "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
              "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while",
              "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before",
              "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
              "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each",
              "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
              "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
              
        final_words=[]

        #find the words which are not present in stop_words
        for word in words:
            if word not in stop_words:
                final_words.append(word)

        #NLP algorithm
        emotions=[]
        with open('emotions.txt','r') as f:
            for line in f:
                processed=line.replace("\n","").replace(",",'').replace("'",'').strip()
                #print(processed)
                word,emotion=processed.split(":")

                if word in final_words:
                    emotions.append(emotion)

        count=collections.Counter(emotions)
        #print(emotions)
        #print(count)
        demo=dict()
        x=sum(count.values())
        for i,j in count.items():
            demo[i]=round((j*100)/x)
        print(demo)
        final_Emotion=""

        for key in demo:
            final_Emotion=key

        if(final_Emotion==""):
            return render_template('classes2.html',no=3)
        else:
            print(final_Emotion.strip())
        return render_template('classes2.html',no=2,count=demo)
    return render_template('classes2.html',no=1)
    
    
@app.route('/email',methods=['POST','GET'])
def email():
    if request.method=='POST':
        sender="Sentimentilysis@gmail.com"
        password="Sentimentilysis@1"
        reciever="omsaikalekar2000@gmail.com"
        
        message="First Name: "+request.form['fname']+"\n"
        message=message+"Mail: "+request.form['mail']+"\n"
        message=message+"Phone Number: "+request.form['phone']+"\n"
        message=message+"Message: "+request.form['message']+"\n"
        
        FROM = sender
        TO = reciever
        SUBJECT = "Analysis"
        TEXT = message

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
        message2="Hello,\n\nGreetings Of the Day!\n\nThank you for connecting with us,we have got your message,Our Admin will reply you soon!\n\n\n\nRegards,\nTeam Sentimentilysis"
        messagemain="""From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, message2)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(sender, password)
            server.sendmail(FROM, TO, message)
            server.sendmail(FROM, request.form['mail'],messagemain)
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")
        return render_template('contact.html')
    
@app.route('/sentiment',methods=['POST','GET'])
def sentiment():
    if request.method=='POST':
        
        l=[]
        with open('Login.csv', 'r') as read_obj:
            csv_dict_reader = DictReader(read_obj)
            for row in csv_dict_reader:
                l.append(row['Key'])
            
        consumerKey=l[0]
        consumersecret=l[1]
        accessToken=l[2]
        accessTokenSecret=l[3]  

        #authenticate
        authenticate = tweepy.OAuthHandler(consumerKey,consumersecret)
        authenticate.set_access_token(accessToken,accessTokenSecret)
        api=tweepy.API(authenticate,wait_on_rate_limit=True)
        
        #taking first 5 tweets
        posts=api.user_timeline(screen_name=str(request.form['fname']) ,count=int(request.form['total']), lang="en" ,tweet_mode="extended")
        if len(posts)==0:
            return render_template('classes.html',st="Invalid")
        df=pd.DataFrame([tweet.full_text for tweet in posts],columns=['Tweets'])
        
        
        
        #cleaning data

        df['Tweets']=df['Tweets'].apply(clean)
        

        df['Subjectivity']=df['Tweets'].apply(subjectivity)
        df['Polarity']=df['Tweets'].apply(polarity)
        
        
        allwords=' '.join([twt for twt in df['Tweets']])
        wordcloud = WordCloud(width=500,height=300,random_state=21,max_font_size=119).generate(allwords)
        #plt.imshow(wordcloud,interpolation="bilinear")
        #plt.axis("off")
        #plt.show()
  
        df['Analysis']=df['Polarity'].apply(CheckAnalysis)
        
        
        #percentage of positive twt
        positive_twt=df[df.Analysis =='Positive']
        positive_twt=positive_twt['Tweets']

        pos=round((positive_twt.shape[0]/df.shape[0])*100, 1)
        
        #percentage of negative twt
        negative_twt=df[df.Analysis =='Negative']
        negative_twt=negative_twt['Tweets']

        neg=round((negative_twt.shape[0]/df.shape[0])*100, 1)
        
        neu=100-pos-neg
        #show values

        #df['Analysis'].value_counts()
        #plt.title("Sentiment Analysis")
        #plt.xlabel("Sentiment")
        #plt.ylabel("Count")
        #df['Analysis'].value_counts().plot(kind=str(request.form['chart']))
        #plt.show()
   
    return render_template('classes.html',name=request.form['fname'],pos=pos,neg=neg,neu=neu)

def clean(text):
    text=re.sub(r'@[A-Za-z0-9]','',text)
    text=re.sub(r'#','',text)
    text=re.sub(r'RT[\s]+','',text)
    text=re.sub(r'https?:\/\/\S+','',text)
    return text
  
#subjectivity
def subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

#polarity
def polarity(text):
    return TextBlob(text).sentiment.polarity
  

#getAnalysis
def CheckAnalysis(score):
    if score>0:
        return "Positive"
    elif score<0:
        return "Negative"
    else:
        return "Neutral"

try:
    if __name__=='__main__':
        app.run(debug=True)
except:
    print("danger")