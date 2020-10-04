//////////// url constant ////////////

// 网站基址
var basUrl = 'http://127.0.0.1:5000/';

// 总览模块入口地址
var overviewUrl = basUrl + 'overview';

// 测试模块入口地址
var trialUrl = basUrl + 'trial';

// 历史结果入口地址
var historyUrl = basUrl + 'history';

// 文件上传地址
var fileUploadUrl = basUrl + 'up_data';

// 获取历史结果
var historyAllResultUrl = basUrl + "history/result/all";

// 获取搜索结果
var historySearchResultUrl = basUrl + "history/result/search"


//////////// result constant ////////////
var filename = "filename";




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