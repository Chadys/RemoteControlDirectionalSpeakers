(function() {
    window.addEventListener("load", function() {
        let ws = new WebSocket("ws://" + window.location.hostname + ":8765/");
        let gn = new GyroNorm();
        let errorNotAvailableMessage = "No gyroscope found, you can't change the direction with this device";
        let garden = document.getElementsByClassName('garden')[0];
        let ball = document.getElementsByClassName("ball")[0];
        let radius = garden.clientWidth / 2;
        let marginToRemove = ball.clientHeight / 2 - 7; //garden + ball border widths
        let circleMiddle = [
            garden.clientTop + radius - ball.clientHeight / 2,
            garden.clientLeft + radius - ball.clientWidth / 2
        ];

        ball.style.top = (circleMiddle[0]) + "px";
        ball.style.left = (circleMiddle[1]) + "px";

        let initArgs = {
            frequency: 50,					// ( How often the object sends the values - milliseconds )
            gravityNormalized: true,			// ( If the gravity related values to be normalized )
            orientationBase: gn.WORLD,		// ( Can be GyroNorm.GAME or GyroNorm.WORLD. gn.GAME returns orientation values with respect to the head direction of the device. gn.WORLD returns the orientation values with respect to the actual north direction of the world. )
            decimalCount: 2,					// ( How many digits after the decimal point will there be in the return values )
            logger: null,					// ( Function to be called to log messages from gyronorm.js )
            screenAdjusted: false			// ( If set to true it will return screen adjusted values. )
        };

        gn.init(initArgs).then(function () {
            gn.start(function (data) {
                // Process:
                document.getElementById("doAlpha").innerText = data.do.alpha;
                document.getElementById("doBeta").innerText = data.do.beta;
                document.getElementById("doGamma").innerText = data.do.gamma;
                document.getElementById("doAbsolute").innerText = data.do.absolute;

                // // La valeur DeviceOrientationEvent.alpha représente le mouvement de l'appareil, autour de l'axe « z », en degrés sur une échelle de 0° à 360° ;
                // // La valeur DeviceOrientationEvent.beta représente le mouvement de l'appareil autour de l'axe « y » en degrés, sur une échelle de -180° à 180°.  Cela représente le mouvement d'avant en arrière de l'appareil ;
                // // La valeur DeviceOrientationEvent.gamma représente le mouvement de l'appareil autour de l'axe « x », exprimée en degrés sur une échelle de -90° à 90°. Cela représente le mouvement de gauche à droite de l'appareil.

                let radAngle = data.do.alpha / 180 * Math.PI;
                ball.style.top = circleMiddle[0] - marginToRemove / 2 + (radius * Math.sin(radAngle)) + "px";
                ball.style.left = circleMiddle[1] - marginToRemove / 2 + (radius * Math.cos(radAngle)) + "px";
                if (ws.readyState = ws.OPEN)
                    ws.send('{"direction":'+data.do.alpha+'}');
            });
        }).catch(function (e) {
            alert(errorNotAvailableMessage);
            // Catch if the DeviceOrientation or DeviceMotion is not supported by the browser or device
        });
    });
})();