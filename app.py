# -*- coding: utf-8 -*-
import requests as requests
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi
from urllib.request import urlopen
from html_table_parser import parser_functions as parser
from selenium import webdriver

ca = certifi.where()

client = MongoClient("mongodb+srv://test:sparta@cluster0.xmayriq.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = client.dbsparta

SECRET_KEY = 'SPARTA'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


# 코딩 시작
# ------------네이버


@app.route("/search", methods=["POST"])
def search():
    nicname_receive = request.form['nicname_give']

    url = 'https://fow.kr/find/' + nicname_receive

    user_info_fow = requests.get(url, headers=headers)
    user_info_fow = BeautifulSoup(user_info_fow.text, 'html.parser')
    data = user_info_fow.find("table", {"class": "tablesorter"})
    p = parser.make2d(data)
    db.list.drop()
    db.freeRank.drop()
    db.soloRank.drop()
    for x in range(len(p)):
        champion = p[x][0]
        cntgame = p[x][1]
        Odds = p[x][2]
        kda = p[x][3]
        kill = p[x][4]
        death = p[x][5]
        assist = p[x][6]
        cs = p[x][7]
        avgold = p[x][8]
        triple = p[x][9]
        quadra = p[x][10]
        penta = p[x][11]
        win = p[x][12]
        lose = p[x][13]
        doc = {
            'champion': champion,
            'cntgame': cntgame,
            'Odds': Odds,
            'kda': kda,
            'kill': kill,
            'death': death,
            'assist': assist,
            'cs': cs,
            'avgold': avgold,
            'triple': triple,
            'quadra': quadra,
            'penta': penta,
            'win': win,
            'lose': lose
        }

        db.list.insert_one(doc)
    #
    #

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    # ---------------------------------------------------------------------------------------------

    driver.get(url)
    html = driver.page_source
    soup_user_profile = BeautifulSoup(html, "html.parser")
    items = soup_user_profile.select(".table_summary")

    # 솔랭 정보 =====================================================================================
    soloRank = str(items).split('<div style="width:5px; height:125px; position:relative; float:left;">')[0]
    league = soloRank.split('리그: ')[1].split(' 5x5')[0]
    ranking_num = soloRank.split('target="_blank"><b>')[1].split('</b><span')[0]
    ranking_per = soloRank.split('위">( ')[1].split(' )</span>')[0]
    tier = soloRank.split('<b><font color')[1].split('">')[1].split('</font>')[0]
    point = soloRank.split('리그 포인트: ')[1].split('<br>')[0]
    record = soloRank.split('</br></br></br></br></br></br></br></div>')[0].split('승급전:')[1].split('<br><br>')[1].split(
        '			')[1].split('		')[0].replace("\n", "")
    rankimg = soloRank.split(' src="')[1].split('" style')[0]
    solo_doc = {
        'name': nicname_receive,
        'ranking_num': ranking_num,
        'ranking_per': ranking_per,
        'league': league,
        'tier': tier,
        'point': point,
        'record': record,
        'rankimg': rankimg
    }
    db.soloRank.insert_one(solo_doc)

    # 자랭 정보 =====================================================================================
    freeRank = str(items).split('<div style="width:5px; height:125px; position:relative; float:left;">')[1]
    league = freeRank.split('리그: ')[1].split(' 5x5')[0]
    ranking_num = freeRank.split('target="_blank"><b>')[1].split('</b><span')[0]
    ranking_per = freeRank.split('위">( ')[1].split(' )</span>')[0]
    tier = freeRank.split('<b><font color')[1].split('">')[1].split('</font>')[0]
    point = freeRank.split('리그 포인트: ')[1].split('<br>')[0]
    record = freeRank.split('</br></br></br></br></br></br></br></div>')[0].split('승급전:')[1].split('<br><br>')[1].split(
        '			')[1].split('		')[0].replace("\n", "")
    rankimg = freeRank.split(' src="')[1].split('" style')[0]
    free_doc = {
        'ranking_num': ranking_num,
        'ranking_per': ranking_per,
        'league': league,
        'tier': tier,
        'point': point,
        'record': record,
        'rankimg': rankimg
    }
    db.freeRank.insert_one(free_doc)
    return jsonify({'msg': '입력 완료!'})


@app.route("/user_info", methods=["GET"])
def homework_get():
    soloRank_list = list(db.soloRank.find({}, {'_id': False}))
    freeRank_list = list(db.freeRank.find({}, {'_id': False}))
    champion_list = list(db.list.find({}, {'_id': False}))
    return jsonify({'soloRank': soloRank_list, 'freeRank': freeRank_list, 'champion': champion_list})


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
