# RemoteControlDirectionalSpeakers
Multi-modules application to control volume and direction of sound by different means, to be used with several speakers placed in a circle (minimum 4).

All modules communicate with each other using sockets. You need a master service receiving module manifests and sending back all manifests of connected modules. Change TCP_socket_attributes.master_client_attributes values and master_Server_communication.MasterServer content as needed.
- **JoystickApp** : Sends direction from connected joystick.
- **LeapMotionApp** : Sends volume. Volume start at 50%, make clockwise/counter clockwise rotations with your finger to increase/decrease the volume. Needs the Leap Motion SDK. Mac lib files included, for other system you need to replace it.
- **SkeletonKinectApp** : Sends the skeleton info needed by ConvertDirectionMiddlewareApp. Needs the Kinect SDK.
- **VolumeAndGyroWebApp** : Simple web app sending volume and direction. For the direction, the app uses a gyroscope so you needs to launch it on a smartphone.
- **ConvertDirectionMiddlewareApp** : Receives direction comming from JoystickApp or VolumeAndGyroWebApp and simply redirects it, or receives data from SkeletonKinectApp and converts it to direction before sending it back.
- **DirectionalSpeakersApp** : App controlling the volume of each speaker to make the sound go in a choosen direction. Receive global volume from LeapMotionApp or VolumeAndGyroWebApp and direction from ConvertDirectionMiddlewareApp. Should receive PCM music streamed via UDP but the app doing that isn't written yet. Needs libbass and libbassmix (from [un4seen](http://www.un4seen.com/)) and two music files of your choice but with correct name and format : 'test.mp3' and '2.pcm' (raw pcm format, not wav).
