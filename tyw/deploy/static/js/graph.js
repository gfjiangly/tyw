// 立马请求图像数据
get_graph_data(fid)

// 基于准备好的dom，初始化echarts实例
var hungryChart = echarts.init(document.getElementById('graph-hungry'));
var fearChart = echarts.init(document.getElementById('graph-fear'));
var ccChart = echarts.init(document.getElementById('graph-cc'));

// 指定图表的配置项和数据
function createOption(title, data) {

    xData = Array.from({length: data.length}, (v,k) => k);

//    option = {
//        title: {
//            text: title
//        },
//        tooltip: {
//            trigger: 'axis'
//        },
//        toolbox: {
//            feature: {
//                saveAsImage: {}
//            }
//        },
//        xAxis: {
//            type: 'category',
//            data: xData,
//            name: '时间'
//        },
//        yAxis: {
//            type: 'value',
//            name: '指标值'
//        },
//        dataZoom: [
//            {
//                type: 'inside',
//                xAxisIndex: [0],
//                start: 0,
//                end: 100
//            },
//        ],
//        series: [{
//            data: data,
//            type: 'line',
//            step: 'start'
//        }]
//    };
    option = {
        title: {
            text: title
        },
        tooltip: {
            trigger: 'axis'
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        xAxis: {
            name: '时间',
            type: 'category',
            data: xData
        },
        yAxis: {
            name: '指标值',
            type: 'value'
        },
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0],
                start: 0,
                end: 100
            },
        ],
        series: [
            {
                type: 'line',
                step: 'start',
                data: data
            },
        ]
    };

    return option
}


// 获取数据
function get_graph_data() {
    $.ajax({
        url: getGraphDataUrl,
        type: "get",
        data: {
            'fid': fid
        },
        success: function(data){

            console.log(data);
            if(data.code === success_code) {

                dataArr = data.data

                $(document).attr("title",dataArr[0]);
                $('#graph-header .filename').text('测试文件：' + dataArr[0])
                $('#graph-header .trial-time').text('测试时间：' + dataArr[1])


                // 使用刚指定的配置项和数据显示图表。
                if(dataArr[2].length !== 0) {
                    hungryChart.setOption(createOption('饥饿指标图', dataArr[2]));
                } else {
                    $('#graph-hungry').remove()
                }

                if(dataArr[3].length !== 0) {
                    fearChart.setOption(createOption('恐惧指标图', dataArr[3]));
                } else {
                    $('#graph-fear').remove()
                }

                if(dataArr[4].length !== 0) {
                    ccChart.setOption(createOption('cc 指标图', dataArr[4]));
                } else {
                    $('#graph-cc').remove()
                }



            } else {
                $('body').html('<h2>获取失败</h2>')
            }
        },
        error: function () {
            alert("请求数据失败！");
        }
    });
}