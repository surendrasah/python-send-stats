import time
import socket
import json
import random
import atexit


def format_measurement_data_json(data):
    data['format'] = 'json'
    return json.dumps(data) + '\n'


class StatsReporter:
    def __init__(
        self,
        socket_type,
        socket_address,
        encoding='utf-8',
        formatter=None
    ):
        self._socket_type = socket_type
        self._socket_address = socket_address
        self._encoding = encoding
        self._formatter = formatter if formatter else lambda d: str(d)
        self.create_socket()
    
    def create_socket(self):
        try:
            sock = socket.socket(*self._socket_type)
            sock.connect(self._socket_address)
            self._sock = sock
            print('Created socket')
        except socket.error as e:
            print(f'Got error while creating socket: {e}')

    def close_socket(self):
        try:
            self._sock.close()
            print('Closed socket')
        except (AttributeError, socket.error) as e:
            print(f'Got error while closing socket: {e}')

    def send_data(self, data):
        try:
            sent = self._sock.send(
                self._formatter(data).encode(self._encoding)
            )
            print(f'Sending sample data... {sent}')
        except (AttributeError, socket.error) as e:
            print(f'Got error while sending data on socket: {e}')

            # attempt to recreate socket on error
            self.close_socket()
            self.create_socket()


reporter = StatsReporter(
    (socket.AF_UNIX, ),
    '/tmp/telegraf.sock',
    formatter=format_measurement_data_json
)
atexit.register(reporter.close_socket)


while True:
    reporter.send_data({'value1': 10, 'value2': random.randint(1, 10)})
    time.sleep(1)
