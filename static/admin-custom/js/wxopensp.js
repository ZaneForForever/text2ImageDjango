export default function wxOpenSp(template_id, controls) {
    console.log('controls length is ' + controls.length)
    let fields_data = []
    for (let i = 0; i < controls.length; i++) {
        let control = controls[i]
        let type = control['property']['control']
        let valueControl = control['value']
        let value
        if (valueControl instanceof Array) {
            if (type == 'File') {
                console.log('is file')
                console.log(valueControl)
                if (valueControl.length == 1) {
                    value = valueControl[0]['oa_file_id']
                } else if (valueControl.length >= 2) {
                    let values = []
                    for (let j = 0; j < valueControl.length; j++) {
                        values.push(valueControl[j]['oa_file_id'])
                    }
                    value = values
                }
            } else {
                value = valueControl[0]['label']
            }
        } else {
            value = valueControl
            if (type == 'Date') {
                value = value.replace('-', '/')
                value = value.replace('-', '/')
            }
        }
        let field = {
            'title': control['property']['title'][0]['text'], 'type': type.toLowerCase(), 'value': value
        }
        fields_data.push(field)
    }
    console.log(fields_data)
    const exData = {
        'fieldList': fields_data
    }
    const json = JSON.stringify(exData)
    console.log('json is ' + json)
    wx.invoke('thirdPartyOpenPage', {
        "oaType": "10001",// String
        "templateId": '8609919e0366af385c3a47ec2f0d0e4c_1665917517',// String
        "thirdNo": fields_data[0]['value'],// String
        "extData": JSON.parse(json)
    }, function (res) {
        console.log('调用完成')
        console.log(res)
        // alert(res.errMsg + ' 审批单号:' + sp_no)
    });
}