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
        print(f'flags = {hex(bd.flags)}')
        device += 1
    print(f'device selected = {BASS_GetDevice()}')


def init_channels(mixer, handles):
    sides = [BASS_SPEAKER_LEFT, BASS_SPEAKER_RIGHT]
    i = 0
    while True:
        for j in range(2):
            if not BASS_Mixer_StreamAddChannel(mixer, handles[-1], BASS_SPEAKER_N(i + 1) | sides[j]):
                handles.pop()
                return
            handles.append(get_stream())
        i += 1
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


def create_mixer(handle):
    bc = BASS_CHANNELINFO()
    if not BASS_ChannelGetInfo(handle, bc):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    mixer = BASS_Mixer_StreamCreate(bc.freq, 4, 0)
    if not mixer:
        handle_bass_error(getframeinfo(currentframe()).lineno)
    return mixer


def get_speaker_volume(direction, speaker_pos, global_volume = 1.0):
    angle = abs(direction - speaker_pos)
    if angle > 180:
        angle = 360 - angle
    angle /= 360  # get value between 0 and 1
    angle = 1 - angle  # invert value
    volume = pow(angle, 5)*(2*angle-0.5)
    volume = 0 if volume < 0 else 1 if volume > 1 else volume
    return volume * global_volume


def init_pos(num_output):
    pos = []
    part = 360 / num_output
    for i in range(num_output):
        pos.append(i*part)
    return pos


def main():
    if not BASS_Init(-1, 44100, BASS_DEVICE_SPEAKERS | BASS_DEVICE_MONO, 0, 0):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print_infos()

    handles = [get_stream()]
    if not handles[0]:
        handle_bass_error(getframeinfo(currentframe()).lineno)

    mixer = create_mixer(handles[0])
    init_channels(mixer, handles)
    print(f'Current device has {len(handles)} outputs')
    pos = init_pos(len(handles))
    play(mixer, handles)
    # for handle in handles:
    #     if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_FREQ, 300000):
    #         handle_bass_error(getframeinfo(currentframe()).lineno)

    channel_length = BASS_ChannelGetLength(handles[0], BASS_POS_BYTE)
    print(f'Music lenght : {BASS_ChannelBytes2Seconds(handles[0], channel_length)} sec')

    while BASS_ChannelIsActive(mixer) == BASS_ACTIVE_PLAYING:
        channel_position = BASS_ChannelGetPosition(handles[0], BASS_POS_BYTE)
        seconds_counter = int(BASS_ChannelBytes2Seconds(handles[0], channel_position))
        print(seconds_counter)
        direction = seconds_counter % 360
        for index, handle in enumerate(handles):
            if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, get_speaker_volume(direction, pos[index], 0.6)):
                handle_bass_error(getframeinfo(currentframe()).lineno)
        time.sleep(2)
    if not BASS_Free():
        handle_bass_error(getframeinfo(currentframe()).lineno)


if __name__ == "__main__":
    main()
