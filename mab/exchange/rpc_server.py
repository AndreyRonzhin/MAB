import json
import pika

from calculation_of_services.models import AccrualService
from exchange import service

import pika
from django.conf import settings
from pika import BlockingConnection, PlainCredentials


class RPC:

    def __init__(self, queue: str):
        self.__connection = None
        self.__channel = None
        self._queue = queue

    def set_connect(self):
        user = settings.RABBITMQ_USER
        password = settings.RABBITMQ_PASSWORD
        host = settings.RABBITMQ_HOST

        credentials = PlainCredentials(user, password)
        try:
            self.__connection = BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))
        except:
            raise ConnectionError('Connection refused')


        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(queue=self._queue)

    @staticmethod
    def on_request(ch, method, props, body):
        json_str = body.decode('utf-8')

        print(json_str)

        response_data = {'id': props.correlation_id,
                         'status': 'ok',
                         'description': '1'}

        response = json.dumps(response_data)
        print(response_data)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.set_connect()
        self.__channel.basic_qos(prefetch_count=1)
        self.__channel.basic_consume(queue='exchange_1c_to_mab', on_message_callback=self.on_request)

        print("Awaiting RPC requests")
        self.__channel.start_consuming()


def start():
    rpc = RPC('exchange_1c_to_mab')
    rpc.start()
