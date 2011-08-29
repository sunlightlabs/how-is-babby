var socket = io.connect('http://ec2-50-17-169-160.compute-1.amazonaws.com:8080');
socket.on('connect', function () {
    socket.on('imgUrl', function (imgUrl) {
        var img = document.getElementById('video_frame');
        img.src = imgUrl;
    });
});

