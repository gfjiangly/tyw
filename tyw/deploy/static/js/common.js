//////////// url constant ////////////

// 网站基址
var basUrl = 'http://127.0.0.1:5000/';

// 总览模块入口地址
var overviewUrl = basUrl + 'overview';

// 测试模块入口地址
var trialUrl = basUrl + 'trial';

// 历史结果入口地址
var historyUrl = basUrl + 'history';

// 文件属性上传地址
var fileAttrUploadUrl = basUrl + 'up_md5';

// 文件上传地址
var fileUploadUrl = basUrl + 'up_data';

// 获取历史结果
var historyAllResultUrl = basUrl + "history/result/all";

// 获取搜索结果
var historySearchResultUrl = basUrl + "history/result/search";

// 重新测试
var retrialUrl = "retrial";

// 删除有关该文件的所有记录
var deleteAllUrl = 'delete/all';


//////////// result constant ////////////
var filename = "filename";


//////////// status constant ////////////

// 通用的成功代码
var success_code = 1;

// 文件已存在的消息
var file_existed_msg = "existed";

// 获取不到锁
var no_lock_msg = "nolock";



//////////// common function ////////////

$('.navbar-brand').attr('href', basUrl);

// 弹出提示框
/**
 * 弹出式提示框，默认1.2秒自动消失
 * @param message 提示信息
 * @param style 提示样式，有alert-success、alert-danger、alert-warning、alert-info
 * @param time 消失时间
 */
var prompt = function (message, style, time)
{
    style = (style === undefined) ? 'alert-success' : style;
    time = (time === undefined) ? 1200 : time;
    $('<div id="promptModal">')
        .appendTo('body')
        .addClass('alert '+ style)
        .css({"display":"block",
            "z-index":99999,
            "left":($(document.body).outerWidth(true) - 120) / 2,
            "top":($(window).height() - 45) / 2,
            "position": "absolute",
            "padding": "20px",
            "border-radius": "5px"})
        .html(message)
        .show()
        .delay(time)
        .fadeOut(10,function(){
            $('#promptModal').remove();
        });
};

// 成功提示
var success_prompt = function(message, time)
{
    prompt(message, 'alert-success', time);
};

// 失败提示
var fail_prompt = function(message, time)
{
    prompt(message, 'alert-danger', time);
};

// 提醒
var warning_prompt = function(message, time)
{
    prompt(message, 'alert-warning', time);
};

// 信息提示
var info_prompt = function(message, time)
{
    prompt(message, 'alert-info', time);
};

// 信息提示
var alert_prompt = function(message, time)
{
    prompt(message, 'alert-pormpt', time);
};
/////////////////////////////////////////////////////////////////

// loading
/**
 * 加载中..遮罩
 * @param text 加载文字
 * @param dom  将 loading 套在指定元素
 */
var mLoading_mask = function(text, dom) {
    text = (text === undefined) ? 'loading...' : text;
    dom = (dom === undefined) ? $('body') : dom;
    dom.mLoading({
        text:text,//加载文字，默认值：加载中...
        //icon:"",//加载图标，默认值：一个小型的base64的gif图片
        html:false,//设置加载内容是否是html格式，默认值是false
        content:"",//忽略icon和text的值，直接在加载框中显示此值
        mask:true//是否显示遮罩效果，默认显示
    });
}

var mLoading_hide = function(dom) {
    dom = (dom === undefined) ? $('body') : dom;
    dom.mLoading("hide");
}

var upload_loading = function() {
    mLoading_mask("上传中...");
}

var trail_loading = function() {
    mLoading_mask("测试中...");
}


var hide_loading = function() {
    mLoading_hide();
}

