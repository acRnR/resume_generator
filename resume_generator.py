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
    flds = 'first_name,last_name,photo_200,city,career,education,hidden,personal,site,bdate'
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
    if 'career' in result and len(result['career']) >= 2:
        for el in ['company', 'position']:
            if el in result['career'][1]:
                u_info[el] = result['career'][1][el]
        if 'from' in result['career'][1] and 'to' not in result['career'][1]:
            u_info['c_date'] = result['career'][1]['from']
        elif 'from' in result['career'][1] and 'to' in result['career'][1]:
            u_info['c_date'] = result['career'][1]['from'] + ' - ' + result['career'][1]['to']
    if 'bdate' in result:
        u_info['bdate'] = result['bdate']
    if 'university_name' in result and result['university_name'] != '':
        u_info['uni_name'] = result['university_name']
        if 'faculty_name' in result and result['faculty_name'] != '':
            u_info['fac_name'] = result['faculty_name']
        if 'graduation' in result and result['graduation'] != 0:
            u_info['graduation'] = result['graduation']
    if 'personal' in result and 'langs' in result['personal'] and len(result['personal']['langs']) >= 2:
        result['personal']['langs'].remove('Русский')
        u_info['langs'] = ', '.join(result['personal']['langs'])
    for item in ['about', 'activities', 'connections', 'contacts', 'personal']:
        if item in result:
            u_info[item] = result[item]
    if 'mobile_phone' in result:
        u_info['phone'] = result['mobile_phone']


@app.route('/')
def index():
    u_info.clear()
    sess['hidden'] = 0
    try:
        if request.args:
            info = request.args['answer']
            if '/' in info:
                info = info.replace('https://vk.com/', '')
            collect_info(info)
            return redirect(url_for('result'))
        return render_template('index.html')
    except:
        sess['hidden'] = 2
        return redirect(url_for('result'))


@app.route('/result')
def result():
    if sess['hidden'] == 0:
        kek = u_info
        return render_template('result.html', info=kek)
    elif sess['hidden'] == 1:
        message = 'К сожалению, у нас нет доступа к странице этого пользователя'
        return render_template('access_error.html', message=message)
    else:
        message = 'Ууупс... Кажется, вы ввели что-то странное, попробуйте ещё раз'
        return render_template('access_error.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)