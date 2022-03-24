<?php

class User
{
    public $age = 0;
    public $name = '';

    public function printData()
    {
        echo 'User ' . $this->name . ' is ' . $this->age . ' years old.<br />';
    }
}

//$usr = new User();

//$usr->age = 20;
//$usr->name = 'HODOR';

$areyouserial = 'O:4:"User":2:{s:3:"age";i:20;s:4:"name";s:5:"HODOR";}';

$usr = unserialize($areyouserial);

$usr->printData();

// echo serialize($usr);

?>
