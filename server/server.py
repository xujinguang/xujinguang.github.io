import SocketServer
import urllib
from blog import *

curr_id = 0
def decode_value(data, blog):
    i = data.find("\r\n\r\n")
    body = data[i + 4:]
    print len(body)
    values = body.split('_&')
    for value in values: 
        kv = value.split('=')
        print len(kv)
        blog[kv[0]] = kv[1]
    print blog

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
    cursor.execute(sql % blog['_blog_'])
    conn.commit()
    content_id = cursor.lastrowid;
    sql = '''
        insert into blog_index_tb 
            (type,
            class,
            title,
            subtitle,
            abstruct,
            content_id,
            sign,
            date,
            time,
            modify_time)
        values
            (%s, %s, '%s', '%s', '%s', %s, '%s', 
            date('now'), time('now'), datetime('now')); 
    ''' % (blog['_type_'], 
        blog['_class_'],
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
        print 'cur', today
        init_blog(today, curr_id)
        gen_blog()
    return ret 


class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(4096).strip()
        print self.data
        ret = process(self.data)
        status = "HTTP/1.1 200 OK\r\n"
        content_type = "content-type:text/xml; charset=utf-8\r\n"
        origin = "Access-Control-Allow-Origin:*\r\n"
        body = "\r\nret=%s\r\n"% ret
        response = status + content_type + origin + body
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080 
    #HOST, PORT = "192.168.1.2", 8080 

    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
