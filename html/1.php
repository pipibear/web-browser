<html>
<head>
<script src="qwebchannel.js" type="text/javascript"></script>
<script src="html2canvas.js" type="text/javascript"></script>
<script>
window.onload = function() {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.printer= channel.objects.printer;
    });
};
function printImage(directly){
    html2canvas(document.querySelector("body")).then(canvas => {
        var data_url = canvas.toDataURL();
        //console.log(data_url)
        printer.printImage(data_url, directly || 0);
    });
}
function printPreviewImage(){
    html2canvas(document.querySelector("body")).then(canvas => {
        var data_url = canvas.toDataURL();
        //console.log(data_url)
        printer.printPreviewImage(data_url);
    });
}
function changeBrowserTheme(style){
    alert('Change=>' + style)
}
</script>
<style type="text/css">
::-webkit-scrollbar {width:12px;height:12px;}
::-webkit-scrollbar-track-piece {background-color:#f6f6f6; border-radius: 6px;margin-top:6px;margin-bottom: 6px;}
::-webkit-scrollbar-thumb {background:#999;border-radius: 6px;}
</style>
<style type="text/css" media="print">
img{border:1px solid #000;}
</style>

</head>
<body>
<h1>testing page</h1>
<div>User Agent: <font color="red"><?php echo $_SERVER['HTTP_USER_AGENT']?></font></div>
<div><a href="2.php">2.php self</a></div>
<div><a href="1.php">1.php self</a></div>

<div><a href="1.php" target="_blank">1.php new</a></div>
<div><a href="2.php" target="_blank">2.php new</a></div>
<div><a href="3.php">3.php download</a></div>
<div><a href="4.pdf" target="_blank">open 4.pdf</a></div>
<div><a href="1.chm">download 1.chm</a></div>
<div><a href="javascript:printer.printPreviewHTML('hello world')">printPreviewHTML</a></div>
<div><a href="javascript:printer.printHTML('hello world', 0)">printHTML dialog</a></div>
<div><a href="javascript:printer.printHTML('hello world', 1)">printHTML</a></div>
<div><a href="javascript:printer.printPreviewPage()">printPreviewPage</a></div>
<div><a href="javascript:window.print()">print</a></div>
<div><a href="javascript:printer.savePageToPDF()">save as pdf</a></div>
<div><a href="javascript:printer.printToPDF(document.body.innerHTML)">print to pdf</a></div>
<div><a href="javascript:printPreviewImage()">printPreviewImage</a></div>
<div><a href="javascript:printImage()">printImage dialog</a></div>
<div><a href="javascript:printImage(1)">printImage</a></div>
<div><a href="javascript:printer.changeTheme('light')">theme light</a></div>
<div><a href="javascript:printer.changeTheme('blue')">theme blue</a></div>
<div><a href="javascript:window.close()">Close</a></div>
<div><a href="javascript:printer.exitApplication()">Exit</a></div>
<div><a href="javascript:confirm('您确认要执行此操作吗？')">confirm</a></div>
<div><a href="javascript:console.log(prompt('请输入一个数字或者字母：'))">prompt</a></div>
<form action="2.php" method="post" enctype="multipart/form-data">
<input type="file" name="file" /><br />
<input type="text" name="username" /><br />
<input type="submit" value="Submit" onclick="form.submit()" />
</form>
<img src="https://www.wehire.net/themes/mobile-common/share-business.png" /><br />
<img src="https://www.wehire.net/themes/mobile-common/share-personal.png" /><br />
<div><a href="javascript:printer.startLoading()">startLoading</a></div>
<div><a href="javascript:printer.stopLoading()">stopLoading</a></div>


</body>
</html>