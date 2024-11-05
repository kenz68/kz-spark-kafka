from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092'],
    client_id='kafka_admin_client'
)
topic_list = admin_client.list_topics()


def create_new_topic():
    """Checks if the topic office_input exists or not. If not, creates the topic."""
    try:
        admin_client.create_topics(new_topics=[NewTopic('office_input', 1, 1)])
        return "Topic office_input successfully created"
    except Exception as e:
        return "Topic office_input already exists err: {}".format(e.__class__.__name__)


if __name__ == '__main__':
    print(create_new_topic())
