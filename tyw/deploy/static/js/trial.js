create_fileinput('#file-upload', '选择测试文件');

// 根据配置信息设置复选框
$(document).ready(function(){

    // 获取配置信息
    get_info(function(data) {
        if(data.code === success_code) {
            $('#trial_person_text').val(data.data['username'])
        } else {
            $('#trial_person_text').val('无（请先配置）')
        }
    })

    config = JSON.parse(config)
    // 设置测试配置
    TARGET_ITEM.forEach(function(item) {
        //console.log(config[item])
        domId = item + '-check';
        if(config[item] === true) {
            $('#' + domId).attr("checked", 'true');
        } else {
            $('#' + domId).attr("disabled", 'disabled');
            $('#' + domId).parent().css("color", "#ccc")
        }
    })

    compreClick();
})



// 综合复选框是否选中
function compreClick() {

    var checked = document.getElementsByName('check')[4].checked;

    if(checked) {
        dom = '<input id="file2-upload" name="data" class="file" type="file" data-theme="fas">'

        $('#file2_upload_div')
        $('#file2_upload_div').html(dom)
        create_fileinput('#file2-upload', '选择体态文件')

    } else {
        $('#file2_upload_div').empty();
    }
}


// 计算文件的 md5
function calculate_md5(file, callback) {
    var blobSlice = File.prototype.slice || File.prototype.mozSlice || File.prototype.webkitSlice,
        chunkSize = 2097152,                             // Read in chunks of 2MB
        chunks = Math.ceil(file.size / chunkSize),
        currentChunk = 0,
        spark = new SparkMD5.ArrayBuffer(),
        fileReader = new FileReader();

    fileReader.onload = function (e) {
        spark.append(e.target.result);                   // Append array buffer
        currentChunk++;

        if (currentChunk < chunks) {
            loadNext();
        } else {
            callback(spark.end());  // Compute hash
        }
    };

    fileReader.onerror = function () {
        console.warn('oops, something went wrong.');
    };

    function loadNext() {
        var start = currentChunk * chunkSize,
            end = ((start + chunkSize) >= file.size) ? file.size : start + chunkSize;

        fileReader.readAsArrayBuffer(blobSlice.call(file, start, end));
    }

    loadNext();
}


// 点击上传按钮
$('#upload-btn').click(function(){

    // 首先求文件的 md5
    file = $('#file-upload')[0].files[0];

    if(typeof(file) === 'undefined' || file === null) {
        fail_prompt("测试文件不能为空")
        return
    }

    filename = $('#file-upload')[0].files[0]['name'];

    // 加载组件
    upload_loading()

    calculate_md5(file, function(md5) {

        username = $('#trial_person_text').val();
        console.log(username)

        // 然后传送 md5
        upload_file_attr(md5, username, function(data) {

            msg = data.msg

            if(msg == no_user_msg) {
                hide_loading();
                alert("请先配置测试者信息");
                return;
            } else if(msg === user_no_found_msg) {
                hide_loading();
                alert("测试者不存在，请先配置");
                return;
            }

            if(msg === no_lock_msg) {
                hide_loading();
                alert('系统繁忙，请稍后重试')

            } else if(msg === file_existed_msg) {

                wrap_upload(md5)

            } else {
                // 上传文件
                upload_file(file, md5, filename, function(data) {

                    hide_loading();

                    // 上传成功
                    if(data.code === 1) {

                        wrap_upload(md5)

                    } else {
                        fail_prompt("上传失败")
                    }

                })
            }


        })
    });


});

function show_result(data) {
    success_prompt("测试成功")
    var resDom = '';

    target_count = TARGET_ITEM.length
    for(var i = 0; i < target_count; i++) {
        key = TARGET_ITEM[i]
        resDom = resDom + '<h5>' + target_text_mapping[key] + ':  ' + get_target_state_text_html(key, data[key]['code'], data[key]['state']) + '</h5>';
    }

    //Object.keys(data).forEach(function(key){
    //     if(key !== 'fid') {
    //       resDom = resDom + '<h5>' + target_text_mapping[key] + ':  ' + get_target_state_text_html(key, data[key]['code'], data[key]['state']) + '</h5>';
    //     }
    //});

    // 查看图像的按钮不要了
    //resDom = resDom + '<button type="button" style="margin-left: 50px; margin-top: 5px" class="view-btn btn-xs btn-default" id="view-' + data["fid"] +
    //  '">查看图像</button>';

    $('.trial-result').html(resDom);
}


// 查看曲线图
$('body').on('click', '.view-btn', function() {

    id = $(this).attr('id');
    fid = id.split('-')[1]
    url = graphUrl + fid
    window.open(url)
})


// 上传 MD5 和 用户名
function upload_file_attr(md5, username, callback) {
     console.log(md5)

    $.ajax({
        url: fileAttrUploadUrl,
        type: "get",
        data: {
            "md5": md5,
            "username": username
        },
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("上传失败！");
        }
    })
}

// 上传文件
function upload_file(file, md5, filename, callback){

    var form = new FormData();
    form.append("data", file);
    form.append("md5", md5);
    form.append("filename", filename)
//    form.append("config", get_checkbox_value())

//    $('.trial-result').html('<h4>检测中...</h4>');
    // info_prompt("正在上传");

    $.ajax({
        url: fileUploadUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("上传失败！");
        }
    });
}

// 上传体态文件
// file1_md5 用于与测试文件绑定
function upload_body_file(file, filename, file1_md5, callback) {

    var form = new FormData();
    form.append("data", file);
    //form.append("md5", file1_md5);
    form.append("filename", filename);

    $.ajax({
        url: bodyFileUploadUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("上传失败！");
        }
    });
}

// 根据存在的 md5 测试
function get_trial_result(md5, callback) {

    var form = new FormData();
    form.append("fid", '');
    form.append("md5", md5);
    form.append("config", get_checkbox_value())
    form.append("save_config", true)

    $.ajax({
        url: retrialUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("测试失败！");
        }
    })
}

// 包装函数
function wrap_upload(md5) {
    // 体态文件暂时不考虑md5
    // 判断是否勾选了“综合”
    if(is_compre_checked()) {

        // 上传体态文件
        // 1.判断是否有选择测试文件
        // 这里不需要判断，因为如果没有选择测试文件，filename = $('#file-upload')[0].files[0]['name']; 就会报错

        // 2.上传体态文件
        body_file = $('#file2-upload')[0].files[0];

        if(typeof(body_file) === 'undefined' || body_file === null) {
            fail_prompt("体态文件不能为空")
            hide_loading();
            return
        }

        body_filename = $('#file2-upload')[0].files[0]['name'];
        upload_body_file(body_file, body_filename, md5, function(data) {

            console.log("上传体态文件");
            hide_loading();
            trail_loading();
            get_trial_result(md5, function(data) {

                //console.log(data)
                hide_loading();

                if(data.code === success_code) {
                    show_result(data.data)
                } else {
                    fail_prompt(data.msg)
                }
            })
        })

    } else {

        hide_loading();
        trail_loading();
        // 文件已存在
        // 直接测试
        get_trial_result(md5, function(data) {

            console.log(data)
            hide_loading();

            if(data.code === success_code) {
                show_result(data.data)
            } else {
                fail_prompt(data.msg)
            }
        })
    }
}



// 复选框
function get_checkbox_value(){
    dic = {}
    var obj=document.getElementsByName('check');
    for(var i = 0; i < obj.length; i++) {

        if(obj[i].checked) {
            dic[CONFIG_ITEM[i]] = true
        } else {
            dic[CONFIG_ITEM[i]] = false
        }
    }
    console.log(dic)
    return JSON.stringify(dic)
}

function is_compre_checked() {
    return document.getElementsByName('check')[4].checked;
}

// 全选
function set_checkbox_all() {
    $('[name="check"]').attr("checked",'true')
}

// 取消全选
function set_checkbox_none() {
    $('[name="check"]').removeAttr('checked')
}



// 开关按钮
//$('[name="status"]').bootstrapSwitch({    //初始化按钮
//       onText:"开启",
//       offText:"关闭",
//       onColor:"success",
//       offColor:"info",
//       onSwitchChange:function(event,state){
//          if(state==true){
//               console.log("开启");
//             }else{
//              console.log("关闭");
//             }
//         }
//});
//
//$('[name="status"]').bootstrapSwitch("size","small");
//$('[name="status"]').bootstrapSwitch('state',true);