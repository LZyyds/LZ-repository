// 获取数据按钮点击事件
document.getElementById('submit-button').addEventListener('click', function() {
  var tableSelect = document.getElementById('table-select');
  var tableName = tableSelect.value;

  // 发送POST请求到后端
  fetch('/get_data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'table_name=' + encodeURIComponent(tableName) + '&offset=0'
  })
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    // 清空表格内容
    var tableBody = document.getElementById('data-table').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    // 处理后端返回的数据
    for (var i = 0; i < data.length; i++) {
      var rowData = data[i];
      var rowElement = document.createElement('tr');

      for (var j = 0; j < rowData.length; j++) {
        var cellData = rowData[j];
        var cellElement = document.createElement('td');
        cellElement.textContent = cellData;
        rowElement.appendChild(cellElement);
      }

      tableBody.appendChild(rowElement);
    }
  })
  .catch(function(error) {
    console.error('Error:', error);
  });
});

// 导出按钮点击事件
document.getElementById('Upload').addEventListener('click', function() {
  var tableSelect = document.getElementById('table-select');
  var tableName = tableSelect.value;

  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.style.display = 'none';
  document.body.appendChild(fileInput);

  fileInput.addEventListener('change', function() {
    const file = fileInput.files[0];
    const fileName = file.name;
    const fileInfo = document.getElementById('file-info');
    fileInfo.textContent = fileName;

    // 创建FormData对象，用于发送文件和表名
    const formData = new FormData();
    formData.append('file', file);
    formData.append('table_name', tableName);

    // 发送POST请求到后端
    fetch('/upload_data', {
      method: 'POST',
      body: formData
    })
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      var uploadMessage = document.getElementById('upload-message');
      if (data.success) {
        uploadMessage.textContent = data.message;
        uploadMessage.style.color = 'green';
      } else {
        uploadMessage.textContent = '上传失败';
        uploadMessage.style.color = 'red';
      }
    })
    .catch(function(error) {
      console.error('Error:', error);
    });

    document.body.removeChild(fileInput);
  });

  fileInput.click();
});
