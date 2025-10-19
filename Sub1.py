import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os
import xml.etree.ElementTree as ET

# Параметры подключения к MQTT-брокеру
HOST = "192.168.1.23"  # IP чемодана
PORT = 1883
KEEPALIVE = 60

# Топики и имена полей
SUB_TOPICS = {
    '/devices/wb-msw-v3_64/controls/Current Motion': 'motion',
    '/devices/wb-msw-v3_64/controls/Temperature': 'temperature',
    '/devices/wb-map12e_35/controls/Ch 3 Q L1': 'voltage vent',
}

# Текущее состояние (последние значения по каждому топику)
JSON_DICT = {v: 0 for v in SUB_TOPICS.values()}
JSON_DICT['number'] = HOST.split('.')[-1]
JSON_DICT['time'] = str(datetime.now())

# Пути к файлам
JSON_PATH = 'data.json'
XML_PATH = 'data.xml'

WRITE_INTERVAL_SEC = 5.0
_last_write = datetime.min


def _ensure_files_initialized():
    """Создаёт файлы, если их нет."""
    if not os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    if not os.path.exists(XML_PATH):
        with open(XML_PATH, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<data>\n</data>\n')


def _append_json(entry: dict):
    """Добавляет запись в красивый JSON-список."""
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    data.append(entry)

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _append_xml_item(entry: dict):
    """Добавляет <item> перед закрывающим </data> в XML."""
    item = ET.Element('item')
    for k, v in entry.items():
        tag = k.replace(' ', '_')
        el = ET.SubElement(item, tag)
        el.text = str(v)

    item_str = ET.tostring(item, encoding='unicode')
    closing = '</data>'

    with open(XML_PATH, 'r+', encoding='utf-8') as f:
        content = f.read()
        pos = content.rfind(closing)
        if pos == -1:
            # Если файл повреждён — пересоздаём
            f.seek(0)
            f.truncate(0)
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<data>\n')
            f.write(item_str + '\n</data>\n')
        else:
            f.seek(pos)
            f.write(item_str + '\n' + closing)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    for topic in SUB_TOPICS.keys():
        client.subscribe(topic)


def on_message(client, userdata, msg):
    global _last_write, JSON_DICT

    payload = msg.payload.decode()
    topic = msg.topic
    param_name = SUB_TOPICS[topic]
    JSON_DICT[param_name] = payload
    JSON_DICT['time'] = str(datetime.now())

    now = datetime.now()
    if (now - _last_write).total_seconds() >= WRITE_INTERVAL_SEC:
        _last_write = now
        snapshot = JSON_DICT.copy()

        _append_json(snapshot)
        _append_xml_item(snapshot)

        print(f'Записано в файлы: {snapshot["time"]}')


def main():
    _ensure_files_initialized()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, KEEPALIVE)
    client.loop_forever()


if __name__ == "__main__":
    main()
