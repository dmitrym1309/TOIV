import paho.mqtt.client as mqtt
import csv
from datetime import datetime
import os

# Параметры подключения к MQTT-брокеру
HOST = "192.168.1.23"  # IP чемодана
PORT = 1883
KEEPALIVE = 60

# Топики и имена полей (оставляем твою схему)
SUB_TOPICS = {
    '/devices/wb-msw-v3_64/controls/Current Motion': 'motion',
    '/devices/wb-msw-v3_64/controls/Temperature': 'temperature',
    '/devices/wb-map12e_35/controls/Ch 3 Q L1': 'voltage vent',
}

# Текущее состояние (последние значения по каждому топику)
SNAPSHOT = {v: '0' for v in SUB_TOPICS.values()}
SNAPSHOT['number'] = HOST.split('.')[-1]
SNAPSHOT['time'] = str(datetime.now())

CSV_PATH = 'data.csv'

WRITE_INTERVAL_SEC = 5.0
_last_write = datetime.min
_first_write_done = False  # как в примере из файла — контролируем первую запись


def _write_csv_row(entry: dict, write_header_if_needed: bool = True):
    """
    Запись в CSV «как в файле»:
    - при первой записи добавляем заголовок,
    - далее дописываем строки.
    Порядок колонок: поля из SUB_TOPICS, затем number и time.
    """
    global _first_write_done

    columns = list(SUB_TOPICS.values()) + ['number', 'time']
    need_header = write_header_if_needed and (not _first_write_done)

    # если файл пустой/не существует — тоже пишем заголовок
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        need_header = True

    mode = 'a'  # дописываем
    with open(CSV_PATH, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if need_header:
            writer.writerow(columns)
            _first_write_done = True
        row = [entry.get(col, '') for col in columns]
        writer.writerow(row)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in SUB_TOPICS.keys():
        client.subscribe(topic)


def on_message(client, userdata, msg):
    global _last_write, SNAPSHOT

    payload = msg.payload.decode()
    topic = msg.topic
    field = SUB_TOPICS.get(topic)
    if field is None:
        return

    SNAPSHOT[field] = payload
    SNAPSHOT['time'] = str(datetime.now())

    now = datetime.now()
    if (now - _last_write).total_seconds() >= WRITE_INTERVAL_SEC:
        _last_write = now
        snapshot_copy = SNAPSHOT.copy()
        _write_csv_row(snapshot_copy)
        print(f'Записано в CSV: {snapshot_copy["time"]}')


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEPALIVE)
    client.loop_forever()


if __name__ == "__main__":
    main()
