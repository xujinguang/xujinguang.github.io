#!/bin/bash
#$1-源文件目录
#$2-目标目录
set +x
if [ $# != 2 ] ; then
	echo "./genHtml.sh dest"
	exit
fi
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
	#3p-相对路径
	for file in `ls $1`;
    do
        if [ -d "$1/$file" ]; then
            mkdir -p "$2/$file" 
            transfile "$1/$file" "$2/$file" "$3../" 
        else
            echo ${file} | awk -F'.' '{print $1,$2}' | while read filename filetype; do
			if [ "$filetype" != "md" ];then
				continue
			fi
			header="<base href=\"$3\">"`cat ./element/header`
			echo $header > tmp_header
			pandoc -f `getfiletype ${filetype}` -t "html" "$1/$file" -o "$2/${filename}.html" -s\
			--include-before-body=./element/body-header --include-after-body=./element/body-tail\
			--include-in-header=./tmp_header
			done
        fi
    done
}
obj=`pwd $2`
#cd "$1"
#echo $obj
transfile "$1" "$2" "../"
rm tmp_header
