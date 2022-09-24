import requests
from django.http import HttpResponse
from django.shortcuts import render
import sys
sys.path.append("..")
import nltk
nltk.download('stopwords')
nltk.download('punkt')
import sqlite3
import os
import re
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
import itertools
import logging
from typing import Optional, Dict, Union

from nltk import sent_tokenize, TweetTokenizer

import torch
from transformers import(
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# Create your views here.
from transformers import pipeline
from transformers.pipelines import SUPPORTED_TASKS

glo = {}
def say_hello(request):
    return render(request, 'hello.html')

def go_home(request):
    return render(request, 'home.html')

def teacher1(request):
    return render(request, 'teacher1.html')

def POST_crawl(request):
    text = request.POST["title"]
    context = {}
    context['text'] = text
    return render(request, 'jojo.html', context)

def question_generation(request):
    title = request.POST.get('title')
    text = request.POST["passage"]
    context = {}
    context['title'] = title
    context['text'] = text
    glo['now_title'] = title

    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()  # 建立 cursor 物件

    sqlstr = "select title from title"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        if title == row[0]:
            return render(request, 'teacher2.html', context)

    sqlstr = "CREATE TABLE IF NOT EXISTS title ('title' TEXT, 'passage' TEXT)"
    cursor.execute(sqlstr)
    sqlstr = "CREATE TABLE IF NOT EXISTS "+title+" ('id' TEXT,'A' TEXT ,'B' TEXT)"
    cursor.execute(sqlstr)

    from .pipelines import pipeline
    nlp = pipeline("multitask-qa-qg")
    results = nlp(text)
    num = len(results)
    ans = []
    qu = []
    n = 0
    sqlstr = "insert into title (title, passage)" \
             "values('" + title + "','" + text + "')"
    cursor.execute(sqlstr)
    conn.commit()

    for r in results:
        if r['answer'].startswith('<pad>'):  #若開頭是<pad>
            r['answer'] = r['answer'][6:]
        ans.append(r['answer'])
        qu.append(r['question'])
        sqlstr = "insert into "+title+" (id, A, B)" \
                 "values ('" + str(n) + "','" + r['question'] + "','" + r['answer'] + "')"
        cursor.execute(sqlstr)
        conn.commit()
        n = n + 1
    context['results'] = zip(range(n), qu, ans)
    context['num'] = num
    conn.close()
    return render(request, 'jojo.html', context)

def save_db(request):   #################沒用到
    conn = sqlite3.connect(os.path.dirname(__file__)+"\database01.db") #建立資料庫連線
    cursor = conn.cursor() #建立 cursor 物件
    #建立一個資料表
    sqlstr = "CREATE TABLE IF NOT EXISTS data ('A' TEXT ,'B' TEXT)"
    cursor.execute(sqlstr)
    # 新增一筆資料
    sqlstr = "insert into data values ('"+request.GET["A"]+"','"+request.GET["B"]+"')"
    cursor.execute(sqlstr)
    conn.commit()
    conn.close()
    return HttpResponse("新增資料成功!!")

def select_db(request):
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    glo['now_title'] = request.GET["choice_title"]
    title = glo['now_title']
    sqlstr = "select id,A,B from " + title
    cursor = cursor.execute(sqlstr)
    #S = "ID, 問題, 答案<br>"
    context = {}
    id = []
    q = []
    a = []
    for row in cursor:
        #S += row[0]+", "+row[1]+", "+row[2]+"<br>"
        id.append(row[0])
        q.append(row[1])
        a.append(row[2])
    context['results'] = zip(id, q, a)
    sqlstr = "select passage from title WHERE title = '" + title + "'"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        text = row[0]
    context['text'] = text
    conn.close()
    return render(request, "teacher_select.html", context)

def delete_db(request):                ######暫時沒用
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "delete from data where id like '"+request.GET["id"]+"'"
    cursor.execute(sqlstr)
    conn.commit()
    conn.close()
    return HttpResponse("刪除成功!!")

def delete_table(request):
    title = glo['now_title']
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "drop table "+title
    cursor.execute(sqlstr)
    conn.commit()
    sqlstr = "delete from title where title like '" + title + "'"
    cursor.execute(sqlstr)
    conn.commit()
    conn.close()
    return render(request, "teacher_choice.html")

def teacher_delete(request):
    return render(request, "teacher_delete.html")

def modify_db(request):
    context = {}
    title = glo['now_title']
    context['title'] = title
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    if request.GET["A"] == '' or request.GET["B"] == '':
        sqlstr = "delete from "+title+" where id like '"+request.GET["id"]+"'"
        cursor.execute(sqlstr)
    else:
        sqlstr = "update " + title + " set A='"+request.GET["A"]+"'where id like '"+request.GET["id"]+"'"
        cursor.execute(sqlstr)
        sqlstr = "update " + title + " set B='" + request.GET["B"] + "'where id like '" + request.GET["id"] + "'"
        cursor.execute(sqlstr)
    sqlstr = "select id,A,B from " + title + ""
    cursor = cursor.execute(sqlstr)
    id = []
    q = []
    a = []
    for row in cursor:
        id.append(row[0])
        q.append(row[1])
        a.append(row[2])
    context['results'] = zip(id, q, a)
    conn.commit()
    sqlstr = "select passage from title WHERE title = '" + title + "'"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        text = row[0]
    context['text'] = text
    conn.close()
    return render(request, "jojo.html", context)

def modify_second(request):
    context = {}
    title = glo['now_title']
    context['title'] = title
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select id,A,B from " + title + ""
    cursor = cursor.execute(sqlstr)
    id = []
    q = []
    a = []
    for row in cursor:
        id.append(row[0])
        q.append(row[1])
        a.append(row[2])
    context['results'] = zip(id, q, a)
    conn.commit()
    sqlstr = "select passage from title WHERE title = '" + title + "'"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        text = row[0]
    context['text'] = text
    conn.close()
    return render(request, "jojo.html", context)

def teacher_choice(requset):
    return render(requset, "teacher_choice.html")

def all_title(request):
    context = {}
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select title from title"
    cursor = cursor.execute(sqlstr)
    name = []
    for row in cursor:
        name.append(row[0])
    context['title'] = name
    return render(request, "all_title.html", context)


def login(request):
    return render(request, 'login.html')

def register(request):
    if request.GET['job'] == 'student':
        return render(request, 's_register.html')
    else:
        return render(request, 't_register.html')

# def t_register(request):     ####用不到
#     return render(request, 't_register.html')
#
# def s_register(request):     ####用不到
#     return render(request, 's_register.html')

def s_create_account(request):
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database02.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "CREATE TABLE IF NOT EXISTS account ('account' TEXT ,'password' TEXT ,'job' TEXT )"
    cursor.execute(sqlstr)
    sqlstr = "select account from account"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        if request.GET["account"] == row[0]:
            return render(request, 's_recreate_account.html')
    sqlstr = "insert into account values ('" + request.GET["account"] + "','" + request.GET["password"] + "','student')"
    cursor.execute(sqlstr)
    conn.commit()
    return render(request, 'login.html')

def t_create_account(request):
    if request.GET["verify"] != '0000':
        return render(request, 'wrong_verify.html')

    conn = sqlite3.connect(os.path.dirname(__file__) + "\database02.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "CREATE TABLE IF NOT EXISTS account ('account' TEXT ,'password' TEXT ,'job' TEXT )"
    cursor.execute(sqlstr)
    sqlstr = "select account from account"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        if request.GET["account"] == row[0]:
            return render(request, 't_recreate_account.html')
    sqlstr = "insert into account values ('" + request.GET["account"] + "','" + request.GET["password"] + "','teacher')"
    cursor.execute(sqlstr)
    conn.commit()
    return render(request, 'login.html')

def login_(request):
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database02.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select account,password,job from account"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        if request.GET['account'] == row[0] and request.GET['password'] == row[1]:
            if row[2] == 'teacher':
                return render(request, 'teacher_choice.html')
            else:
                glo['now_account'] = request.GET['account']
                return render(request, 'student_choice.html')
    return render(request, 're_login.html')

def view_account(request):     ####查看所有帳號
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database02.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select * from account"
    cursor = cursor.execute(sqlstr)
    S = 'account, password, job <br>'
    for row in cursor:
        S += row[0]+", "+row[1]+", "+row[2]+"<br>"
    return HttpResponse(S)

def s_all_title(request):
    context = {}
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select title from title"
    cursor = cursor.execute(sqlstr)
    name = []
    for row in cursor:
        name.append(row[0])
    context['title'] = name
    return render(request, "s_all_title.html", context)

def s_write(request):       ##出題目
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    glo['now_title'] = request.GET["choice_title"]
    title = glo['now_title']
    sqlstr = "select A,id from " + title
    cursor = cursor.execute(sqlstr)
    context = {}
    id = []
    q = []
    for row in cursor:
        q.append(row[0])
        id.append(row[1])
    context['results'] = zip(id, q)

    glo['now_id'] = id         ##存目前id用於接收答案(id = name)

    sqlstr = "select passage from title WHERE title = '" + title + "'"
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        text = row[0]
    context['text'] = text
    conn.close()
    return render(request, "s_answer.html", context)


def text_process(tweet):     ##答案前處理
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = re.sub(r'#', '', tweet)
    tokenizer = TweetTokenizer()
    tweet_tokenized = tokenizer.tokenize(tweet)
    stopwords_english = stopwords.words('english')
    tweet_processsed=[word for word in tweet_tokenized
    if word not  in stopwords_english and word not in
    string.punctuation]
    tweet_processsed_lower = []
    for word in tweet_processsed:
      word = word.lower()
      if word != 'the':
        tweet_processsed_lower.append(word)
    return tweet_processsed_lower


def answer_compared(request):
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database01.db")  # 建立資料庫連線
    cursor = conn.cursor()
    title = glo['now_title']
    id = glo['now_id']

    correct_ans = []
    sqlstr = "select B from " + title
    cursor = cursor.execute(sqlstr)
    for row in cursor:
        correct_ans.append(row[0])

    answer = zip(correct_ans,id)
    correct = 0
    RoW = []
    user_ans = []
    for corr_ans, i in answer:
        ans = request.GET[i]
        user_ans.append(ans)
        ans = text_process(ans)
        corr_ans = text_process(corr_ans)
        count = len(corr_ans)
        for c_a in corr_ans:
            for a in ans:
                if c_a == a:
                    count -= 1
                    break
        if count == 0:        ##答對
            RoW.append(1)
            correct += 1
        else:                 ##答錯
            RoW.append(0)
    wrong = []
    need_corr = []
    num = 0
    for o in RoW:
        if o == 0:
            wrong.append(user_ans[num])
            need_corr.append(correct_ans[num])
        num += 1

    topic_size = len(id)
    context = {}
    context['correct'] = correct
    context['topic_size'] = topic_size
    context['results'] = zip(wrong,need_corr)
    context['RoW'] = RoW
    context['correct_ans'] = correct_ans
    cursor.close()

    account = glo['now_account']                  #儲存分數
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database03.db")  # 建立資料庫連線
    cursor = conn.cursor()
    # 建立一個資料表
    sqlstr = "CREATE TABLE IF NOT EXISTS "+account+" ('title' TEXT ,'score' TEXT)"
    cursor.execute(sqlstr)
    # 新增一筆資料
    sqlstr = "insert into "+account+" values ('" + title + "','" + str(correct) +"/" + str(topic_size) + "')"
    cursor.execute(sqlstr)
    conn.commit()
    conn.close()

    return render(request, 'student_score.html', context)

def see_score(request):
    account = glo['now_account']
    context = {}
    conn = sqlite3.connect(os.path.dirname(__file__) + "\database03.db")  # 建立資料庫連線
    cursor = conn.cursor()
    sqlstr = "select * from "+ account
    cursor = cursor.execute(sqlstr)
    title = []
    score = []
    for row in cursor:
        title.append(row[0])
        score.append(row[1])
    context['results'] = zip(title,score)
    return render(request, "see_score.html", context)

def back_student_choice(request):
    return render(request, 'student_choice.html')