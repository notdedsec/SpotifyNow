<?php
#?phpgay
$key = shell_exec("py push.py ".$_GET['code']);
header("Location: http://t.me/notdedsecbot/?start=".$key);
?>
