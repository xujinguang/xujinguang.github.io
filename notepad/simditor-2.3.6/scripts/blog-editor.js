(function() {
  $(function() {
    var $preview, editor, mobileToolbar, toolbar;
    Simditor.locale = 'en-US';
    toolbar = ['table', 'indent', 'outdent', 'alignment', '|', 'bold', 'italic', 'underline', 'strikethrough', 'fontScale', 'color', '|', 'blockquote', 'code', 'link', 'image', '|', 'ol', 'ul', '|', 'hr', ];

    editor = new Simditor({
        textarea: $('#txt-content'),
        placeholder: '这里输入文字...',
        toolbar: toolbar,
        pasteImage: true,
        defaultImage: 'simditor-2.3.6/images/image.png',
        upload: location.search === '?upload' ? {
        url: '/upload'
      } : false
    });

    $preview = $('#preview');
    if ($preview.length > 0) {
            return editor.on('valuechanged', function(e) {
            return $preview.html(editor.getValue());
        });
    }

    $('#where').hide();
    submit_blog(editor);
     
  });
}).call(this);

/*************************************************************************
* 方法说明：可复用的http请求发送函数
* 参数说明：
*　　method：请求方式(GET/POST)
*　　url：目标URL
*　　content：用POST方式发出请求时想传给服务器的数据，
*　　　　　　若用GET方式：请传null
*　　responseType：响应内容的格式(text/xml)
*　　callback：要回调的函数
*************************************************************************/
//定义XMLHttpRequest对象实例
var xhttp = false;

function send_request(method, url, content, responseType, callback) {
    xhttp = false;
    //初始化XMLHttpRequest对象
    if (window.XMLHttpRequest) { //Mozilla 浏览器
        xhttp = new XMLHttpRequest();
        if (xhttp.overrideMimeType) {//设置MiME类别
            xhttp.overrideMimeType("text/xml");
        }
    } else {
        if (window.ActiveXObject) { // IE浏览器
            try {
                xhttp = new ActiveXObject("Msxml2.XMLHTTP");
            }
            catch (e) {
                try {
                    xhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                catch (e) {}
            }
        }
    }
    
    if (!xhttp) { // 异常,创建对象实例失败不能创建XMLHttpRequest对象实例
        return false;
    }

    if (responseType.toLowerCase() == "text" || responseType.toLowerCase() == "xml") {
        xhttp.onreadystatechange = callback;
    } else {//"响应类别参数错误"
        return false;
    }
 
    // 确定发送请求的方式和URL以及是否异步执行下段代码
    if (method.toLowerCase() == "get") {
        xhttp.open(method, url, true);
    } else if (method.toLowerCase() == "post") {
        xhttp.open(method, url, true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    } else {//http请求类别参数错误
        return false;
    }
    //发起请求
    xhttp.send(content);
}

function submit_blog(editor){
    Date.prototype.pattern = function(fmt) {         
        var o = {         
            "M+" : this.getMonth()+1, //月份         
            "d+" : this.getDate(), //日         
            "h+" : this.getHours()%12 == 0 ? 12 : this.getHours()%12, //12小时         
            "H+" : this.getHours(), //24小时         
            "m+" : this.getMinutes(), //分         
            "s+" : this.getSeconds(), //秒         
            "q+" : Math.floor((this.getMonth()+3)/3), //季度         
            "S" : this.getMilliseconds() //毫秒         
        };
      
        if(/(y+)/.test(fmt)){         
            fmt = fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));         
        }         
        
        for(var k in o){         
            if(new RegExp("("+ k +")").test(fmt)){         
                fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));         
            }         
        }         
        return fmt;         
    } 

    var gen_subtitle = function() {
        var curr_date = new Date();
        var year = curr_date.getFullYear();       //年
        var month = curr_date.getMonth() + 1;     //月
        var day = curr_date.getDate();            //天
        var hour = curr_date.getHours();          //时
        var minute = curr_date.getMinutes();      //分

        //补前缀0
        if(month < 10)
            month = '0' + month;
        if(day < 10)
            day = '0' + day;
        if(hour < 10)
            hour = '0' + hour;   
        if(minute < 10)
            minute = '0' + minute;      
        var subtitle = year + '-' + month + '-' + day + ' ' + hour + ':' + minute;
        return subtitle;
    }

    var gen_weekday = function() {
        var curr_date = new Date();
        var  day = curr_date.getDay();
        var weekday = {
            "0" : "日",
            "1" : "一",
            "2" : "二",
            "3" : "三",
            "4" : "四",
            "5" : "五",
            "6" : "六"
        };
        return "星期" + weekday[day + ""];
    }

    //自动补全子标题
    $('#subtitle').blur(function() {
        var subtitle = $('#subtitle').val(); 
        if(subtitle == "") {
            var curr_date = new Date();
            $('#subtitle').val(curr_date.pattern("yyyy-MM-dd HH:mm:ss"));
        }
    });

    //自动签名
    $('#title').focus(function() {
        $('#where').hide();
    });
    $('#subtitle').focus(function() {
        $('#where').hide();
    });
    $('#sign').focus(function() {
        $('#where').show();
    });
    $('#where').change(function(){
        var sign = $('#sign').val();
        sign = sign + document.getElementById('where').options[document.getElementById('where').selectedIndex].value;
        $('#sign').val(sign);
        $('#where').hide();
    });

    //提交文章
    $('form').submit(function(e){
        var blog = editor.getValue();
        var title = $('#title').val();
        if(title == "") {
            alert("请输入文章标题");
            return;
        }
        var subtitle = $('#subtitle').val();
        if(subtitle == "") {
            var curr_date = new Date();
            subtitle = curr_date.pattern("yyyy-MM-dd HH:mm:ss");
            $('#subtitle').val(subtitle);
        }

        var sign = $('#sign').val();
        if(sign == "") {
            sign = "火星";
            $('#sign').val(sign);
        }

        sign = "—— " + gen_weekday() + " 于" + sign;
        
        var send_data = "_TITLE_=" + title +
                        "&_SUBTITLE_=" + subtitle +
                        "&_SIGN_=" + sign +
                        "&_BLOG_=" + blog;
        var url = "http://127.0.0.1:9999";
        alert(send_data);
        
        var response_callback = function() {
            if (xhttp.readyState !== 4) 
                return;
            if (xhttp.status !== 200) {
                alert("server error!");
                return;
            }   
            var response_str = eval('('+xhttp.responseText+')');
            // operation type 
            if (response_str.error_code === 3) {
                // not login
                document.location.href="../index.html";
                return;
            } else if (response_str.error_code !== 0) {
                alert(response_str.error_msg);
                return;
            } 
            alert('sucess');
        }   

        send_request("POST", url, encodeURI(send_data), "TEXT", response_callback); 
    });
}
