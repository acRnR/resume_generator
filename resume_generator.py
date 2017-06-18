#from docx import Document
#from docx.shared import Inches
from flask import Flask
from flask import url_for, render_template, request, redirect, flash, session
import requests
import json

app = Flask(__name__)

#document = Document()
u_info = {}


def make_a_docx():
    paragraph = document.add_paragraph('Lorem ipsum dolor sit amet.', style='ListBullet')
    paragraph.style = 'ListBullet'
    prior_paragraph = paragraph.insert_paragraph_before('Lorem ipsum')
    document.add_heading('The REAL meaning of the universe')
    document.add_heading('The role of dolphins', level=2)
    document.add_page_break()
    table = document.add_table(rows=2, cols=2)
    cell = table.cell(0, 1)
    cell.text = 'parrot, possibly dead'
    row = table.rows[1]
    row.cells[0].text = 'Foo bar to you.'
    row.cells[1].text = 'And a hearty foo bar to you too sir!'
    table.style = 'LightShading-Accent1'
    document.add_picture('picture.jpg', width=Inches(3.0))




def vk_api(method, **kwargs):
    api_request = 'https://api.vk.com/method/'+method + '?'
    api_request += '&'.join(['{}={}'.format(key, kwargs[key]) for key in kwargs])
    return json.loads(requests.get(api_request).text)


def collect_info(u_id):
    #u_id = '1'
    flds = 'first_name,last_name,photo_200,city,career,education,hidden,about,activities,connections,contacts,occupation,personal,site,status'
    #arr_flds = flds.split(',')
    result = vk_api('users.get', user_ids=u_id, fields=flds, v='5.63')
    if 'hidden' not in result['response'][0]:
        clean_info(result['response'][0])
    else:
        u_info['hidden'] = 'К сожалению, пользователь закрыл доступ к информации на своей странице'
    #print(result['response'][0]['faculty'])
    #for el in arr_flds:
     #   if el in result['response'][0]:
      #      u_info[d[el]] = result['response'][0]
    #for key in result['response'][0]:
     #   print(key, result['response'][0][key])
        #for el in key:
        #    print(el, key[el])#, result['response'][key])
#    print(result)


def clean_info(result):
    if 'photo_200' in result:
        u_info['photo'] = result['photo_200']
    u_info['name'] = result['first_name'] + ' ' + result['last_name']
    if 'site' in result:
        u_info['site'] = '<a href"' + result['site'] + '">' + result['site'] + '</a>'
    u_info['city'] = result['city']['title']


@app.route('/')
def index():
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
    photo = u_info['photo']
    u_info.pop('photo')
    return render_template('result.html', photo=photo, info=u_info)


@app.route('/access_error')
def access_error():
    pass


if __name__ == '__main__':
    app.run(debug=True)
    #collect_info()