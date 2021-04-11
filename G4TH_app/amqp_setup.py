import pika
from os import environ

# ----------  Establish Connection  ---------- #
hostname = environ.get('rabbit_host') or 'localhost'
port = environ.get('rabbit_port') or 5672
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600
    )
)
channel = connection.channel()

#scenarios: ourchasing incentives, planting virtual box, opening box, purchasing membership
#microservices (queues) : error, activity
#microservices (message provider) : order, box, box opening, subscription 

exchangename = "order_topic"
exchangetype = "topic" 
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

# ------------      Error Queue     ------------ #
queue_name = 'Error'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.error')

# ------------      Activity log Queue     ------------ #
queue_name = 'Activity_log'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.activity')

# ------------ Re-establish Connection ------------- #
def check_setup():
    global connection, channel, hostname, port, exchangename, exchangetype
    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype)

# ------------ Testing Connection ------------- #
def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error: ", e)
        print("...creating a new connection.")
        return False