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
    $('#subclass-name').hide();
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

/*
//测试回调
function process_response(){
    //响应完成且响应正常
    if(xhttp.readyState == 1){
        alert("XMLHttpRequest对象开始发送请求");
    }else if(xhttp.readyState == 2){
        alert("XMLHttpRequest对象的请求发送完成");
    }else if(xhttp.readyState == 3){
        alert("XMLHttpRequest对象开始读取服务器的响应");
    }else if(xhttp.readyState == 4){
        alert("XMLHttpRequest对象读取服务器响应结束");
        //if(xhttp.status == 200 || xhttp.status == 0){
        alert("xhttp="+xhttp);
        if(xhttp.status == 200) {
            //信息已经成功返回，开始处理信息
            //先捕获下所有的请求头
            var headers = xhttp.getAllResponseHeaders();
            alert("所有的请求头= "+headers);
            //得到服务器返回的信息
            var infor = xhttp.responseText;
            alert("服务器端的响应 = "+infor);
        }else{
            alert("所请求的服务器端出了问题"+xhttp.status);
        }
    }
}
*/

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

    // 确定发送请求的方式和URL以及是否异步执行下段代码
    if (method.toLowerCase() == "get") {
        xhttp.open(method, url, true);
    } else if (method.toLowerCase() == "post") {
        xhttp.open(method, url, true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    } else {//http请求类别参数错误
        return false;
    }
    //设置回调
    if (responseType.toLowerCase() == "text" || responseType.toLowerCase() == "xml") {
        xhttp.onreadystatechange = callback;
        //xhttp.onreadystatechange = process_response;
    } else {//"响应类别参数错误"
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


    var gen_subclass = function(class_id) {
        var subclass = document.getElementById('subclass-name');
        //清空
        subclass.options.length = 0;
        var subclass_name = [];
        switch(class_id) {
            case 7:
                subclass_name = ['----', '数据结构','算法','编译','Lisp','C', 'C++','Python','PHP','Shell','Linux','网络','数据库','操作系统','机器学习','人工智能','web','黑客'];
                break;
            case 10:
                subclass_name = ['----','矩阵','数值分析','运筹学','算法','代数','几何学','概率统计'];
                break;
            case 17:
                subclass_name = ['----','小说','诗词','散文','名著'];
                break;
            default:
                break;
        }
        for(var i = 0; i < subclass_name.length; ++i) {
            subclass.add(new Option(subclass_name[i], subclass_name[i]));
        }
    }

    var type_id = 1;  //默认博客
    var class_id = 0; //默认其他
    var subclass_id = 0; //默认其他

    $('#type-name').change(function(){
        type_name = document.getElementById('type-name').selectedIndex;
    });

    $('#class-name').change(function(){
       class_id = document.getElementById('class-name').selectedIndex;
       //alert(class_id);
       subclass_id = 0;
       if(class_id == 7 || class_id == 10 || class_id == 17) {
            gen_subclass(class_id);
            $('#subclass-name').show();
       } else {
            $('#subclass-name').hide();
       }
    });

    $('#subclass-name').change(function(){
        subclass_id = document.getElementById('subclass-name').selectedIndex;
    });

    //提交文章
    $('form').submit(function(e){
        //阻止默认行为，也可以用隐藏ifream
        //e.preventDefault();
        //设置5s刷新页面
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

        var blog = editor.getValue();

        var key_word = $('#key-word').val();

        var sign = $('#sign').val();
        if(sign == "") {
            sign = "火星";
            $('#sign').val(sign);
        }

        sign = "—— " + gen_weekday() + " 于" + sign;

        var send_data = "op_=1" + //保存博客
                        "_&_title__=" + title +
                        "_&_subtitle__=" + subtitle +
                        "_&_key__=" + key_word +
                        "_&_sign__=" + sign +
                        "_&_type__=" + type_id +
                        "_&_class__=" + class_id +
                        "_&_subclass__=" + subclass_id +
                        "_&_blog__=" + blog;
        alert(send_data);
        
        //var url = "http://192.168.1.2:8080";
        var url = "http://localhost:8080";
        var callback = function() {
            if (xhttp.readyState == 4){ //4表示和服务器端的交互已经完成
                if (xhttp.status == 200) {
                    var response_str = xhttp.responseText; //服务器端需要设置content-type为text/xml
                    ret = response_str.split('=');
                    if(ret[1] == 0) {
                        swal("提交成功", "赶紧到Github发布吧！", "success", "Cool");
                        //定时刷新编辑器和打开分类主页
                        setTimeout(function(){
                                url = '../index.html';
                                switch(type_name) {
                                case 1:
                                url = '../blog.html';
                                break;
                                case 2:
                                url = '../read.html';
                                break;
                                case 3:
                                url = '../scope.html';
                                break;
                                case 4:
                                url = '../science.html';
                                break;
                                case 5:
                                url = '../literature.html';
                                break;
                                }
                                window.location.href = "notepad.html";
                                window.open(url);
                                }, 3000);
                    }else {
                        swal("提交失败", "服务器处理出错！", "error", "Cool");
                    }

                } else {
                    //本地运行status=0,跨域名访问，在server端加上域名控制
                    swal("提交失败", "服务器完蛋了，请重启服务！", "error", "Cool");
                }   
            }
        }   

        send_request("POST", url, send_data, "TEXT", callback); 
    });
}
