//create_fileinput('#heart-file-upload', '选择测试文件');

$(document).ready(function(){

    get_info(function(data) {
        $('#name').val(data.data['username'])
        $('#age').val(data.data['age'])
        $('#min-hbeat').val(data.data['min_beats'])
        $('#max-hbeat').val(data.data['max_beats'])
    })

    minBeatsClick();
    maxBeatsClick();

})

function minBeatsClick() {
    if(is_min_checked()) {
        $('#min-hbeat').removeAttr("disabled")
    } else {
        $('#min-hbeat').attr('disabled', 'true')
    }
}

function maxBeatsClick() {
    if(is_max_checked()) {
        $('#max-hbeat').removeAttr("disabled")
    } else {
        $('#max-hbeat').attr('disabled', 'true')
    }
}



// 配置按钮
$('#person-config-btn').click(function() {

    var username = $('#name').val();
    var age = $('#age').val();
    var min_beats = $('#min-hbeat').val();
    var max_beats = $('#max-hbeat').val();

    if(username === '' || typeof(username) === "undefined") {
        fail_prompt('请输入测试者姓名！')
        return;
    } else if(age === '' || typeof(age) === "undefined") {
        fail_prompt('请输入测试者年龄！')
        return;
    } else if(isNaN(age) || age <= 0 || age >= 200) {
        fail_prompt('年龄格式不正确！')
        return;
    }

    if(is_min_checked() && (min_beats == '' || isNaN(min_beats) || min_beats < 0 || min_beats >= 400)) {
        fail_prompt("最小心率格式不正确！")
        return
    }
    if(is_max_checked() && (max_beats == '' || isNaN(max_beats) || max_beats < 0 || max_beats >= 400)) {
        fail_prompt("最大心率格式不正确！")
        return
    }

    if(!is_min_checked()) {
        min_beats = -1
    }
    if(!is_max_checked()) {
        max_beats = -1
    }

    mLoading_mask("配置中...");
    upload_info(username, age, min_beats, max_beats, function(data) {

        // 判断是否要上传文件
        beat_file = $('#heart-file-upload')[0].files[0];

        if(typeof(beat_file) === 'undefined' || beat_file === null) {
            mLoading_hide();
            $('#min-hbeat').val(data.data['min'])
            $('#max-hbeat').val(data.data['max'])
            success_prompt("配置成功！")
            return
        }

        // 上传文件
        upload_hbeat_file(beat_file, username, function(data2) {
            console.log(data2)
            mLoading_hide();
            $('#min-hbeat').val(data2.data['min'])
            $('#max-hbeat').val(data.data['max'])
            success_prompt("配置成功！")
        })

    })
});

// 上传测试者信息
function upload_info(username, age, min_beats, max_beats, callback) {

    $.ajax({
        url: uploadPersonInfoUrl,
        type: "post",
        data: {
            "username": username,
            "age": age,
            "min_beats": min_beats,
            "max_beats": max_beats
        },
        success : function(data){
            callback(data)
        },
        error: function () {
            mLoading_hide()
            alert("上传失败！");
        }
    })

}

// 获取测试者信息
function get_info(callback) {
    $.ajax({
        url: getPersonInfoUrl,
        type: "get",
        data: {
        },
        success : function(data){
            callback(data)
        },
        error: function () {
            alert("获取失败！");
        }
    })
}

// 上传文件
function upload_hbeat_file(file, username,  callback) {
    var form = new FormData();
    form.append("data", file)
    form.append("username", username)

    $.ajax({
        url: uploadHeartBeatFileUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("上传文件失败！");
        }
    })
}

// 最小心率复选框是否被勾中
function is_min_checked() {
    return document.getElementsByName('check')[0].checked;
}

// 最大心率复选框是否被勾中
function is_max_checked() {
    return document.getElementsByName('check')[1].checked;
}