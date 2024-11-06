import time

from kafka import KafkaConsumer
import datetime
from constant import env

def dt_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def consume_message(bootstrap_server, topic, messages_per_second, group_id):
    """Kafka message consumer script."""
    # Initialize kafka consumer
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_server,
        group_id=group_id,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        request_timeout_ms=60000
    )

    try:
        print(f"[{dt_str()}][{group_id}]: Consuming messages from {topic}")
        for message in consumer:
            print(f"[{dt_str()}][{group_id}]: Received {message.value.decode('utf-8')}")
            time.sleep(1 / messages_per_second)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == '__main__':
    consume_message(env.BOOTSTRAP_SERVER, env.TEST_TOPIC, 2, env.CONSUMER_GROUP)