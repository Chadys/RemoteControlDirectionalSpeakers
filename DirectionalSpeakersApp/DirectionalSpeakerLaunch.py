import time
import asyncio
import json

from inspect import currentframe, getframeinfo
from operator import itemgetter

from pybass import *
from pybassmix import *

import master_server_communication


vars = {'volume': 0.6, 'direction': 0}
master_server = master_server_communication.MasterServer()
server_dict = {}
bass_put_error_value = ctypes.c_uint32(-1).value  # 4294967295, because BASS_StreamPutData return DWORD(-1) in case of error


class ConnexionManager():

    def __init__(self, ip, name, transport, protocol):
        self.ip = ip
        self.name = name
        self.transport = transport
        self.protocol = protocol


class UDPMusicClientProtocol(asyncio.DatagramProtocol):

    def __init__(self, handles, loop):
        self.transport = None
        self.handles = handles
        self.on_con_lost = loop.create_future()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        for handle in self.handles:
            amount = BASS_StreamPutData(handle, data, len(data) | BASS_STREAMPROC_END)
            if amount == bass_put_error_value:
                handle_bass_error(getframeinfo(currentframe()).lineno)
        self.transport.close()

    def error_received(self, exc):
        music_server = server_dict['music']
        master_server.send_failure(music_server.ip, music_server.name, 'error ({})'.format(exc))
        server_dict['music'] = None

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)
        music_server = server_dict['music']
        master_server.send_failure(music_server.ip, music_server.name, 'shutdown')
        server_dict['music'] = None


class TCPClientProtocol(asyncio.Protocol):

    def __init__(self, var_name, loop):
        self.loop = loop
        self.on_con_lost = loop.create_future()
        self.var_name = var_name

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        content = json.loads(data.decode())
        vars[self.var_name] = content.get(self.var_name, 0.6)

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)
        server = server_dict[self.var_name]
        master_server.send_failure(server.ip, server.name, 'error ({})'.format(exc))

    def eof_received(self):
        server = server_dict[self.var_name]
        master_server.send_failure(server.ip, server.name, 'shutdown')
        return False


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
    error_code = BASS_ErrorGetCode()
    print(f'l {line} | BASS error {error_code} : {get_error_description(error_code)}')
    BASS_Free()
    master_server.close_connection()
    exit(1)


def get_stream():
    # return BASS_StreamCreateFile(False, b'test.mp3', 0, 0, BASS_STREAM_DECODE | BASS_STREAM_PRESCAN)
    return BASS_StreamCreate(8000, 1, BASS_STREAM_DECODE, STREAMPROC_PUSH, None)


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


def update_all_speakers_volume(handles, direction, pos, global_volume=1.0):
    # vol = [0,1,0,0]
    for index, handle in enumerate(handles):
        # if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, vol[index]):
        if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL,
                                        get_speaker_volume(direction, pos[index], global_volume)):
            handle_bass_error(getframeinfo(currentframe()).lineno)


def update_all_speakers_volume2(handles, direction, all_pos, global_volume=1.0):
    vol = []
    total = 0
    for speaker_pos in all_pos:
        angle = abs(direction - speaker_pos)
        if angle > 180:
            angle = 360 - angle
        angle = 180 - angle  # invert value
        if angle < 30:
            angle = 0
        vol.append(angle)
        total += angle
        if total == 0:
            total = 360
    vol = [(x/total)*global_volume for x in vol]
    for index, handle in enumerate(handles):
        if not BASS_ChannelSetAttribute(handle, BASS_ATTRIB_VOL, vol[index]):
            handle_bass_error(getframeinfo(currentframe()).lineno)


def init_pos(num_output):
    pos = []
    part = 360 / num_output
    for i in range(num_output):
        pos.append(i*part)
    return pos


async def fill_streams(handles):
    music_server = server_dict['music']
    if music_server is not None:
        await music_server.protocol.on_con_lost
    with open('2.pcm', 'rb') as f:
        data = f.read()
        for handle in handles:
            amount = BASS_StreamPutData(handle, data, len(data) | BASS_STREAMPROC_END)
            if amount == bass_put_error_value:
                handle_bass_error(getframeinfo(currentframe()).lineno)
        await asyncio.sleep(1)


def test_single_channel():
    if not BASS_Init(-1, 44100, BASS_DEVICE_MONO, 0, 0):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    num_speakers = get_speakers_count()
    print(f'Current device has {num_speakers} output(s)')
    h = BASS_StreamCreateFile(False, b'test.mp3', 0, 0, BASS_SPEAKER_N(0) | BASS_SPEAKER_LEFT | BASS_STREAM_AUTOFREE)
    BASS_ChannelPlay(h, False)
    while BASS_ChannelIsActive(h) == BASS_ACTIVE_PLAYING:
        time.sleep(2)
    if not BASS_Free():
        handle_bass_error(getframeinfo(currentframe()).lineno)
    exit(1)


async def connect_to_client(service_type, manifest, available_manifests, handles, loop):
    wanted_services = [dep for dep in manifest['deps'] if service_type in dep['name']]
    wanted_services.sort(key=itemgetter('priority'))
    for wanted_service in wanted_services[::-1]:
        service_name = wanted_service['name']
        for available_manifest in available_manifests:
            for service in available_manifest.get('services', []):
                if service.get('name', None) == service_name:
                    ip = available_manifest.get('ip', None)
                    port = service.get('port', None)
                    type = service.get('type', None)
                    if type == 'TCP':
                        return ConnexionManager(ip, service_name, *await loop.create_connection(
                            lambda: TCPClientProtocol(service_type, loop), ip, port))
                    elif type == 'UDP':
                        return ConnexionManager(ip, service_name, *await loop.create_datagram_endpoint(
                            lambda: UDPMusicClientProtocol(handles, loop), remote_addr=(ip, port)))
    return None


async def update_glob(var_name, step, max_value, reset_value):
    server = server_dict[var_name]
    if server is not None:
        await server.protocol.on_con_lost
    while True:
        vars[var_name] += step
        if vars[var_name] > max_value:
            vars[var_name] = reset_value
        await asyncio.sleep(1)


async def main(loop):
    available_manifests = master_server.get_man()

    manifest = master_server_communication.MasterServer.get_self_man()

    if not BASS_Init(-1, 44100, BASS_DEVICE_MONO, 0, 0):
        handle_bass_error(getframeinfo(currentframe()).lineno)
    print_infos()
    num_speakers = get_speakers_count()
    print(f'Current device has {num_speakers} output(s)')

    handles = [get_stream()]
    if not handles[0]:
        handle_bass_error(getframeinfo(currentframe()).lineno)

    mixer = create_mixer(handles[0], num_speakers)
    init_channels(mixer, handles, num_speakers)

    num_outputs = len(handles)
    print(f'Using {num_outputs} output(s)')
    if num_outputs < num_speakers/2:
        error_code = BASS_ErrorGetCode()
        print(f'BASS error {error_code} : {get_error_description(error_code)}')
    if num_outputs == 0:
        return

    pos = init_pos(num_outputs)

    for service_type in ['volume', 'direction', 'music']:
        server_dict[service_type] = await connect_to_client(service_type, manifest, available_manifests, handles, loop)

    asyncio.ensure_future(update_glob('volume', 0.01, 1, 0.1))
    asyncio.ensure_future(update_glob('direction', 1, 360, 0))
    asyncio.ensure_future(fill_streams(handles))
    await asyncio.sleep(1)

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
        update_all_speakers_volume2(handles, direction, pos, vars['volume'])
        await asyncio.sleep(2)

    if not BASS_Free():
        handle_bass_error(getframeinfo(currentframe()).lineno)
    master_server.close_connection()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    for _, server in server_dict.items():
        if server is not None:
            if server.type == 'TCP':
                server.writer.close()
            elif server.type == 'UDP':
                server.transport.close()
    loop.close()
