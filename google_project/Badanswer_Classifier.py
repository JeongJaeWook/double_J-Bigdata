# -*- coding: utf-8 -*-
"""불량응답 분류모델.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10iZS3E2IXcqrvZQTjgoJ-Ny9y_kgf6FS
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
# %matplotlib inline

"""Let's read the data from csv file"""

df = pd.read_excel('2019 google BAD sample(1-12).xlsx',sheet_name=0,usecols='A,B,C')
df.columns = ['ID','label','C1']

df.head()

"""Let's look into our data"""

df.groupby('label').size()

print(df.isnull().sum())

"""Now let's create new feature "message length" and plot it to see if it's of any interest"""

#응답에 숫자도 있어서 int 형으로 생각함 -> 문자형으로 변환
df['C1'] = df['C1'].apply(str)

# df['length'] = df['C1'].str.len()
df['length'] = df['C1'].apply(len)

#중복 제거
df.drop_duplicates(subset=['C1'],inplace=True) # C1 열에서 중복인 내용이 있다면 중복 제거
df.head()

df.info()

mpl.rcParams['patch.force_edgecolor'] = True
plt.style.use('seaborn-bright')
df.hist(column='length', by='label', bins=50,figsize=(11,5))

"""Looks like the lengthy is the message, more likely it is a spam. Let's not forget this

### Text processing and vectorizing our meddages

Let's create new data frame. We'll need a copy later on
"""

text_feat = df['C1'].copy()
text_feat.head()

"""Now define our tex precessing function. It will remove any punctuation and stopwords aswell."""

def text_process(text):
    
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = [word for word in text.split() if word.lower() not in stopwords.words()]
    
    return " ".join(text)

#처음 다운로드할때만
import nltk
nltk.download('stopwords')

text_feat = text_feat.apply(text_process)

# text_feat = text_feat.str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
# text_feat=text_feat.dropna(how = 'any') 
# print(text_feat.isnull().values.any()) 


# #한국어니까...영어는 삭제돼서 NULL로 됨.

# Null 값이 존재하는 행 제거.... 제거해야할까?? 
#삭제할경우 -> 불용어 처리를 하다보면 NULL값이 될 수 있는데 불량응답을 나중에 걸러낼 수 있을까? 
#삭제를 안할경우 -> Null 값도 불량응답으로 훈련할텐데 전체베이스가 아닌 오픈문항에서 비포함 케이스도 불량응답으로 처리하지 않을까?

#벡터화
vectorizer = TfidfVectorizer()

# #TfidfVectorizer()
# 등장횟수도 많고 문서 분별력 있는 단어들을 스코어링한 것

# #장점
# 선택된 단어는 TF-IDF 스코어를 가지며 어떤 단어가 중요한 단어인지 직관적으로 해석이 가능하며, 
# 전처리(pos-of-tagging)가 잘 수행 되었을때 다른 변수선택/추출보다 견줄만한 성능을 가지고 있다.

# #단점
# 제외된 단어들은 학습에 사용되지 않기 때문에 새로운 단어에 대한 해석이 불가능 
# 순서를 고려하지 않기 때문에 어순에 대한 문법적인 의미를 담고 있지 않는다.

features = vectorizer.fit_transform(text_feat)

"""###  Classifiers and predictions

First of all let's split our features to test and train set
"""

features_train, features_test, labels_train, labels_test = train_test_split(features, df['label'], test_size=0.3, random_state=111)

"""Now let's import bunch of classifiers, initialize them and make a dictionary to itereate through"""

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score

svc = SVC(kernel='sigmoid', gamma=1.0)
knc = KNeighborsClassifier(n_neighbors=49)
mnb = MultinomialNB(alpha=0.2)
dtc = DecisionTreeClassifier(min_samples_split=7, random_state=111)
lrc = LogisticRegression(solver='liblinear', penalty='l1')
rfc = RandomForestClassifier(n_estimators=31, random_state=111)
abc = AdaBoostClassifier(n_estimators=62, random_state=111)
bc = BaggingClassifier(n_estimators=9, random_state=111)
etc = ExtraTreesClassifier(n_estimators=9, random_state=111)

"""Parametres are based on notebook:
[Spam detection Classifiers hyperparameter tuning][1]


  [1]: https://www.kaggle.com/muzzzdy/d/uciml/sms-spam-collection-dataset/spam-detection-classifiers-hyperparameter-tuning/
"""

clfs = {'SVC' : svc,'KN' : knc, 'NB': mnb, 'DT': dtc, 'LR': lrc, 'RF': rfc, 'AdaBoost': abc, 'BgC': bc, 'ETC': etc}

"""Let's make functions to fit our classifiers and make predictions"""

def train_classifier(clf, feature_train, labels_train):    
    clf.fit(feature_train, labels_train)

def predict_labels(clf, features):
    return (clf.predict(features))

"""Now iterate through classifiers and save the results"""

pred_scores = []
for k,v in clfs.items():
    train_classifier(v, features_train, labels_train)
    pred = predict_labels(v,features_test)
    pred_scores.append((k, [accuracy_score(labels_test,pred)]))

# 오류 : DataFrame.from_items
# df = pd.DataFrame.from_items(pred_scores,orient='index', columns=['Score'])
score=pd.DataFrame.from_dict(dict(pred_scores),orient='index',columns=['Score'])
score

score.plot(kind='bar', ylim=(0.3,1.0), figsize=(11,6), align='center', colormap="Accent")
plt.xticks(np.arange(9), df.index)
plt.ylabel('Accuracy Score')
plt.title('Distribution by Classifier')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

"""Looks like ensemble classifiers are not doing as good as expected.

### Stemmer

It is said that stemming short messages does no goot or even harm predictions. Let's try this out.

Define our stemmer function
"""

# 현재 오픈문항이 단답형이기 때문에 어간추출 생략함

# def stemmer (text):
#     text = text.split()
#     words = ""
#     for i in text:
#             stemmer = SnowballStemmer("Korean")
#             words += (stemmer.stem(i))+" "
#     return words

# text_feat = text_feat.apply(stemmer)

#대신 벡터라이즈를 수정
# CountVectorizer() : 
# 가장 단순한 특징으로, 텍스트에서 단위별 등장횟수를 카운팅하여 수치벡터화
# 특별한 의미를 지니지 않는데 자주 사용되는 단어가 높은 가중을 가질 수 있음

from sklearn.feature_extraction.text import CountVectorizer
vectorizer2 = CountVectorizer(min_df=1)

features = vectorizer2.fit_transform(text_feat)

features_train, features_test, labels_train, labels_test = train_test_split(features, df['label'], test_size=0.3, random_state=111)

pred_scores = []
for k,v in clfs.items():
    train_classifier(v, features_train, labels_train)
    pred = predict_labels(v,features_test)
    pred_scores.append((k, [accuracy_score(labels_test,pred)]))

# df2 = pd.DataFrame.from_items(pred_scores,orient='index', columns=['Score2'])
score2 = pd.DataFrame.from_dict(dict(pred_scores),orient='index', columns=['Score2'])
score = pd.concat([score,score2],axis=1)
score

score.plot(kind='bar', ylim=(0.3,1.0), figsize=(11,6), align='center', colormap="Accent")
plt.xticks(np.arange(9), df.index)
plt.ylabel('Accuracy Score')
plt.title('Distribution by Classifier')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

#보통 2개를 분류하는 케이스에서는 활성화함수를 'relu'씀.

import keras
from keras.layers import Dense
from keras.models import Sequential

#모델구성
model = Sequential()
model.add(Dense(units = 100 , activation = 'relu' , input_dim = features_train.shape[1]))
model.add(Dense(units = 50 , activation = 'relu'))
model.add(Dense(units = 25 , activation = 'relu'))
model.add(Dense(units = 10 , activation = 'relu'))
model.add(Dense(units = 1 , activation = 'sigmoid'))
model.compile(optimizer = 'adam' , loss = 'binary_crossentropy' , metrics = ['accuracy'])
model.summary()

#모델훈련
y_test = np.array(labels_train) #array로 바꿔줘야한다고 함 ...
model.fit(features_train,y_test , epochs = 5)

pred = model.predict(features_test)

print(accuracy_score(labels_test,pred.round()))

"""Looks like mostly the same . Ensemble classifiers doing a little bit better, NB still got the lead.

### What have we forgotten? Message length!

Let's append our message length feature to the matrix we fit into our classifiers
"""

# 오류 : as_matrix()
# lf = sms['length'].as_matrix()
lf =df['length'].values
newfeat = np.hstack((features.todense(),lf[:, None]))

features_train, features_test, labels_train, labels_test = train_test_split(newfeat, df['label'], test_size=0.3, random_state=111)
features_test

pred_scores = []
for k,v in clfs.items():
    train_classifier(v, features_train, labels_train)
    pred = predict_labels(v,features_test)
    pred_scores.append((k, [accuracy_score(labels_test,pred)]))

# df3 = pd.DataFrame.from_items(pred_scores,orient='index', columns=['Score3'])
score3 = pd.DataFrame.from_dict(dict(pred_scores),orient='index', columns=['Score3'])
score = pd.concat([score,score3],axis=1)
score

score.plot(kind='bar', ylim=(0.7,1.0), figsize=(11,6), align='center', colormap="Accent")
plt.xticks(np.arange(9), df.index)
plt.ylabel('Accuracy Score')
plt.title('Distribution by Classifier')
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

"""This time everyone are doing a little bit worse, except for LinearRegression and RandomForest. But the winner is still MultinominalNaiveBayes.

### Voting classifier

We are using ensemble algorithms here, but what about ensemble of ensembles? Will it beat NB?
"""

from sklearn.ensemble import VotingClassifier

eclf = VotingClassifier(estimators=[('BgC', bc), ('ETC', etc), ('RF', rfc), ('Ada', abc)], voting='soft')

eclf.fit(features_train,labels_train)

pred = eclf.predict(features_test)

print(accuracy_score(labels_test,pred))

#모델 저장
from sklearn.linear_model import LogisticRegression
from sklearn import datasets
import pickle
from sklearn.externals import joblib


#GBoost 자리에 최적 모델쓰면돼요
with open('filename11.pkl', 'wb') as file:  
    pickle.dump(eclf, file)

#데이터에 적용하기

ap_data = pd.read_excel('AP open data_20201111.xlsx',sheet_name=0,usecols='A,B,C')
ap_data = ap_data[:]

ap_data.columns = ['ID','label','C1']
ap_data['C1'] = ap_data['C1'].apply(str)
ap_data['length'] = ap_data['C1'].apply(len)
ap_data.head()

google_2020 = pd.read_excel('2020 google BAD sample(1-9).xlsm',sheet_name=0,usecols='A,B,C')
google_2020.columns = ['ID','label','C1']
google_2020['C1'] = google_2020['C1'].apply(str)
google_2020.drop_duplicates(subset=['C1'],inplace=True) # C1 열에서 중복인 내용이 있다면 중복 제거
google_2020['length'] = google_2020['C1'].apply(len)

google_x_test = google_2020['C1']
google_x_test = google_x_test.apply(text_process)
google_2020.info()

# pred = model.predict(features_test)
# print(accuracy_score(labels_test,pred.round()))

google_x_test2 = google_x_test
google_x_features = vectorizer2.fit_transform(google_x_test2)
data = np.expand_dims(np.asarray(google_x_features), axis=0)
google_y_test = np.array(google_2020['label'])

pred = eclf.predict(google_x_features.reshape(-1,1))

1. 분류별로 모델 생성
2. 통합 모델