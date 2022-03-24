<?php

include 'classlog.php';

// Create an object

$obj = new LogFile();

// Set filename and log data

$obj->filename = 'somefile.log';
$obj->LogData('Test');

// Destructor will be called and 'somefile.log' will be deleted

?>
