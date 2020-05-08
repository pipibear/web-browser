<?php
function download_content($content, $title, $charset='gbk'){
    if(empty($content)){
        die('Content can not be empty.') ;
    }
    
    ob_end_clean() ;
    header("Content-Disposition: attachment; filename=".$title);
    header("Content-Type: application/octet-stream;");
    //header( "Expires: Mon, 26 Jul 1997 05:00:00 GMT" );
    header( "Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT" );
    //header("Accept-Ranges: bytes");
    header("Content-Transfer-Encoding: binary");
    header( "Cache-Control: post-check=0, pre-check=0", false );
    header("Content-Length: ".strlen($content));

    print($content) ;exit ;
}

download_content('this is testing', 'hello.txt') ;