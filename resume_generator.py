from flask import Flask
from flask import url_for, render_template, request, redirect, flash, session
import requests
import json

app = Flask(__name__)
u_info = []
sess = {}


def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    return json.loads(requests.get(api_request).text)


def collect_info(u_id):
    flds = 'first_name,last_name,photo_200,city,career,education,hidden,about,activities,connections,contacts,occupation,personal,site,status'
    result = vk_api('users.get', user_ids=u_id, fields=flds, v='5.65')
    if 'hidden' not in result['response'][0]:
        clean_info(result['response'][0])
    else:
        sess['hidden'] = 1


def clean_info(result):
    if 'photo_200' in result:
        u_info.append(result['photo_200'])
    u_info.append(result['first_name'] + ' ' + result['last_name'])
    if 'site' in result and result['site'] != '':
        u_info.append(result['site'])
    if 'city' in u_info:
        u_info.append(result['city']['title'])
    if 'career' in result and 'company' in result['career'][0]:
        u_info.append(result['career'][0]['company'])
    print(u_info)

@app.route('/')
def index():
    sess['hidden'] = 0
    if request.args:
        print('one')
        info = request.args['answer']
        print('two')
        collect_info(info)
        print('three')
        return redirect(url_for('result'))
    return render_template('index.html')


@app.route('/result')
def result():
    if sess['hidden'] != 1:
        photo = u_info[0]
        kek = u_info[1:]
        return render_template('result.html', photo=photo, info=kek)
    else:
        return render_template('access_error.html')

@app.route('/access_error')
def access_error():
    pass


if __name__ == '__main__':
    app.run(debug=True)
    #collect_info()