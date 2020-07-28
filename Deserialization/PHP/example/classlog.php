<?php 

class LogFile
{
    // Specify log filename
    
    public $filename = 'error.log';
    
    // Some code
    
    public function LogData($text)
    {
        echo 'Log some data: ' . $text . '<br />';
        file_put_contents($this->filename, $text, FILE_APPEND);
    }
    
    // Destructor that deletes the log file
    
    public function __destruct()
    {
        echo '__destruct deletes "' . $this->filename . '" file. <br />';
        unlink(dirname(__FILE__) . '/' . $this->filename);
    }
}

?>
