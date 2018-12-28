import time

from inspect import currentframe, getframeinfo

from pybass import *
from pybassmix import *


def get_speakers_count():
    # hack to get real number because on my machine the number of speakers returned from BASS_GetInfo is always 0
    sides = [BASS_SPEAKER_LEFT, BASS_SPEAKER_RIGHT]
    i = 0
    while True:
        for j in range(2):
            h = BASS_StreamCreateFile(False, b'test.mp3', 0, 0,
                                      BASS_SPEAKER_N(i + 1) | sides[j])
            if not h:
                return i*2 + j
            BASS_StreamFree(h)
        i += 1


def handle_bass_error(line):
    print(f'l {line} | BASS error {get_error_description(BASS_ErrorGetCode())}')
    exit(1)


def get_stream():
    return BASS_StreamCreateFile(False, b'test.mp3', 0, 0, BASS_STREAM_DECODE | BASS_STREAM_PRESCAN)


def print_infos():
    print('============== BASS Information ==============')
    bi = BASS_INFO()
    if not BASS_GetInfo(ctypes.byref(bi)):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print('number of speakers available = %d' % bi.speakers)
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


def init_channels(mixer, handles, num_speakers):
    # use only one output of each physical speaker
    for i in range(1, num_speakers+1):
        if not BASS_Mixer_StreamAddChannel(mixer, handles[-1],
                                           BASS_SPEAKER_N(i) | BASS_SPEAKER_LEFT | BASS_STREAM_AUTOFREE):
            handles.pop()
            return
        handles.append(get_stream())


def play(mixer, handles):
    # drift_correction = 35000
    # if not BASS_ChannelSetPosition(handles[1], drift_correction, BASS_POS_BYTE):
    #     handle_bass_error(getframeinfo(currentframe()).lineno)
    BASS_ChannelPlay(mixer, False)


def create_mixer(handle, num_speakers):
    bc = BASS_CHANNELINFO()
    if not BASS_ChannelGetInfo(handle, bc):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    mixer = BASS_Mixer_StreamCreate(bc.freq, num_speakers, 0)
    if not mixer:
        handle_bass_error(getframeinfo(currentframe()).lineno)
    return mixer


def get_speaker_volume(direction, speaker_pos, global_volume=1.0):
    angle = abs(direction - speaker_pos)
    if angle > 180:
        angle = 360 - angle
    angle /= 360  # get value between 0 and 1
    angle = 1 - angle  # invert value
    volume = pow(angle, 5) * (2*angle-0.5)
    volume = 0 if volume < 0 else 1 if volume > 1 else volume
    return volume * global_volume


def init_pos(num_output):
    pos = []
    part = 360 / num_output
    for i in range(num_output):
        pos.append(i*part)
    return pos


def main():
    if not BASS_Init(-1, 44100, BASS_DEVICE_MONO, 0, 0):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print_infos()
    num_speakers = get_speakers_count()
    print(f'Current device has {num_speakers} outputs')

    handles = [get_stream()]
    if not handles[0]:
        handle_bass_error(getframeinfo(currentframe()).lineno)

    mixer = create_mixer(handles[0], num_speakers)
    init_channels(mixer, handles, num_speakers)
    print(f'Using {len(handles)} outputs')
    pos = init_pos(len(handles))
    play(mixer, handles)
    # for handle in handles:
    #     if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_FREQ, 300000):
    #         handle_bass_error(getframeinfo(currentframe()).lineno)

    channel_length = BASS_ChannelGetLength(handles[0], BASS_POS_BYTE)
    print(f'Music length : {BASS_ChannelBytes2Seconds(handles[0], channel_length)} sec')

    while BASS_ChannelIsActive(mixer) == BASS_ACTIVE_PLAYING:
        channel_position = BASS_ChannelGetPosition(handles[0], BASS_POS_BYTE)
        seconds_counter = int(BASS_ChannelBytes2Seconds(handles[0], channel_position))
        print(seconds_counter)
        direction = seconds_counter*5 % 360
        print(f'Direction : {direction}')
        # vol = [0,1,0,0]
        for index, handle in enumerate(handles):
            if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, get_speaker_volume(direction, pos[index], 0.6)):
            # if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, vol[index]):
                handle_bass_error(getframeinfo(currentframe()).lineno)
        time.sleep(2)
    if not BASS_Free():
        handle_bass_error(getframeinfo(currentframe()).lineno)


if __name__ == "__main__":
    main()
