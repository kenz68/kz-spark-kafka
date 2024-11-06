import datetime
import time

from kafka import KafkaAdminClient, KafkaConsumer, TopicPartition

from constant import env


def dt_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_topic_statistics(bootstrap_servers, topic, consumer_group):
    """Fetch detailed statistics about a kafka topic, including consumer group lag."""
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        group_id=consumer_group,
    )

    try:
        # Get topic details
        topic_metadata = admin_client.describe_topics([topic])
        if not topic_metadata:
            print(f"[{dt_str()}] Topic {topic} does not exist")
            return

        # Fetch partitions and offsets
        partitions_info = topic_metadata[0]["partitions"]
        total_messages = 0
        total_lag = 0

        print(f"[{dt_str()}] Topic '{topic}' has {len(partitions_info)} partitions.")

        partition_details = []
        for partition in partitions_info:
            partition_id = partition["partition"]
            tp = TopicPartition(topic, partition_id)
            consumer.assign([tp])

            # Get beginning and end offsets
            beginning_offset = consumer.beginning_offsets([tp])[tp]
            end_offset = consumer.end_offsets([tp])[tp]
            total_messages += end_offset - beginning_offset

            # Get the current committed offset for the consumer group
            committed_offset = consumer.committed(tp)
            if committed_offset is None:
                committed_offset = 0

            # Calculate the lag
            lag = end_offset - committed_offset
            total_lag += lag

            partition_details.append(
                {
                    "partition": partition_id,
                    "beginning_offset": beginning_offset,
                    "end_offset": end_offset,
                    "lag": lag,
                    "committed_offset": committed_offset,
                    "leader": partition["leader"],
                    "replicas": len(partition["replicas"]),
                    "in_sync_replicas": len(partition["isr"]),
                }
            )

            # Print the partition details
            for detail in partition_details:
                print(
                    f"[{dt_str()}]: Partition {detail['partition']} - "
                    f"Leader: {detail['leader']}, "
                    f"Replicas: {detail['replicas']}, "
                    f"In-Sync Replicas: {detail['in_sync_replicas']}, "
                    f"Beginning Offset: {detail['beginning_offset']}, "
                    f"End Offset: {detail['end_offset']}, "
                    f"Committed Offset: {detail['committed_offset']}, "
                    f"Lag: {detail['lag']}"
                )

            # Print the total messages and total lag
            print(f"[{dt_str()}]: Total message in topic: {total_messages}")
            print(f"[{dt_str()}]: Total lag for consumer group {consumer_group}: {total_lag}")

    finally:
        consumer.close()
        admin_client.close()


def monitor_topic(bootstrap_servers, topic, consumer_group, interval):
    """Kafka topic monitoring script."""
    try:
        while True:
            get_topic_statistics(bootstrap_servers, topic, consumer_group)
            print(f"[{dt_str()}]: Sleeping for {interval} seconds before next check...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"[{dt_str()}]: Monitoring stopped...")


if __name__ == "__main__":
    monitor_topic(env.BOOTSTRAP_SERVER, env.TEST_TOPIC, env.CONSUMER_GROUP, 10)
