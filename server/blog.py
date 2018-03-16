#!/urs/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import ConfigParser
import datetime
import io
import sys
import types
import re

ACTIVE=''' id="active" '''
TEMPLATE = '''<html lang="zh-cn">
<head>
    <title>%s</title>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="../css/page.css">
    <link rel="stylesheet" type="text/css" href="../css/code-styles.css">
    <script src="http://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/highlight.min.js"></script>
    <script >hljs.initHighlightingOnLoad();</script>  
    <link rel="shortcut icon" href="../image/yuan.ico" type="image/x-icon"/>
</head>
<body>
    <div class="blog-header"></div>
    <div class="blog-nav">
        <hr id="up"/>
        <button id="first" onclick="window.location.href='../index.html'">首 页
        </button><button  %s onclick="window.location.href='../blog.html'">博 客
        </button><button  %s onclick="window.location.href='../read.html'">读 书
        </button><button  %s onclick="window.location.href='../science.html'">科 学
        </button><button  %s onclick="window.location.href='../literature.html'">文 哲
        </button><button  %s onclick="window.location.href='../scope.html'">视 野
        </button><button  onclick="window.location.href='../chief_engineer.html'">首 领</button>
        <hr id="down"/>
    </div>
    <div class="blog-body">
        <div id="title">%s</div>
        <div id="subtitle">%s</div>
        %s
        <div id="sign">%s</div>
        <footer>
            <a href="%s">上一篇</a>
            <span id="back-top"><a href="#">返回页顶</a></span>
            <span id="next-blog"><a href="%s">下一篇</a></span>
        </footer>
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = '''<html lang="zh-cn">
<head>
	<title>裸猿森林</title>
	<meta http-equiv="Content-Type" content="text/html" charset="utf-8">
	<link rel="stylesheet" type="text/css" href="./css/page.css">
    <link rel="shortcut icon" href="./image/yuan.ico" type="image/x-icon"/>
</head>
<body>
    <div class="nav">
        <h1><a href="index.html">裸猿森林</a></h1>
        <hr id="up"/>
        <h2>目录</h2>
        <ul>%s
        </ul>
        %s
        <footer>
            <a href="">CopyLift: 所有文章转载请注明出处，侵权必究！| @X光设计 | Email: zqbxsx@126.com</a>
        </footer>
    </div>
</body>
</html>
'''

today = datetime.date.today()
curr_id = 0

def DEBUG(log):
    #print log
    pass

def read_conf(blog_conf):
    conf = ConfigParser.ConfigParser()
    conf.read('blog.conf')
    blog_conf['db_path'] = conf.get('BLOG', 'db_path')
    blog_conf['html_path'] = conf.get('BLOG', 'html_path')
    

def get_blog_content(cursor, content_id):
    sql = '''
        select
            content
        from
            content_tb
        where
            id = %s
    '''
    cursor.execute(sql % content_id)
    return cursor.fetchone()[0]

def get_blog_type_name(cursor, type_name):
    sql = '''
        select
            name
        from
            type_name_tb 
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        type_name.append(row[0])

def get_blog_class_name(cursor, class_name):
    sql = '''
        select
            type,
            subtype,
            name
        from
            class_name_tb 
        order by type, subtype asc
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        if not class_name.has_key(row[0]):
            class_name[row[0]] = {}
        class_name[row[0]][row[1]] = row[2]

def get_last_html(cursor, last_html):
    sql = '''
        select
            type,
            html
        from
            html_tb
        group by type
        order by type asc 
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        last_html[row[0]] = row[1]
    sql = '''
        select
            type
        from
            type_name_tb
        where type != 0
        group by type
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        if row[0] not in last_html.keys():
            last_html[row[0]] = "" 

#def get_prev_html(cursor, type_id):
#    sql = '''
#        select 
#            html
#        from
#            html_tb
#        where 
#            type = %s
#        order by time
#        desc
#        limit 1
#    '''
#    cursor.execute(sql % type_id)
#    return cursor.fetchone()[0]

def get_html_id(cursor, html_id):
    '''
        获取当前的起始编号
        计数当前html_tb的记录数即可
    '''
    sql = '''
        select 
            type,
            count(*)
        from
            html_tb
        group by type
    ''' 
    cursor.execute(sql)
    for row in cursor.fetchall():
        html_id[row[0]] = int(row[1])



def set_file_name(cursor, html_dict):
    '''
        生成html文件名
        拼接编号和后缀
    '''
    html_id = {}
    get_html_id(cursor, html_id)
    DEBUG(html_id)
        
    for i in html_dict.keys():
        if not html_id.has_key(i):
            html_id[i] = 0
        for j in range(len(html_dict[i])):
            html_dict[i][j]['file_name'] += '_' + str(html_id[i]) + '.html'
            html_dict[i][j]['id'] = html_id[i]
            html_id[i] += 1

def adjust_last_html(conf, last_html, next_html):
    '''
        调整对上一篇文章的下一篇链接
    '''
    if len(last_html) == 0:
        return
        
    body=""
    src = "<span id=\"next-blog\"><a href=\"\">"
    rep = "<span id=\"next-blog\"><a href=\"%s\">"
    with io.open(conf['html_path'] + last_html, 'r') as html:
        content = html.read()
        body = content.replace(src, rep % next_html)
        html.close()
    with io.open(conf['html_path'] + last_html, 'w') as html:
        html.write(body)
        html.close()

def set_prev_next_html(cursor, conf, html_dict, last_html):
    for i in html_dict.keys():
        num = len(html_dict[i]) 
        for j in range(num):
            #只有一个
            if j == 0 and j == num - 1:
                prev_html = last_html[i]
                next_html = ''
                adjust_last_html(conf, last_html[i], html_dict[i][j]['file_name'])
            #第一个,但不是最后一个
            elif j == 0:
                prev_html = last_html[i]
                next_html = html_dict[i][j + 1]['file_name']
                adjust_last_html(conf, last_html[i], html_dict[i][j]['file_name'])
            #最后一个，但不是第一个
            elif j == num - 1:
                prev_html = html_dict[i][j - 1]['file_name']
                next_html = '' 
            #中间
            else:
                prev_html = html_dict[i][j - 1]['file_name']
                next_html = html_dict[i][j + 1]['file_name']
            html_dict[i][j]['prev_html'] = prev_html
            html_dict[i][j]['next_html'] = next_html 

def insert_html_tb(conn, html_dict):
    '''
        将当前的所有html文件名插入db，等价于更新编号
    '''
    cursor = conn.cursor()
    sql = '''
        insert into html_tb
            (time, type, class, subclass, title, html)
        values
        (
             datetime('now'),
             %s,
             %s,
             %s,
            '%s',
            '%s'
        );
    ''' 
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            cursor.execute(sql% (curr_html['type'], curr_html['class'], curr_html['subclass'], 
                                curr_html['title'], curr_html['file_name']))
    conn.commit()


def format_content(content):
    body = ""
    rep = '</p>\n'
    pattarn = r'<\/\p>'
    body = re.sub(pattarn, rep, content)
    rep = '../'
    pattarn = r'\/run\/media\/work\/xujinguang\/blog\/xujinguang.github.io\/'
    body = re.sub(pattarn, rep, body)
    return body

def get_blog_content(cursor, html_dict):
    sql = '''
        select
            content
        from 
            content_tb
        where
            id = %s
    '''
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            cursor.execute(sql % curr_html['content_id'])
            content = cursor.fetchone()[0]
            #curr_html['content'] = format_content(content)
            curr_html['content'] = content.encode('utf-8')

def select_blogs(cursor):
    global today
    global curr_id
    print today
    print curr_id
    sql = ""
    if curr_id != 0:
        sql = '''
            select 
                id,
                type, 
                class, 
                subclass, 
                title, 
                subtitle, 
                abstruct,
                content_id,
                sign,
                date,
                time
            from 
                blog_index_tb
            where
                id = %s
        ''' % curr_id 
    else:
        sql = '''
            select 
                id,
                type, 
                class, 
                subclass, 
                title, 
                subtitle, 
                abstruct,
                content_id,
                sign,
                date,
                time
            from 
                blog_index_tb
            where
                date = '%s'
            order by time
            asc    
        ''' % today
    print sql
    cursor.execute(sql)
    blogs = cursor.fetchall()
    return blogs
    
def get_blogs(cursor, conf, html_dict):
    global today
    blogs = select_blogs(cursor)
    nav = {
        1:(ACTIVE, '', '', '', ''),
        2:('', ACTIVE, '', '', ''),
        3:('', '', ACTIVE, '', ''),
        4:('', '', '', ACTIVE, ''),
        5:('', '', '', '', ACTIVE)
    }

    type_name = []
    get_blog_type_name(cursor, type_name)
    class_name = {}
    get_blog_class_name(cursor, class_name)
    if type(today) == type('str'):
        today = datetime.datetime.strptime(today, "%Y-%m-%d") 
    today = today.strftime("%Y%m%d")

    ID = 0
    TYPE = 1 
    CLASS = 2 
    SUBCLASS = 3 
    TITLE = 4 
    SUBTITLE = 5 
    ABSTRUCT = 6
    CONTENT_ID = 7
    SIGN = 8
    DATE = 9
    TIME = 10

    for blog in blogs:
        curr_html = {}
        i = blog[TYPE]
        j = blog[CLASS]
        k = blog[SUBCLASS]
        curr_html['type'] = i
        curr_html['type_name'] = type_name[i]
        curr_html['class'] = j
        curr_html['subclass'] = k 
        title = blog[TITLE].encode('utf-8')
        curr_html['title'] = title
        curr_html['html_title'] = str(type_name[i]) + '-' + title
        curr_html['nav'] = nav[i]
        curr_html['subtitle'] = blog[SUBTITLE].encode('utf-8')
        curr_html['date'] = blog[DATE].encode('utf-8')
        curr_html['abstruct'] = blog[ABSTRUCT].encode('utf-8')
        if k != 0:
            file_name = today + '_' + type_name[i] + '_' + class_name[j][0] + '_' + class_name[j][k]
        else:
            file_name = today + '_' + type_name[i] + '_' + class_name[j][0] 
        curr_html['file_name'] = file_name
        curr_html['content_id'] = blog[CONTENT_ID] 
        curr_html['sign'] = blog[SIGN].encode('utf-8')
        curr_html['prev_html'] = ""
        curr_html['next_html'] = ""
        
        if not html_dict.has_key(i):
            html_dict[i] = []
        html_dict[i].append(curr_html)

def update_type_html(conf, html_dict):
    global today
    src = "<table>"
    other_rep = '''<table>
            <tr>
                <td><a href="%s">%s</a></td>
                <td id="right-time">%s</td>
            </tr>
    '''
    read_rep = '''<table>
            <tr>
                <td><a href="%s">%s</a></td>
                <td id="book-name"><a href="%s">%s</a></td>
                <td id="right-time">%s</td>
            </tr>
    '''
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            body = ""
            html_file = conf['html_path'][0:-5] + curr_html['type_name'] + '.html'
            with io.open(html_file, 'r') as html:
                content = html.read()
                href = str('./blog/' + curr_html['file_name'])
                title = '《'.encode('utf-8') + curr_html['title'] + '》'.encode('utf-8')
                if(curr_html['type'] == 2):
                    txt = read_rep % (href, title, href, curr_html['abstruct'], curr_html['date'])
                    body = content.replace(src, txt)
                else:
                    body = content.replace(src, other_rep % (href, title, curr_html['date']))
                print body
                html.close()
            with io.open(html_file, 'w') as html:
                html.write(body)
                html.close()

def output_html(conf, html_dict):
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            html = io.open(conf['html_path'] + curr_html['file_name'], "wb")
            DEBUG(curr_html['file_name'])
            DEBUG(curr_html['content'])
            #参数列表，第一个需要有都好，使用+拼接
            content = format_content(curr_html['content'])
            param = (str(curr_html['html_title']),) + curr_html['nav'] + (curr_html['title'],
                        curr_html['subtitle'],
                        str(content),
                        curr_html['sign'],
                        str(curr_html['prev_html']),
                        str(curr_html['next_html']))
            text = TEMPLATE % param
            DEBUG(text)
            html.write(text)
            html.close()

def update_banner(conf, html_dict):
    '''
        更新条幅
    '''
    body = ""
    ref = '''<a href="%s">%s</a>'''
    href=""
    #href = '''<a href="./blog/20170610_literature_literature_poem_11.html">《未来》</a>'''
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            title = '《'+ curr_html['title'] + '》'
            href += ref %(str('./blog/' + curr_html['file_name']), title)

    pattarn = r'\<marquee.*\>'
    rep = '''<marquee scrollamount="3" onMouseOut="this.start()" onMouseOver="this.stop()">最新动态：%s</marquee>''' % href
    with io.open(conf['html_path'][0:-5] + 'index.html', 'r') as html:
        content = html.read()
        body = re.sub(pattarn, rep.encode('utf-8'), content)
        #print body
        html.close()
    with io.open(conf['html_path'][0:-5] + 'index.html', 'w') as html:
        html.write(body)
        html.close()
    

def get_all_html(cursor, all_html):
    class_name = {}
    get_blog_class_name(cursor, class_name)

    sql = '''
        select
            t.time,
            t.class,
            t.subclass,
            t.title,
            t.html
        from
        (
            select
                time,
                class,
                subclass,
                title,
                html
            from
                html_tb
            order by time desc
        )t
        order by class, subclass asc
    '''
    cursor.execute(sql)
    for row in cursor.fetchall():
        curr_class_name =  class_name[row[1]][row[2]]
        if not all_html.has_key(curr_class_name):
            all_html[curr_class_name] = [] 
        record = (row[0].split(' ')[0], row[3], row[4])
        all_html[curr_class_name].append(record)

def output_all_html(conf, all_html):
    index_str = '''
            <li><a href="#%s">%s-(%s)</a></li>'''
    class_index_str = '''
        <div id="%s">
        <hr id="up"/>
        <h2><a href="#%s">%s</a></h2>
            <table>%s
            </table>
        </div>'''
    record_str = '''
                <tr>
                    <td><a href="./blog/%s" target="_blank">%s</a></td>
                    <td id="right-time">%s</td>
                </tr>'''
    all_index = ""
    all_class_index = ""

    for class_name in sorted(all_html.keys()):
        records = all_html[class_name]
        all_index += index_str % (class_name, class_name, len(records))
        all_record = ""
        for record in records:
            title = '《'.encode('utf-8') + record[1] + '》'.encode('utf-8')
            all_record += record_str % (str(record[2]), title, str(record[0]))
        all_class_index += class_index_str % ((class_name,) * 3 + (all_record,))
    all_index_html = INDEX_TEMPLATE % (all_index, all_class_index)

    #print all_index_html
    with io.open(conf['html_path'][0:-5] + 'all_index.html', 'w') as html:
        html.write(all_index_html)
        html.close()

def test():
    reload(sys)  
    sys.setdefaultencoding('utf8')  
    conf = {}
    read_conf(conf)
    conn = sqlite3.connect(conf['db_path'])
    cursor = conn.cursor()

    #type_name = []
    #get_blog_type_name(cursor, type_name)
    #print type_name[2]
    #class_name = {}
    #get_blog_class_name(cursor, class_name)
    #print class_name[7][8]
    #print class_name[7][0]

    all_html = {}
    #get_all_html(cursor, all_html)
    #print all_html

    #output_all_html(conf, all_html)
    update_banner(conf, all_html)

    conn.close()
    
def gen_blog():
    reload(sys)  
    sys.setdefaultencoding('utf8')  
    global today
    if len(sys.argv) == 2:
        print sys.argv[0], sys.argv[1]
        today = sys.argv[1]

    #初始化blog.conf
    conf = {}
    read_conf(conf)
    #print conf['db_path']

    conn = sqlite3.connect(conf['db_path'])
    cursor = conn.cursor()

    html_dict = {}
    get_blogs(cursor, conf, html_dict)

    #按照格式拼接文件名:日期-分类-学科-编号.html
    set_file_name(cursor, html_dict)
    #print html_dict
    #return

    #获取上一篇的文章,用于下文的set_prev_next_html
    last_html = {}
    get_last_html(cursor, last_html)

    #链接各个博客
    set_prev_next_html(cursor, conf, html_dict, last_html)

    #获取html的body
    get_blog_content(cursor, html_dict)
    #print html_dict

    #生成文章文件
    output_html(conf, html_dict)

    #更新每个模块的主页文章列表
    update_type_html(conf, html_dict)

    #插入的目的是为了方便生成目录
    insert_html_tb(conn, html_dict)

    #更新主页动态文字横幅
    update_banner(conf, html_dict)

    all_html = {}
    get_all_html(cursor, all_html)
    #print all_html
    output_all_html(conf, all_html)

    conn.close()

def init_blog(date, blog_id):
    global today
    today = date
    global curr_id 
    curr_id = blog_id

if __name__ == "__main__":
    gen_blog()
    #test()
