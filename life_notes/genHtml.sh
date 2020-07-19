#!/bin/bash
#$1-源文件目录
#$2-目标目录 取目录名为相对路径起始点
set +x
if [ $# != 2 ] ; then
	echo "genHtml.sh element 拷贝到 同一个目录下，执行"
	echo "./genHtml.sh src dest"
	exit
fi
project=`basename $(pwd $2)`
function getfiletype()
{
	case "$1" in
	"md")
		echo "markdown"
		;;
	"*")
		echo "$1"
		;;
	esac
}

function transfile() 
{
	#1p-遍历路径
	#2p-目标路径
	#3p-返回路径 - 服务于css文件
	#4p-相对路径 - 服务于递归路径
	for file in `ls $1`;
    do
		if [ "$file" == "leetcode" -o "$file" == ".." ];then
			continue
		fi
		if [ "$file" == ".git" -o "$file" == ".gitignore" ];then
			continue
		fi
        if [ -d "$1/$file" ]; then
            mkdir -p "$2/$file" 
			#生成它的索引文件
			curridx="$1/$file/index.md"
			echo "## $file" > $curridx
			cat ./element/index.css >> $curridx
			echo -e "\n|目录|日期|" >> $curridx 
			echo "|----|----|" >> $curridx
			#添加返回上一层
			echo "|[返回上一层]($4/index.html)||" >> $curridx 
			#NR>1很关键， 因为ls会有个统计行数
			ls -l "$1/$file/" | awk 'NR>1' | awk '{print $6,$7,$9}'| while read MON DAY FILE;
			do
				echo "$1/$file/$FILE"
				if [ -d "$1/$file/$FILE" ];then
					url="$4/$file/${FILE}/index.html"
					echo "|[《${FILE}》]($url)|2020-$MON-$DAY|" >> $curridx
				else
					echo ${FILE} | awk -F'.' '{print $1,$2}' | while read filename filetype; 
					do
						if [ "$filetype" != "md" -o "$FILE" == "index.md" ];then
							continue
						fi
						#echo "$MON,$DAY,$FILE"
						
						url="$4/$file/${filename}.html"
						echo "|[《${filename}》]($url)|2020-$MON-$DAY|" >> $curridx
					done
				fi
			done
			if [ "$file" == "." -o "$file" == ".." ];then
				continue
			fi
            transfile "$1/$file" "$2/$file" "$3../" "$4/$file"
        else
            echo ${file} | awk -F'.' '{print $1,$2}' | while read filename filetype; do
			if [ "$filetype" != "md" ];then
				continue
			fi
			header="<base href=\"$3\">"`cat ./element/header.html`
			echo $header > tmp_header

			#索引 - 必须大写字母
			if [ "$filename" == "index" ];then
				beforebody="./element/nav-header.html"
				afterbody="./element/nav-tail.html"
			else
				beforebody="./element/body-header.html"
				cat $beforebody > tmp_body
				#返回
				echo "<a id=\"retindex\" href=\"$4/index.html\">返回目录</a>" >> tmp_body 
				beforebody="tmp_body"
				afterbody="./element/body-tail.html"
			fi

			#echo $beforebody 
			pandoc -f `getfiletype ${filetype}` -t "html" "$1/$file" -o "$2/${filename}.html" -s\
			--include-before-body="$beforebody" --include-after-body="$afterbody"\
			--include-in-header=./tmp_header --metadata title=""

			if [ "$filename" == "index" ];then
				rm "$1/$file"
			fi 
			done
        fi
    done
}

function workspace()
{
	curridx="$1/index.md"
	echo "## $4" > $curridx
	cat ./element/index.css >> $curridx
	echo -e "\n|目录|日期|" >> $curridx 
	echo "|----|----|" >> $curridx
	#添加返回上一层
	echo "|[ 返回上一层](index.html)||" >> $curridx 
	#NR>1很关键， 因为ls会有个统计行数
	ls -l "$1/" | awk 'NR>1' | awk '{print $6,$7,$9}'| while read MON DAY FILE;
	do
		echo "$1/$FILE"
		if [ -d "$1/$FILE" ];then
			url="$4/${FILE}/index.html"
			echo "|[《${FILE}》]($url)|2020-$MON-$DAY|" >> $curridx
		else
			echo ${FILE} | awk -F'.' '{print $1,$2}' | while read filename filetype; 
			do
				if [ "$filetype" != "md" -o "$FILE" == "index.md" ];then
					continue
				fi
				#echo "$MON,$DAY,$FILE"
				
				url="$4/${filename}.html"
				echo "|[《${$filename}》]($url)|2020-$MON-$DAY|" >> $curridx
			done
		fi
	done 
}
workspace "$1" "$2" "../" "$project"
transfile "$1" "$2" "../" "$project"
rm tmp_header
rm tmp_body
