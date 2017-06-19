from flask import Flask
from flask import url_for, render_template, request, redirect, flash, session
import requests
import json

app = Flask(__name__)
u_info = {}
sess = {}


def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    return json.loads(requests.get(api_request).text)


def collect_info(u_id):
    flds = 'first_name,last_name,photo_200,city,career,education,hidden,about,activities,connections,contacts,occupation,personal,site,status,bdate'
    result = vk_api('users.get', user_ids=u_id, fields=flds, v='5.65')
    if 'hidden' not in result['response'][0]:
        clean_info(result['response'][0])
    else:
        sess['hidden'] = 1


def clean_info(result):
    if 'photo_200' in result:
        u_info['photo'] = result['photo_200']
    u_info['name'] = result['first_name'] + ' ' + result['last_name']
    if 'site' in result and result['site'] != '':
        u_info['site'] = result['site']
    if 'city' in u_info:
        u_info['city'] = result['city']['title']
    if 'career' in result and len(result['career']) >= 2:# and 'company' in result['career'][0]:
        #print(len(result['career']))
        for el in ['company', 'position']:
            if el in result['career'][1]:
                u_info[el] = result['career'][1][el]
        if 'from' in result['career'][1] and 'to' not in result['career'][1]:
            u_info['c_date'] = result['career'][1]['from']
        elif 'from' in result['career'][1] and 'to' in result['career'][1]:
            u_info['c_date'] = result['career'][1]['from'] + ' - ' + result['career'][1]['to']
    if 'bdate' in result:
        u_info['bdate'] = result['bdate']
    if 'university_name' in result:
        u_info['uni_name'] = result['university_name']
        if 'faculty_name' in result and result['faculty_name'] != '':
            u_info['fac_name'] = result['faculty_name']
        if 'graduation' in result:
            u_info['graduation'] = result['graduation']

    #if
    print(u_info)

@app.route('/')
def index():
    u_info.clear()
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
        #career = {
        #    'company':'Организация',
        #    'c_date':''
        #}
        kek = u_info
        return render_template('result.html', info=kek)
    else:
        return render_template('access_error.html')

@app.route('/access_error')
def access_error():
    pass


if __name__ == '__main__':
    app.run(debug=True)