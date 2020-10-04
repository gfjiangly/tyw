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

$('#upload-btn').click(function(){

    var form = new FormData();
    form.append("data", $('#file-upload')[0].files[0]);
    form.append("filename", $('#file-upload')[0].files[0]['name'])

    $.ajax({
        url: fileUploadUrl,
        type: "post",
        data: form,
        processData : false,
        contentType : false,
        success : function(data){

            console.log(data);

            success_prompt("上传成功", 1200)

            var resDom = '';
            Object.keys(data).forEach(function(key){
                 resDom = resDom + '<h4>' + key + ' : ' + data[key] + '</h4>';
            });
            $('.trial-result').html(resDom);
        },
        error: function () {
            alert("上传失败！");
        }
    });

});
