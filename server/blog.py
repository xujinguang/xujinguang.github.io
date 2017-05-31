#!/urs/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import ConfigParser
import datetime
import io
import sys
import types

ACTIVE=''' id="active" '''
TEMPLATE = '''<html lang="zh-cn">
<head>
    <title>%s</title>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="../css/page.css">
</head>
<body>
    <div class="blog-header"></div>
    <div class="blog-nav">
        <hr id="up"/>
        <button id="first" onclick="window.location.href='../index.html'">首 页
        </button><button  %s onclick="window.location.href='../blog.html'">博 客
        </button><button  %s onclick="window.location.href='../read.html'">读 书
        </button><button  %s onclick="window.location.href='../scope.html'">视 野
        </button><button  %s onclick="window.location.href='../science.html'">科 学
        </button><button  %s onclick="window.location.href='../literature.html'">诗 文
        </button><button  onclick="window.location.href='../index.html'">首 领</button>
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

def get_blog_type_name(cursor, tb):
    sql = '''
        select
            name
        from
            %s
    '''
    cursor.execute(sql % tb)
    return cursor.fetchall()

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
            (time, type, class, html)
        values
        (
             datetime('now'),
              %s,
             %s,
            '%s'
        );
    ''' 
    for i in html_dict.keys():
        for j in range(len(html_dict[i])):
            curr_html = html_dict[i][j]
            cursor.execute(sql% (curr_html['type'], curr_html['class'], curr_html['file_name']))
    conn.commit()


#def format_content(content):
#    p = ""
#    p += "<p>"
#    for ch in content:
#        if ch == '\t':
#            p += "</p>\n\t<p>"
#        else:
#            p += ch
#    p += "</p>\n"
#    return p 

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

    type_name = get_blog_type_name(cursor, 'type_name_tb')
    class_name = get_blog_type_name(cursor, 'class_name_tb')
    if type(today) == type('str'):
        today = datetime.datetime.strptime(today, "%Y-%m-%d") 
    today = today.strftime("%Y%m%d")

    ID = 0
    TYPE = 1 
    CLASS = 2 
    TITLE = 3 
    SUBTITLE = 4 
    ABSTRUCT = 5
    CONTENT_ID = 6
    SIGN = 7
    DATE = 8
    TIME = 9

    for blog in blogs:
        curr_html = {}
        i = blog[TYPE]
        j = blog[CLASS]
        curr_html['type'] = i
        curr_html['type_name'] = type_name[i][0]
        curr_html['class'] = j
        title = blog[TITLE].encode('utf-8')
        curr_html['title'] = title
        curr_html['html_title'] = str(type_name[i][0]) + '-' + title
        curr_html['nav'] = nav[i]
        curr_html['subtitle'] = blog[SUBTITLE].encode('utf-8')
        curr_html['date'] = blog[DATE].encode('utf-8')
        curr_html['abstruct'] = blog[ABSTRUCT].encode('utf-8')
        curr_html['file_name'] = today + '_' + type_name[i][0] + '_' + class_name[j][0]
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
                if(curr_html['type'] == 2):
                    txt = read_rep % (href, curr_html['title'], href, curr_html['abstruct'], curr_html['date'])
                    body = content.replace(src, txt)
                else:
                    body = content.replace(src, other_rep % (href, curr_html['title'], curr_html['date']))
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
            param = (str(curr_html['html_title']),) + curr_html['nav'] + (curr_html['title'],
                        curr_html['subtitle'],
                        curr_html['content'],
                        curr_html['sign'],
                        str(curr_html['prev_html']),
                        str(curr_html['next_html']))
            text = TEMPLATE % param
            DEBUG(text)
            html.write(text)
            html.close()
            
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


    conn.close()

def init_blog(date, blog_id):
    global today
    today = date
    global curr_id 
    curr_id = blog_id

if __name__ == "__main__":
    gen_blog()
