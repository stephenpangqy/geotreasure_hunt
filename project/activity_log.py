import json
import os
import amqp

monitorBindingKey='#'

# ------ Start consuming messages ------ #
def consume():
    amqp.check_setup()
    queue_name = 'Activity_log'
    amqp.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
     