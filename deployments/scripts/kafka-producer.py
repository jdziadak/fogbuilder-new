from kafka import KafkaProducer
import sys

# Kafka producer. Connects to the proper cluster identified by the IP address and sends each line of the input file
#   as messages to the given topic.
# Input arguments:
#   - IP address
#   - port that Kafka listens on for external connections
#   - name of the topic to write to
#   - text file to read the messages from
#
# Example usage:
#   python kafka-producer.py 192.168.0.100 19092 books kafka-records

def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        print('B')
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        print('C')
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[f'{sys.argv[1]}:{sys.argv[2]}'], api_version=(0, 10))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer

if __name__ == '__main__':
    with open(f'{sys.argv[4]}', 'r') as input_file:
        records_to_send = input_file.readlines()
        kafka_producer = connect_kafka_producer()
        for recipe in records_to_send:
            print('A')
            publish_message(kafka_producer, sys.argv[3], 'raw', recipe.strip())
        if kafka_producer is not None:
            kafka_producer.close()
