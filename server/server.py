#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socketserver
import urllib
from blog import *

curr_id = 0
def decode_value(data, blog):
    i = data.find("\r\n\r\n")
    body = data[i + 4:]
    print (body)
    print (len(body))
    values = body.split('_&')
    for value in values:
        kv = value.split('_=')
        #print (len(kv))
        blog[kv[0]] = kv[1]
    print (blog)

def list_blog(conn, blog):
    return 0 

def save_blog(conn, blog):
    global curr_id
    sql = '''
        insert into content_tb
            (content)
        values
            ('%s');
    '''
    cursor = conn.cursor()
    content = blog['_blog_'].replace("<p><img", '''<p id="img"><img''').replace("'", '\'\'')
    if blog['_class_'] == '17' and blog['_subclass_'] == '2':
        content = blog['_blog_'].replace("<p>", '''<p id="poem">''')
    #print (sql %content)
    cursor.execute(sql % content)
    conn.commit()
    content_id = cursor.lastrowid;
    sql = '''
        insert into blog_index_tb 
            (type,
            class,
            subclass,
            title,
            subtitle,
            abstruct,
            content_id,
            sign,
            date,
            time,
            modify_time)
        values
            (%s, %s, %s, '%s', '%s', '%s', %s, '%s', 
            date('now', 'localtime'), 
            time('now', 'localtime'), 
            datetime('now', 'localtime')); 
    ''' % (blog['_type_'], 
        blog['_class_'],
        blog['_subclass_'],
        blog['_title_'],
        blog['_subtitle_'],
        blog['_key_'],
        content_id,
        blog['_sign_'])
    cursor.execute(sql)
    conn.commit()
    curr_id = cursor.lastrowid;
    return 0 

def edit_blog(conn, blog):
    return 0 

def process(data):
    blog = {}
    conf = {}
    decode_value(data, blog)
    if len(blog) == 0:
        return -1;
    #return 0

    read_conf(conf)
    conn = sqlite3.connect(conf['db_path'])
    ret = 0
    if blog['op'] == '0':
        ret = list_blog(conn, blog)
    elif blog['op'] == '1':
        ret = save_blog(conn, blog)
    elif blog['op'] == '2':
        ret = edit_blog(conn, blog)
    else:
        ret = -2
    conn.close()

    if blog['op'] == '1':
        today = datetime.date.today()
        print ('cur', today)
        init_blog(today, curr_id)
        gen_blog()
    return ret 


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(65535).strip()
        print (self.data)
        ret = process(self.data)
        #ret = 0
        status = "HTTP/1.1 200 OK\r\n"
        content_type = "content-type:text/xml; charset=utf-8\r\n"
        origin = "Access-Control-Allow-Origin:*\r\n"
        body = "\r\nret=%s\r\n"% ret
        response = status + content_type + origin + body
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080 
    #HOST, PORT = "192.168.1.2", 8080 

    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
