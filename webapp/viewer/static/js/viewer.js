var socket = io.connect('http://ec2-50-17-169-160.compute-1.amazonaws.com:8080');
socket.on('connect', function () {
    socket.on('imgUrl', function (imgUrl) {
        var img = document.getElementById('video_frame');
        img.src = imgUrl;
        // Image starts off hidden, to avoid a brief second of a broken image, so unhide it now.
        //img.style.display = '';
    });
});

