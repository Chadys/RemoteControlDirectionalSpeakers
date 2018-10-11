function updateVolume (newVolume) {
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
}