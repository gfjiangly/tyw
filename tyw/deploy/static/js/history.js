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


var fill_table = function(domId, data) {
    var resDom = '';

    for(var i = 0; i < data.length; i++) {
        resDom = resDom + '<tr>';
        resDom = resDom + '<td>' + data[i]["filename"] + '</td>';
        resDom = resDom + '<td>' + data[i]["trial_time"] + '</td>';
        resDom = resDom + '<td>' + data[i]["aa"] + '</td>';
        resDom = resDom + '<td>' + data[i]["bb"] + '</td>';
        resDom = resDom + '<td>' + data[i]["cc"] + '</td>';
        resDom = resDom + '</tr>';
    }
    $(domId).html(resDom);
}
