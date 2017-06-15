# xujinguang.github.io
#### 金光博客
## 博客编辑器
	./notepad/notepad.html
## 博客后台服务
	./server/server.py
## 博客生成器
	./server/blog.py
## 安装说明
1. 安装sqlite3
2. 安装python
3. 创建*.db
4. 使用sqlite.sql创建表
5. 填写blog.conf配置
6. 本地终端首先运行服务
```
	$ python server.py
```
7. 打开notepad.html编辑文章
8. 填写必要内容
9. Submit提交，成功则标示本地生成博客成功
10. 博客推送到github

## 修改说明
1.修改导航栏的内容或次序
    1.1.sqlite.sql的表type_name_tb重新编序号或者名字
    1.2.server/blog.py中的输出模板需要调整
    1.3.已有的博客html导航文件需要调整次序或改名

2.增加分类
    2.1.sqlite.sql的表class_name_tb添加新编号和名字
    2.2.notepad/scripte/blog-editor.js的gen_subclass中添加名称
    2.3.如何涉及主分类，在notepad.html中添加主分类
    2.4.已生成的博客就不建议修改分类了。个别改改就行。



