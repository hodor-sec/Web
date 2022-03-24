<?php

include 'classlog.php';

// ... Some other code that uses LogFile class ...

// Simple class definition

class User
{
    // Class data
    
    public $age = 0;
    public $name = '';
    
    // Print data
    
    public function PrintData()
    {
        echo 'User ' . $this->name . ' is ' . $this->age . ' years old. <br />';
    }
}

// Unserialize user supplied data

$usr = unserialize($_GET['usr_serialized']);
$usr->PrintData();

?>

