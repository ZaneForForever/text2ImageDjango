function copy(eleId) {
    // let ele = document.getElementById(eleId);
    let clipboard = new ClipboardJS('.copy-sp');
    clipboard.on('success', function (e) {
        e.clearSelection();
        clipboard.destroy();
        alert('复制成功');
    });
    clipboard.on('error', function (e) {
        clipboard.destroy();
        alert('复制失败');
    });
}