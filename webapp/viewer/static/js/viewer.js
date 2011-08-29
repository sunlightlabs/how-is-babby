var socket = io.connect('http://localhost:8080');
socket.on('connect', function () {
    socket.on('imgUrl', function (imgUrl) {
        var div = document.getElementById('frames');
        div.innerHTML = '<img src="' + imgUrl + '"/>';
    });
});

