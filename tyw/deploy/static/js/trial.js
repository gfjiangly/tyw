$('#file-upload').fileinput({
    allowedFileExtensions: ['txt', 'csv', 'pkl'],//接收的文件后缀
    showUpload: false, //是否显示上传按钮
    showCaption: true,//是否显示标题
    browseClass: "btn btn-primary", //按钮样式
    enctype: 'multipart/form-data',
    validateInitialCount:true,
    previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
    msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
});



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
        upload_file_attr(md5, function(msg) {

            if(msg === no_lock_msg) {
                hide_loading();
                alert('当前有其他用户在上传大文件，请稍后重试')

            } else if(msg === file_existed_msg) {

                // 文件已存在
                hide_loading();
                alert('该文件已存在或当前有其他用户在上传该文件，请不要重复上传')

            } else {
                // 上传文件
                upload_file(file, md5, filename, function(data) {

                    hide_loading();

                    // 上传结果处理
                    if(data.code === 1) {
                        success_prompt("上传成功")
                    } else {
                        fail_prompt("上传失败")
                    }

                })
            }
        })
    });


});

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
            callback(data.msg)
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

    $('.trial-result').html('<h4>检测中...</h4>');
    // info_prompt("正在上传");

    $.ajax({
        url: fileUploadUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){
            callback(data)
            // console.log(data);
//            success_prompt("检测成功", 1200)
//
//            var resDom = '';
//            Object.keys(data).forEach(function(key){
//                 resDom = resDom + '<h4>' + key + ' : ' + data[key] + '</h4>';
//            });
//            $('.trial-result').html(resDom);
        },
        error: function () {
            hide_loading();
            alert("上传失败！");
        }
    });
}