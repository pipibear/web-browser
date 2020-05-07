<html>
<head>
</head>
<body>
<h1>testing page</h1>
<div>User Agent: <font color="red"><?php echo $_SERVER['HTTP_USER_AGENT']?></font></div>
<div>File: <?php print_r($_FILES) ?></div>
<div>Post: <?php print_r($_POST) ?></div>
<div><a href="1.php">1.php self</a></div>
<div><a href="2.php">2.php self</a></div>

<div><a href="1.php" target="_blank">1.php new</a></div>
<div><a href="2.php" target="_blank">2.php new</a></div>

<div><a href="2.pdf" target="_blank">open 2.pdf</a></div>
<div><a href="2.chm">download 2.chm</a></div>
<div><a href="javascript:">printview</a></div>
<div><a href="javascript:" onclick="window.print()">print</a></div>
<div><a href="javascript:window.close()">Close</a></div>
<div><a href="javascript:printer.exitApplication()">Exit</a></div>
</body>
</html>