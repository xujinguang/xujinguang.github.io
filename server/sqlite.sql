---警告：sqlite不支持表的字段alter功能，因此，如果下面任何表的字段需要修订只有一个方式
---创建临时表导出数据->丢弃旧表->创建修订后的新表->从临时表导入数据
create temp table tmp as select * from blog_index_tb;
drop table blog_index_tb;
create table blog_index_tb ...
insert into blog_index_tb select * from tmp;
drop table tmp;

--增加子类型子段
insert into blog_index_tb (id, type, class, title, subtitle, abstruct, content_id, sign, date, time, modify_time) select * from tmp;

create table blog_index_tb(
	id integer primary key autoincrement,
	type tinyint,
	class tinyint,
    subclass tinyint not null default 0,
	title varchar(32) not null default (date('now', 'localtime')),
	subtitle varchar(64) default null,
	abstruct varchar(128) default null,
	content_id int,
	sign varchar(16) not null default (datetime('now', 'localtime')),
	date date not null default (date('now', 'localtime')),
	time time not null default (time('now', 'localtime')),
	modify_time datetime
);

create table content_tb(
	id integer primary key autoincrement,
	content text
);

create table type_name_tb(
	type tinyint primary key,
	name varchar(32)
);

create table class_name_tb(
	type tinyint,
    subtype tinyint,
	name varchar(32),
    primary key (type, subtype)
);

--增加title
insert into html_tb (id, time, type, class, subclass, html) select * from tmp;

create table html_tb(
	id integer primary key autoincrement,
	time datetime not null default (datetime('now', 'localtime')),
	type tinyint,
	class tinyint,
    subclass tinyint not null default 0,
    title varchar(32) default null,
	html varchar(64)
);

--这是导航标签的分类，这个可以根据需要调整
--编号从左向右的，调整时和尽量和网页保持一致
insert into type_name_tb values 
	(0, 'index'),
	(1, 'blog'),
	(2, 'read'),
	(3, 'scope'),
	(4, 'science'),
	(5, 'literature');

--这个分类是discovery工具的学科分类，直接转移过来编号存入
--新增学科直接追加
insert into class_name_tb values
	(0, 0, 'other'),	
	(1, 0, 'music'),
	(2, 0, 'biology'),
	(3, 0, 'chemistry'),
	(4, 0, 'economics'),
	(5, 0, 'religious'),
	(6, 0, 'history'),

	(7, 0, 'computer'),
	(7, 1, 'data-structure'),
	(7, 2, 'alogrithm'),
	(7, 3, 'compiler'),
	(7, 4, 'lisp'),
	(7, 5, 'C'),
	(7, 6, 'C++'),
	(7, 7, 'python'),
	(7, 8, 'php'),
	(7, 9, 'shell'),
	(7, 10, 'linux'),
	(7, 11, 'network'),
	(7, 12, 'database'),
	(7, 13, 'os'),
	(7, 14, 'machine-learning'),
	(7, 15, 'ai'),
	(7, 16, 'web'),
	(7, 17, 'hack'),

	(8, 0, 'biography'),
	(9, 0, 'logic'),

	(10, 0, 'math'),
	(10, 1, 'matrix'),
	(10, 2, 'numerical-analysis'),
	(10, 3, 'operational-research'),
	(10, 4, 'alogrithm'),
	(10, 5, 'algebra'), 
	(10, 6, 'geometry'), 
	(10, 7, 'probability-statistics'), 

	(11, 0, 'natural-science'),
	(12, 0, 'physics'),
	(13, 0, 'anthropology'),
	(14, 0, 'social-science'),
	(15, 0, 'civil-engineering'),
	(16, 0, 'universe'),

	(17, 0, 'literature'),
	(17, 1, 'novel'),
	(17, 2, 'poem'),
	(17, 3, 'essay'),
	(17, 4, 'masterpiece'),

	(18, 0, 'psychology'),
	(19, 0, 'medicine'),
	(20, 0, 'philosophy');

--测试数据建立
insert into content_tb
	(content)
values
	("测试博客1	分段	再分段"),
	("测试博客2"),
	("测试博客3"),
	("测试博客4"),
	("测试博客5"),
	("测试博客6"),
	("测试博客7"),
	("测试博客8"),
	("测试博客9"),
	("测试博客10"),
	("测试博客11");

