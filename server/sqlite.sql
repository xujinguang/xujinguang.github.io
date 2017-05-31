---警告：sqlite不支持表的字段alter功能，因此，如果下面任何表的字段需要修订只有一个方式
---创建临时表导出数据->丢弃旧表->创建修订后的新表->从临时表导入数据
create temp table tmp as select * from blog_index_tb;
drop table blog_index_tb;
create table blog_index_tb ...
insert into blog_index_tb select * from tmp;
drop table tmp;

create table blog_index_tb(
	id integer primary key autoincrement,
	type tinyint,
	class tinyint,
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
	type tinyint primary key,
	name varchar(32)
);

create table html_tb(
	id integer primary key autoincrement,
	time datetime not null default (datetime('now', 'localtime')),
	type tinyint,
	class tinyint,
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
	(0, 'NULL'),	
	(1, 'art'),
	(2, 'biology'),
	(3, 'chemistry'),
	(4, 'economics'),
	(5, 'religious'),
	(6, 'history'),
	(7, 'computer'),
	(8, 'biography'),
	(9, 'logic'),
	(10, 'math'),
	(11, 'natural-science'),
	(12, 'physics'),
	(13, 'anthropology'),
	(14, 'social-science'),
	(15, 'civil-engineering'),
	(16, 'universe'),
	(17, 'literature'),
	(18, 'psychology'),
	(19, 'medicine'),
	(20, 'philosophy');

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

insert into blog_index_tb 
	(  
	   type,
	   class,
	   title,
	   subtitle,
	   abstruct,
	   content_id,
	   sign,
	   date,
	   time,
	   modify_time
	)
values
	(
		1,
		2,
		'blog',
		'',
		'',
		1,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		1,
		4,
		'blog',
		'',
		'',
		2,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		2,
		10,
		'blog',
		'',
		'',
		3,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		3,
		12,
		'blog',
		'',
		'',
		4,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		4,
		20,
		'blog',
		'',
		'',
		5,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		5,
		15,
		'blog',
		'',
		'',
		1,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		1,
		2,
		'blog',
		'',
		'',
		11,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		3,
		2,
		'blog',
		'',
		'',
		10,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		4,
		8,
		'blog',
		'',
		'',
		6,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		2,
		9,
		'blog',
		'',
		'',
		8,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	),
	(
		5,
		5,
		'blog',
		'',
		'',
		7,
		'于成都',
		date('now'),
		time('now'),
		datetime('now')
	);



		


