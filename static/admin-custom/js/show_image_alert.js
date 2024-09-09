function show_pic(icon_url) {
    let msg_html = `<img src="${icon_url}" width="600px" />`
    // $alert接收3个参数，data，title，options
    // options使用案例可以参考https://element.eleme.cn/#/zh-CN/component/message-box#options
    self.parent.app.$alert(msg_html, 'Zane', {
        dangerouslyUseHTMLString: true
    })


    
}