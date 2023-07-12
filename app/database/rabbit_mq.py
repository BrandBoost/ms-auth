from pika import ConnectionParameters, BlockingConnection
from pika.exceptions import AMQPConnectionError
from app.config.settings import Config, logger  # type: ignore


class RabbitManager:
    parameters: ConnectionParameters = ConnectionParameters(Config.RABBIT_HOST, Config.RABBIT_PORT)
    connection: BlockingConnection = BlockingConnection(parameters)
    channel = connection.channel()

    @classmethod
    async def connect(cls):
        try:
            logger.info("Connected to RabbitMQ")
            if cls.connection is None or cls.connection.is_closed:
                cls.connection = BlockingConnection(cls.parameters)
            return cls
        except AMQPConnectionError as e:
            logger.info(f"Error connecting to RabbitMQ: {str(e)}")
            raise ConnectionError("Failed to connect to RabbitMQ")

    @classmethod
    async def create_channel(cls):
        return cls.connection.channel()

    @classmethod
    async def declare_queue(cls, queue_name):
        cls.channel.queue_declare(queue=queue_name)

    @classmethod
    async def publish_message(cls, queue_name, message):
        cls.channel.basic_publish(exchange='', routing_key=queue_name, body=message)

    @classmethod
    async def consume_messages(cls, queue_name, callback):
        cls.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        cls.channel.start_consuming()

    @classmethod
    async def close(cls):
        if cls.connection and not cls.connection.is_closed:
            cls.connection.close()
