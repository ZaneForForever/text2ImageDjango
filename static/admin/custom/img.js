function show_pic(icon_url) {
    console.log("show pic!!")
    let msg_html = `<img src="${icon_url}" width="500px" />`
    // $alert接收3个参数，data，title，options
    // options使用案例可以参考https://element.eleme.cn/#/zh-CN/component/message-box#options

    Vue.prototype.$msgbox({
        // title:"大图",
        message: msg_html,
        dangerouslyUseHTMLString: true,
        showConfirmButton: false
    }).catch(function () {
    })
    // self.parent.app.$alert(msg_html, '这里是title', {
    //     dangerouslyUseHTMLString: true
    // })
}