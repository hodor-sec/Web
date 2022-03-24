<?php

class Test
{
    public $variable = 'BUZZ';
    public $variable2 = 'OTHER';
    
    public function PrintVariable()
    {
        echo $this->variable . '<br />';
    }
    
    public function __construct()
    {
        echo '__construct<br />';
    }
    
    public function __destruct()
    {
        echo '__destruct<br />';
    }
    
    public function __wakeup()
    {
        echo '__wakeup<br />';
    }
    
    public function __sleep()
    {
        echo '__sleep<br />';
        
        return array('variable', 'variable2');
    }
}

// Create an object, will call __construct

$obj = new Test();

// Serialize object, will call __sleep

$serialized = serialize($obj);

// Print serialized string

print 'Serialized: ' . $serialized . ' <br />';

// Unserialize string, will call __wakeup

$obj2 = unserialize($serialized);

// Call PintVariable, will print data (BUZZ)

$obj2->PrintVariable();

// PHP script ends, will call __destruct for both objects($obj and $obj2)

?>
