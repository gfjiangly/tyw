$(document).ready(function(){
    get_info(function(data) {
        $('#name').val(data.data['username'])
        $('#age').val(data.data['age'])
        $('#min-hbeat').val(data.data['min_beats'])
        $('#max-hbeat').val(data.data['max_beats'])
    })

})




// 配置按钮
$('#person-config-btn').click(function() {

    var username = $('#name').val();
    var age = $('#age').val();
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

    mLoading_mask("配置中...");
    upload_info(username, age, function(data) {
        mLoading_hide();
        $('#min-hbeat').val(data.data['min'])
        $('#max-hbeat').val(data.data['max'])
        success_prompt("配置成功！")
    })
});

// 上传测试者信息
function upload_info(username, age, callback) {

    $.ajax({
        url: uploadPersonInfoUrl,
        type: "post",
        data: {
            "username": username,
            "age": age
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