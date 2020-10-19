$('#file-upload').fileinput({
    allowedFileExtensions: ['txt', 'csv', 'pkl'],//接收的文件后缀
    showUpload: false, //是否显示上传按钮
    showCaption: true,//是否显示标题
    browseClass: "btn btn-primary", //按钮样式
    enctype: 'multipart/form-data',
    validateInitialCount:true,
    previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
    msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
    showPreview: false
});

// 根据配置信息设置复选框
$(document).ready(function(){

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
})



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
    filename = $('#file-upload')[0].files[0]['name'];

    // 加载组件
    upload_loading()

    calculate_md5(file, function(md5) {

        // 然后传送 md5
        upload_file_attr(md5, function(data) {

            msg = data.msg

            if(msg === no_lock_msg) {
                hide_loading();
                alert('系统繁忙，请稍后重试')

            } else if(msg === file_existed_msg) {

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

            } else {
                // 上传文件
                upload_file(file, md5, filename, function(data) {

                    hide_loading();

                    // 上传成功
                    if(data.code === 1) {
                        success_prompt("上传成功")

                        trail_loading()

                        get_trial_result(md5, function(data) {

                            hide_loading();

                            if(data.code === success_code) {
                                show_result(data.data)
                            } else {
                                fail_prompt(data.msg)
                            }
                        })

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
    Object.keys(data).forEach(function(key){
         if(key !== 'fid') {
            resDom = resDom + '<h5>' + target_text_mapping[key] + ':  ' + get_target_state_text_html(key, data[key]['code'], data[key]['state']) + '</h5>';
         }
    });

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


// 上传 MD5
function upload_file_attr(md5, callback) {
     console.log(md5)

    $.ajax({
        url: fileAttrUploadUrl,
        type: "get",
        data: {
            "md5": md5
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