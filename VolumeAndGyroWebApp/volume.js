(function(){
    window.addEventListener("load", function(){
        let ws = new WebSocket("ws://"+window.location.hostname+":8765/");
        let sliderBar = document.getElementById("sliderBar");

        sliderBar.addEventListener("change", function(event){
            let newVolume = event.srcElement.value;
            if (newVolume < 5) {
                document.getElementById("volumeIcon").classList.remove('fa-volume-down');
                document.getElementById("volumeIcon").classList.remove('fa-volume-up');
                document.getElementById("volumeIcon").classList.add('fa-volume-off');
            } else if (newVolume < 75) {
                document.getElementById("volumeIcon").classList.remove('fa-volume-off');
                document.getElementById("volumeIcon").classList.remove('fa-volume-up');
                document.getElementById("volumeIcon").classList.add('fa-volume-down');
            } else {
                document.getElementById("volumeIcon").classList.remove('fa-volume-down');
                document.getElementById("volumeIcon").classList.remove('fa-volume-off');
                document.getElementById("volumeIcon").classList.add('fa-volume-up');
            }
            if (ws.readyState = ws.OPEN)
                ws.send('{"volume":'+newVolume+'}');
        });
    });
})();
