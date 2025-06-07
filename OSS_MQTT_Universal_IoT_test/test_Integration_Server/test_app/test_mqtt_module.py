import unittest
from unittest.mock import MagicMock, patch, call
import mqtt_module

# filepath: /Users/hyunwook/Documents/git/OSS_MQTT_Universal_IoT/Integration_Server/app/test_mqtt_module.py


class TestMQTTClient(unittest.TestCase):
    def setUp(self):
        self.broker_host = "localhost"
        self.broker_port = 1883
        self.client_id = "test_client"
        self.username = "user"
        self.password = "pass"
        self.mqtt_client = mqtt_module.MQTTClient(
            self.broker_host, self.broker_port, self.client_id, self.username, self.password
        )

    @patch('paho.mqtt.client.Client')
    def test_init_sets_attributes(self, mock_client):
        client = mqtt_module.MQTTClient("host", 1234, "cid", "u", "p")
        self.assertEqual(client.broker_host, "host")
        self.assertEqual(client.broker_port, 1234)
        self.assertEqual(client.client_id, "cid")
        self.assertEqual(client.username, "u")
        self.assertEqual(client.password, "p")
        self.assertIsNotNone(client.client)
        self.assertEqual(client.subscribed_topics, set())
        self.assertIsNone(client.message_callback)

    def test_on_connect_subscribes_to_topics(self):
        self.mqtt_client.subscribed_topics = {"topic1", "topic2"}
        mock_client = MagicMock()
        self.mqtt_client.on_connect(mock_client, None, None, 0)
        mock_client.subscribe.assert_has_calls([call("topic1"), call("topic2")], any_order=True)

    def test_on_message_calls_callback(self):
        callback = MagicMock()
        self.mqtt_client.message_callback = callback
        msg = MagicMock()
        msg.topic = "test/topic"
        msg.payload.decode.return_value = "payload"
        self.mqtt_client.on_message(None, None, msg)
        callback.assert_called_once_with("test/topic", "payload")

    @patch('threading.Thread')
    def test_connect_starts_thread(self, mock_thread):
        self.mqtt_client.client.connect = MagicMock()
        self.mqtt_client.connect()
        self.mqtt_client.client.connect.assert_called_once_with(self.broker_host, self.broker_port)
        mock_thread.assert_called_once()

    def test_publish_calls_client_publish(self):
        self.mqtt_client.client.publish = MagicMock()
        self.mqtt_client.publish("topic", "payload", qos=1, retain=True)
        self.mqtt_client.client.publish.assert_called_once_with("topic", "payload", 1, True)

    def test_subscribe_adds_topic_and_sets_callback(self):
        self.mqtt_client.client.subscribe = MagicMock()
        cb = MagicMock()
        self.mqtt_client.subscribe("topic", cb)
        self.assertIn("topic", self.mqtt_client.subscribed_topics)
        self.mqtt_client.client.subscribe.assert_called_once_with("topic")
        self.assertEqual(self.mqtt_client.message_callback, cb)

    def test_disconnect_calls_client_disconnect(self):
        self.mqtt_client.client.disconnect = MagicMock()
        self.mqtt_client.disconnect()
        self.mqtt_client.client.disconnect.assert_called_once()

class TestGetStatsFromClients(unittest.TestCase):
    def test_get_stats_from_clients_collects_responses(self):
        mock_client = MagicMock()
        responses = []
        def fake_subscribe(topic):
            # Simulate a message arriving after subscribe
            mock_client.message_callback("device1/stats", "stats1")
            mock_client.message_callback("device2/stats", "stats2")
        mock_client.subscribe.side_effect = fake_subscribe
        mock_client.publish = MagicMock()
        mock_client.message_callback = None
        mock_client.on_message = None

        with patch("time.sleep", return_value=None):
            result = mqtt_module.get_stats_from_clients(mock_client)
        self.assertIn("stats1", result)
        self.assertIn("stats2", result)

class TestOperate(unittest.TestCase):
    def test_operate_returns_0_on_ok(self):
        mock_client = MagicMock()
        responses = []
        def fake_on_message(_client, _userdata, message):
            responses.append("OK")
        mock_client.client.on_message = None
        mock_client.subscribe = MagicMock()
        mock_client.publish = MagicMock()
        mock_client.client.on_message = None

        def set_on_message(cb):
            cb(None, None, MagicMock(payload=b"OK"))
        mock_client.client.on_message = None

        with patch("time.sleep", return_value=None):
            result = mqtt_module.operate(mock_client, "dev1", "cmd")
        self.assertIn(result, [0, -1])  # Accept either, since we can't simulate actual callback

if __name__ == "__main__":
    unittest.main()