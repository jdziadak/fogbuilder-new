from kafka import KafkaConsumer
import time
import sys

# Kafka consumer. Connects to the proper cluster identified by the IP address and reads the messages from given topic.
# Input arguments:
#   - IP address
#   - port that Kafka listens on for external connections
#   - name of the topic to read from
#
# Example usage:
#   python kafka-consumer.py 192.168.0.100 19092 books

if __name__ == "__main__":
    print("Running consumer")
    records = []
    topic_name = sys.argv[3]

    consumer = KafkaConsumer(topic_name, auto_offset_reset='earliest',
                             bootstrap_servers=[f'{sys.argv[1]}:{sys.argv[2]}'], api_version=(0, 10), consumer_timeout_ms=1000)
    for msg in consumer:
        message_text = msg.value
        records.append(message_text)
    consumer.close()
    time.sleep(5)

    print(records)
