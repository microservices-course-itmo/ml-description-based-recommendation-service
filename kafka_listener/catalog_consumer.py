import logging
import traceback

from kafka import KafkaConsumer
import os

from kafka_listener.schema import new_wine_saved_message_sent_event_pb2 as new_wine
from data.db import add_new_wine


TOPIC_CATALOG = "eventTopic"
BOOTSTRAP_SERVER = [os.environ.get("S_CATALOG_KAFKA_HOST")]
AUTO_OFFSET_RESET = "earliest"
GROUP_ID = "wine.catalog-service"


def get_message_new_wine():
    consumer_new_wine = KafkaConsumer(
        TOPIC_CATALOG,
        bootstrap_servers=BOOTSTRAP_SERVER,
        auto_offset_reset=AUTO_OFFSET_RESET,
        group_id=GROUP_ID,
    )

    logging.info("New wines")
    for message in consumer_new_wine:
        message = message.value
        result = new_wine.NewWineSavedMessageSentEvent()
        result.ParseFromString(message)

        try:
            add_new_wine(result.wineId)
        except Exception:
            logging.error(traceback.format_exc())
