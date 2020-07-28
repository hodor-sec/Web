<?php

class TestClass
{
    public $variable = 'HELLO!';

    public function printVariable()
    {
        echo $this->variable . '<br />';
    }

    // Constructor
    public function __construct()
    {
        echo 'Hello from __construct <br />';
    }

    // Destructor
    public function __destruct()
    {
        echo 'Hello from __destruct <br />';
    }

    public function __toString()
    {
        return 'Hello from __toString<br />';
    }
}

$object = new TestClass();

$object->printVariable();

echo $object;

?>
