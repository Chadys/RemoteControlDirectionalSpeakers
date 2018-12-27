import time

from inspect import currentframe, getframeinfo

from pybass import *
from pybassmix import *


def handle_bass_error(line):
    print(f'l {line} | BASS error {get_error_description(BASS_ErrorGetCode())}')
    exit(1)


def get_stream():
    return BASS_StreamCreateFile(False, b'test.mp3', 0, 0, BASS_STREAM_DECODE | BASS_STREAM_PRESCAN)


def print_infos():
    print('============== BASS Information ==============')
    bi = BASS_INFO()
    if not BASS_GetInfo(bi):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print('============== Device Information ==============')

    bd = BASS_DEVICEINFO()
    device = 1
    while BASS_GetDeviceInfo(device, bd):
        print(f'Device {device}')
        print(f'description = {bd.name}')
        print(f'driver = {bd.driver}')
        print(f'flags = {bd.flags}')
        device += 1
    print(f'device selected = {BASS_GetDevice()}')


def init_channels(mixer, handles):
    sides = [BASS_SPEAKER_LEFT, BASS_SPEAKER_RIGHT]
    for i in range(2):
        for j in range(2):
            if not BASS_Mixer_StreamAddChannel(mixer, handles[i * 2 + j], BASS_SPEAKER_N(i + 1) | sides[j]):
                handle_bass_error(getframeinfo(currentframe()).lineno)
    #
    # if not BASS_Mixer_StreamAddChannel(mixer, handle, BASS_MIXER_MATRIX):
    #     handle_bass_error(getframeinfo(currentframe()).lineno)
    # matrix = (ctypes.c_float*8)(1.0,0.0, 0.0,0.0, 0.0,0.0, 0.0,1.0)
    # if not BASS_Mixer_ChannelSetMatrix(handle, ctypes.cast(matrix, ctypes.POINTER(ctypes.c_float))):
    #     handle_bass_error(getframeinfo(currentframe()).lineno)


def play(mixer, handles):
    drift_correction = 35000
    if not BASS_ChannelSetPosition(handles[2], drift_correction, BASS_POS_BYTE) or \
            not BASS_ChannelSetPosition(handles[3], drift_correction, BASS_POS_BYTE):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    BASS_ChannelPlay(mixer, False)


def create_mixer(handles):
    bc = BASS_CHANNELINFO()
    if not BASS_ChannelGetInfo(handles[0], bc):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    mixer = BASS_Mixer_StreamCreate(bc.freq, 4, 0)
    if not mixer:
        handle_bass_error(getframeinfo(currentframe()).lineno)
    return mixer

def main():
    if not BASS_Init(-1, 44100, BASS_DEVICE_SPEAKERS | BASS_DEVICE_MONO, 0, 0):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print_infos()

    handles = [get_stream(), get_stream(), get_stream(), get_stream()]
    if not all(handles):
        handle_bass_error(getframeinfo(currentframe()).lineno)

    mixer = create_mixer(handles)
    init_channels(mixer, handles)
    play(mixer, handles)

    channel_length = BASS_ChannelGetLength(handles[0], BASS_POS_BYTE)
    print(f'Music lenght : {BASS_ChannelBytes2Seconds(handles[0], channel_length)} sec')

    while BASS_ChannelIsActive(mixer) == BASS_ACTIVE_PLAYING:
        channel_position = BASS_ChannelGetPosition(handles[0], BASS_POS_BYTE)
        print(int(BASS_ChannelBytes2Seconds(handles[0], channel_position)))
        # if not BASS_ChannelSetAttribute(handles[0], BASS_ATTRIB_VOL, 0.1):
        #     handle_bass_error(getframeinfo(currentframe()).lineno)
        # if not BASS_ChannelSetAttribute(handles[2], BASS_ATTRIB_FREQ, 10000):
        #     handle_bass_error(getframeinfo(currentframe()).lineno)
        time.sleep(2)
    if not BASS_Free():
        handle_bass_error(getframeinfo(currentframe()).lineno)


if __name__ == "__main__":
    main()
