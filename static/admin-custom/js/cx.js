export default function CxHttpPost(url, body, callback, failedCallback) {
    let httpRequest = new XMLHttpRequest();//第一步：创建需要的对象
    httpRequest.open('POST', url, true); //第二步：打开连接
    httpRequest.send(body);//发送请求 将情头体写在send中
    /**
     * 获取数据后的处理程序
     */
    httpRequest.onreadystatechange = function () {//请求后的回调接口，可将请求成功后要执行的程序写在其中
        if (httpRequest.readyState == 4) {
            if (httpRequest.status == 200) {//验证请求是否发送成功
                let json = httpRequest.responseText;//获取到服务端返回的数据
                callback(json)
            } else {
                failedCallback(httpRequest.status)
            }
        }

    };
}

