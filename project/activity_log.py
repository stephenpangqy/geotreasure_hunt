import json
import os
import amqp_setup

# i classified different microservices' activity by the microservice name
# so i used topic exchange not fanout
monitorBindingKey='*.activity'

# ------ Start consuming messages ------ #
def consume():
    amqp_setup.check_setup()
    queue_name = 'Activity_log'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming()

# ------ print the file/microservice to retrieve activity from ------ #
def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an order log by " + __file__)
    processOrderLog(json.loads(body))
    print() # print a new line feed

# ------ print the activity log------ #
def processOrderLog(order): 
    print("Recording an order log:")
    print(order)


if __name__ == "__main__":  
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    consume()