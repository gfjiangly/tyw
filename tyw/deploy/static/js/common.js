//////////// url constant ////////////

// 网站基址
//var basUrl = 'http://127.0.0.1:5000/';
var basUrl = '/';

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

// 体态文件上传地址
var bodyFileUploadUrl = basUrl + "up_body";

// 上传温度、当前心率、血氧饱和度
var healthConfigUploadUrl = basUrl + "up_health_config"

// 获取健康数据
var getHealthConfigUrl = basUrl + "config/health"

// 获取历史结果
var historyAllResultUrl = basUrl + "history/result/all";

// 获取搜索结果
var historySearchResultUrl = basUrl + "history/result/search";

// 图像入口地址
var graphUrl = basUrl + "graph/"

// 获取图像数据
var getGraphDataUrl = basUrl + "graph/data"

// 重新测试
var retrialUrl = "do_trial";

// 删除有关该文件的所有记录
var deleteAllUrl = 'delete/all';

// 上传测试者信息
var uploadPersonInfoUrl = 'person/upload/info';

// 上传心率文件
var uploadHeartBeatFileUrl = 'person/upload/file'

// 获取测试者信息
var getPersonInfoUrl = "person/info";



//////////// result constant ////////////
var filename = "filename";


//////////// status constant ////////////

// 通用的成功代码
var success_code = 1;

// 文件已存在的消息
var file_existed_msg = "existed";

// 获取不到锁
var no_lock_msg = "nolock";

// 没有配置用户
var no_user_msg = "nouser";

// 用户未找到
var user_no_found_msg = "nofound";

// 指标
var TARGET_ITEM  = ['hungry', 'fear', 'tired', 'health', 'comprehensive'];

var HEALTH_CONFIG_ITEM = ['temperature', 'curr_heart_rate', 'blood_oxygen']

var CONFIG_ITEM = ['HUNGRY_MODEL', 'FEAR_MODEL', 'TIRED_MODEL', 'HEALTH_MODEL', 'FITNESS_MODEL']


// 指标状态
var HUNGRY_STATE = 1;
var NOT_HUNGRY_STATE = 0;
var FEAR_STATE = 1;
var NOT_FEAR_STATE = 0;
var CC_STATE = 1;
var NOT_CC_STATE = 0;
var NO_STATE = -1;


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

/////////////////////////////////////////////////////////////////

// 文字信息
/**
 * 文字信息
 * @param dom 显示文字的 DOM
 * @param text 文字
 * @param type 类型 【default, info, success, warning, fail】
 */
var type_color_mapping = {'default': '#888', 'info': '#0099FF', 'success': '#228B22', 'warning': '#F7C709', 'fail': '#FF0000', 'black': '#000000'}
var text_rendering = function(dom, text, type) {
    dom.text(text).css('color', type_color_mapping[type])
}

var success_text = function(dom, text) {
    text_rendering(dom, text, 'success')
}

var default_text = function(dom, text) {
    text_rendering(dom, text, 'default')
}

var info_text = function(dom, text) {
    text_rendering(dom, text, 'info')
}

var warning_text = function(dom, text) {
    text_rendering(dom, text, 'warning')
}

var fail_text = function(dom, text) {
    text_rendering(dom, text, 'fail')
}

var black_text = function(dom, text) {
    text_rendering(dom, text, 'black')
}

// 根据指标状态设置文本
var target_text_mapping = {'hungry': '饥饿状态', 'fear': '恐惧状态', 'tired': '疲劳状态', 'comprehensive': '综合状态', 'health': '健康状态'}
var target_result_mapping = {'hungry': ['不饥饿', '饥饿'], 'fear': ['不恐惧', '恐惧'], 'tired': ['不疲劳', '疲劳'], 'comprehensive': ['不好', '好'], 'health': ['健康', '异常']}
var code_status_mapping = {'0': '未开启测试', '1': '未知', '-1': '测试数据长度不够', '-401': '上传未测试' }

var set_target_state_text = function(dom, target_title, code, state) {

    state = parseInt(state);

    code = parseInt(code)
    //console.log(code)

    if(isNaN(code)  || typeof(code) === "undefined" || code === 'null' || code === '') {
        code = '-401'
    }

    code = code.toString()
    if(code === '1') {
        text = target_result_mapping[target_title][state]
        console.log(state)

        if(state === NO_STATE) {
            default_text(dom, '未知')
        } else if(state === 0) {

            success_text(dom, text)

        } else if(state === 1) {

            fail_text(dom, text)
        }
    } else if(code === '0') {
        info_text(dom, code_status_mapping[code])
    } else {
        warning_text(dom, code_status_mapping[code])
    }


}

// 设置综合指标
var set_comprehensive_state_text = function(dom, code, state) {
    state = parseInt(state);
    code = parseInt(code)

    if(isNaN(code)  || typeof(code) === "undefined" || code === 'null' || code === '') {
        code = '-401'
    }

    code = code.toString()
    if(code === '1') {

        text = state

        if(state === NO_STATE) {
            default_text(dom, '未知')
        } else {
            success_text(dom, text)
        }

    } else if(code === '0') {
        info_text(dom, code_status_mapping[code])
    } else {
        warning_text(dom, code_status_mapping[code])
    }
}


// 获取某项指标对应的文字
var get_target_state_text_html = function(target_title, code, state) {

    state = parseInt(state);

    code = parseInt(code)
    //console.log(code)
    text = target_result_mapping[target_title][state]
    color = ''

    if(isNaN(code)  || typeof(code) === "undefined" || code === 'null' || code === '') {
        code = '-401'
    }

    code = code.toString()
    if(code === '1') {
        if(state === NO_STATE) {
            text = '未知'
            color = type_color_mapping['default']
        } else if(state === 0) {

            color = type_color_mapping['success']
        } else if(state === 1) {

            color = type_color_mapping['fail']

        }
    } else if(code === '0') {
        color = type_color_mapping['info']
        text = code_status_mapping[code]
    } else {
        color = type_color_mapping['warning']
        text = code_status_mapping[code]
    }


    resDom = '<span style="color:' + color + '">' + text + '</span>';
    return resDom;
}

// 获取综合指标
var get_comprehensive_state_text_html = function(code, state) {

    code = parseInt(code)
    color = ''
    text = ''

    if(isNaN(code)  || typeof(code) === "undefined" || code === 'null' || code === '') {
        code = '-401'
    }

    code = code.toString()
    if(code === '1') {
        if(state === NO_STATE) {
            text = '未知'
            color = type_color_mapping['default']
        } else {
            color = type_color_mapping['black']

            ours = state['ours']
            sport = state['sport']

            ours_text = '体态综合识别结果: ' + ours + '%(强度: >45%，较强)';
            sport_text = '基于运行状态识别结果: ' + sport + '%(强度: <=45%，较弱)';

            resDom = '<h5><span style="color:' + color + '">' + ours_text + '</span></h5>' +
                     '<h5><span style="color:' + color + '">' + sport_text + '</span></h5>';

            return resDom;
        }

    } else if(code === '0') {
        color = type_color_mapping['info']
        text = code_status_mapping[code]
    } else {
        color = type_color_mapping['warning']
        text = code_status_mapping[code]
    }


    resDom = '<h5>综合状态: <span style="color:' + color + '">' + text + '</span></h5>';
    return resDom;
}
//var get_comprehensive_state_text_html = function(code, state) {
//
//    state = parseInt(state);
//
//    code = parseInt(code)
//    //console.log(code)
//    text = state
//    color = ''
//
//    if(isNaN(code)  || typeof(code) === "undefined" || code === 'null' || code === '') {
//        code = '-401'
//    }
//
//    code = code.toString()
//    if(code === '1') {
//        if(state === NO_STATE) {
//            text = '未知'
//            color = type_color_mapping['default']
//        } else {
//            color = type_color_mapping['success']
//        }
//
//    } else if(code === '0') {
//        color = type_color_mapping['info']
//        text = code_status_mapping[code]
//    } else {
//        color = type_color_mapping['warning']
//        text = code_status_mapping[code]
//    }
//
//
//    resDom = '<span style="color:' + color + '">' + text + '</span>';
//    return resDom;
//}


// 文件上传框
// 产生文件上传的控件
function create_fileinput(domId, title) {
    $(domId).fileinput({
        language: 'zh', //设置语言
        browseLabel: title,
        allowedFileExtensions: ['txt', 'csv', 'pkl', 'xlsx', '.xls'],//接收的文件后缀
        showUpload: false, //是否显示上传按钮
        showCaption: true,//是否显示标题
        browseClass: "btn btn-primary", //按钮样式
        enctype: 'multipart/form-data',
        validateInitialCount:true,
        previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
        msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
        showPreview: false
    });

}