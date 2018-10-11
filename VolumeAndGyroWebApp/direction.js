var gn = new GyroNorm();
/*var initArgs = {
    frequency:50,					// ( How often the object sends the values - milliseconds )
    gravityNormalized:true,			// ( If the gravity related values to be normalized )
    orientationBase:GyroNorm.GAME,		// ( Can be GyroNorm.GAME or GyroNorm.WORLD. gn.GAME returns orientation values with respect to the head direction of the device. gn.WORLD returns the orientation values with respect to the actual north direction of the world. )
    decimalCount:2,					// ( How many digits after the decimal point will there be in the return values )
    logger:null,					// ( Function to be called to log messages from gyronorm.js )
    screenAdjusted:false			// ( If set to true it will return screen adjusted values. )
};*/

gn.init().then(function(){
    var errorNotAvailableMessage = "No gyroscope found, you can't change the direction with this device";
    if (!gn.isAvailable(GyroNorm.DEVICE_ORIENTATION)){
        alert(errorNotAvailableMessage);
        return;
    }
    gn.start(function(data){
        // Process:


        // La valeur DeviceOrientationEvent.alpha représente le mouvement de l'appareil, autour de l'axe « z », en degrés sur une échelle de 0° à 360° ;
        // La valeur DeviceOrientationEvent.beta représente le mouvement de l'appareil autour de l'axe « y » en degrés, sur une échelle de -180° à 180°.  Cela représente le mouvement d'avant en arrière de l'appareil ;
        // La valeur DeviceOrientationEvent.gamma représente le mouvement de l'appareil autour de l'axe « x », exprimée en degrés sur une échelle de -90° à 90°. Cela représente le mouvement de gauche à droite de l'appareil.

        // data.do.alpha	( deviceorientation event alpha value )
        // data.do.beta		( deviceorientation event beta value )
        // data.do.gamma	( deviceorientation event gamma value )
        // data.do.absolute	( deviceorientation event absolute value )

        // data.dm.x		( devicemotion event acceleration x value )
        // data.dm.y		( devicemotion event acceleration y value )
        // data.dm.z		( devicemotion event acceleration z value )

        // data.dm.gx		( devicemotion event accelerationIncludingGravity x value )
        // data.dm.gy		( devicemotion event accelerationIncludingGravity y value )
        // data.dm.gz		( devicemotion event accelerationIncludingGravity z value )

        // data.dm.alpha	( devicemotion event rotationRate alpha value )
        // data.dm.beta		( devicemotion event rotationRate beta value )
        // data.dm.gamma	( devicemotion event rotationRate gamma value )
    });
}).catch(function(e){
    alert(errorNotAvailableMessage)
    // Catch if the DeviceOrientation or DeviceMotion is not supported by the browser or device
});