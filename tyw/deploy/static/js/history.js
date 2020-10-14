// 加载立即请求数据
get_all_result();

// 获取所有数据
function get_all_result() {
    $.ajax({
        url: historyAllResultUrl,
        type: "get",
        data: {},
        success: function(data){

            //console.log(data);
            fill_table('#table-content', data);
        },
        error: function () {
            alert("请求数据失败！");
        }
    });
}

//前缀搜索
$('#search-input').on('input propertychange', function() {

    var last_table_content = $('#table-content').html();
    //console.log(last_table_content)

    var search_txt = $(this).val().trim();
    if(search_txt === '' || typeof(search_txt) === 'undefined') {
        get_all_result();

    } else {

        $.ajax({
            url: historySearchResultUrl,
            type: "get",
            data: {
                "prefix": search_txt
            },
            success: function(data){

                //console.log(data);
                if(data === [] || typeof(data) === "undefined" || data.length === 0) {
                    // 显示上次的
                    // $('#table-content').html(last_table_content);
                    fill_table('#table-content', data);
                } else {
                    fill_table('#table-content', data);
                    last_table_content = $('#table-content').html();
                }

            },
            error: function () {
                fail_prompt("搜索失败！");
            }
        })
    }
});


// 填充表格内容
var fill_table = function(domId, data) {
    var resDom = '';

    for(var i = 0; i < data.length; i++) {
        resDom = resDom + '<tr>';
        resDom = resDom + '<td>' + data[i]["filename"] + '</td>';
        resDom = resDom + '<td>' + data[i]["upload_time"] + '</td>';
        resDom = resDom + '<td>' + data[i]["aa"] + '</td>';
        resDom = resDom + '<td>' + data[i]["bb"] + '</td>';
        resDom = resDom + '<td>' + data[i]["cc"] + '</td>';
        resDom = resDom + '<td><button type="button" class="retrial-btn btn-xs btn-success" id="retrial-' + data[i]["id"] +
                          '">重测</button><button type="button" class="delete-btn btn-xs btn-danger" id="delete-' + data[i]["id"] +
                          '">删除</button><td>';
        resDom = resDom + '</tr>';
    }
    //console.log(resDom)
    $(domId).html(resDom);
}

// 删除表格一行
function delete_row() {
}

// 重测按钮
$('body').on('click', '.retrial-btn', function() {
    id = $(this).attr('id');
    fid = id.split('-')[1]

    trail_loading()

    get_retrial_result(fid, function(data) {
        hide_loading()
        console.log(data)
    })

})

// 删除按钮
$('body').on('click', '.delete-btn', function() {

    deleteDom = $(this).parent().parent()
    var msg = "确定删除吗？"
    if(!confirm(msg)) {
        return
    }
    // 确认删除后
    id = $(this).attr('id');
    fid = id.split('-')[1]
    console.log('file id: ' + fid)
    delete_record_all(fid, function(data) {
        // 删除成功后
        if(data.code === success_code) {
            deleteDom.remove()
            success_prompt("删除成功")
        } else {
            fail_prompt("删除失败")
        }

    })





})

// 重新测试
function get_retrial_result(fid, callback) {
    $.ajax({
        url: retrialUrl,
        type: "get",
        data: {
            "fid": fid
        },
        success : function(data){
            callback(data)
        },
        error: function () {
            hide_loading();
            alert("重测失败！");
        }
    })
}

// 删除记录
function delete_record_all(fid, callback) {
    $.ajax({
        url: deleteAllUrl,
        type: "post",
        data: {
            "fid": fid
        },
        success : function(data){
            callback(data)
        },
        error: function () {
            alert("删除失败！");
        }
    })
}