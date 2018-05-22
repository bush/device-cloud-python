#!/usr/bin/env python

'''
    Copyright (c) 2016-2017 Wind River Systems, Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software  distributed
    under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
    OR CONDITIONS OF ANY KIND, either express or implied.
'''

import json
import os
import unittest
from binascii import crc32
import mock
from mock import MagicMock
import platform
import re
import socket
import ssl
import sys

# yocto supports websockets, not websocket, so check for that
try:
    import websocket
except ImportError:
    import websockets as websocket

from time import sleep

import device_cloud
import device_cloud.test.test_helpers as helpers

if sys.version_info.major == 2:
    builtin = "__builtin__"
else:
    builtin = "builtins"

class ClientActionDeregister(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up Mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Set up a callback function
        user_data = "user data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)

        # Register action with callback
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

        # Deregister action
        result = self.client.action_deregister("action-name")
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionReregisterNotExist(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Attempt to deregister an action that does not exist
        result = self.client.action_deregister("action-name")
        assert result == device_cloud.STATUS_NOT_FOUND
        assert "action-name" not in self.client.handler.callbacks

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCallback(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Register action with callback
        user_data = "user data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCallbackExists(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Setup callbacks and user data
        user_data = "user data"
        user_data_2 = "user_data"
        callback = helpers.configure_callback_function(self.client, None,
                                                       user_data, 0)
        callback_2 = helpers.configure_callback_function(self.client, None,
                                                         user_data_2, 0)

        # Register action with callback
        result = self.client.action_register_callback("action-name", callback,
                                                      user_data)
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

        # Attempt (and fail) to register same action with a different callback
        result = self.client.action_register_callback("action-name", callback_2,
                                                      user_data_2)
        assert result == device_cloud.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].callback is callback
        assert (self.client.handler.callbacks["action-name"].user_data is
                user_data)

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCommand(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Register action with a command
        command = "do a thing"
        result = self.client.action_register_command("action-name", command)
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientActionRegisterCommandExists(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Set up commands
        command = "do a thing"
        command_2 = "do a different thing"

        # Regsiter action with a command
        result = self.client.action_register_command("action-name", command)
        assert result == device_cloud.STATUS_SUCCESS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

        # Attempt (and fail) to register action with a different command
        result = self.client.action_register_command("action-name", command_2)
        assert result == device_cloud.STATUS_EXISTS
        assert "action-name" in self.client.handler.callbacks
        assert self.client.handler.callbacks["action-name"].command is command

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientAlarmPublish(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue alarm for publishing
        # specify republish=False
        result = self.client.alarm_publish("alarm_key", 4,
                                           message="alarm message",
                                           republish=False)
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishAlarm)
        assert pub.name == "alarm_key"
        assert pub.state == 4
        assert pub.message == "alarm message"
        assert pub.republish == False
        work = self.client.handler.work_queue.get()
        assert work.type == device_cloud._core.constants.WORK_PUBLISH

        # Queue alarm for publishing
        # do not specify republish, use default value
        result = self.client.alarm_publish("alarm_key", 5,
                                           message="alarm message")
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishAlarm)
        assert pub.name == "alarm_key"
        assert pub.state == 5
        assert pub.message == "alarm message"
        assert pub.republish == False
        work = self.client.handler.work_queue.get()
        assert work.type == device_cloud._core.constants.WORK_PUBLISH

        # Queue alarm for publishing
        # default republish=True
        result = self.client.alarm_publish("alarm_key", 6,
                                           message="alarm message",
                                           republish=True)
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishAlarm)
        assert pub.name == "alarm_key"
        assert pub.state == 6
        assert pub.message == "alarm message"
        assert pub.republish == True
        work = self.client.handler.work_queue.get()
        assert work.type == device_cloud._core.constants.WORK_PUBLISH

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientAttributePublish(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue attribute for publishing
        result = self.client.attribute_publish("attribute_key",
                                               "attribute string")
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishAttribute)
        assert pub.name == "attribute_key"
        assert pub.value == "attribute string"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientConnectFailure(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open, mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_mqtt.return_value.on_connect_rc = -1
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Fail to connect
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_FAILURE
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_alive() is False
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()



class ClientConnectSuccess(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self,  mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open, mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect successfully
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is True
        assert self.client.disconnect() == device_cloud.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientDisconnectFailure(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open, mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_mqtt.return_value.on_disconnect_rc = -1
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Receive failure for disconnecting
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_alive() is True
        assert self.client.is_connected() is True
        assert self.client.disconnect() == device_cloud.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_alive() is False
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientEventPublish(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue event (log) for publishing
        result = self.client.event_publish("event message")
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishLog)
        assert pub.message == "event message"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientFileDownloadAsyncSuccess(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.rename")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.getsize")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("requests.get")
    @mock.patch("socket.gethostbyname")
    @mock.patch("os.makedirs")
    def runTest(self, mock_gethostbyname, mock_makedirs, mock_get, mock_mqtt, mock_sleep, mock_getsize, mock_exists,
                mock_isfile, mock_isdir, mock_rename, mock_open, mock_context):
        # Set up mocks
        # make sure the 3rd is false so that the calc_file_checksum
        # returns None and we pass the check
        mock_exists.side_effect = [True, True, True, False ]
        mock_isdir.side_effect = [False, True]
        mock_isfile.side_effect = [True, False]
        mock_makedirs.side_effect = [True]
        mock_rename.side_effect = [True]
        mock_getsize.return_value = 4532
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_client_read = mock_open.return_value.__enter__.return_value.read
        mock_client_read.side_effect = read_strings
        mock_handle_write = mock_open.return_value.__enter__.return_value.write
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_get.return_value.status_code = 200
        file_content = ["This ", "is ", "totally ", "a ", "file.\n",
                        "What ", "are ", "you ", "talking ", "about.\n"]
        mock_gethostbyname.return_value = ["1.1.1.1"]


        file_bytes = []
        for i in range(len(file_content)):
            file_bytes.append(file_content[i].encode())

        mock_get.return_value.iter_content.return_value = file_bytes
        written_arr = []
        mock_handle_write.side_effect = written_arr.append
        download_callback = mock.Mock()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == device_cloud.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request download
        result = self.client.file_download("filename.ext",
                                           "/destination/file.ext",
                                           callback=download_callback)
        assert result == device_cloud.STATUS_SUCCESS
        download_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.get"
        assert jload["1"]["params"]["fileName"] == "filename.ext"

        # Set up and 'receive' reply from Cloud
        # use a None checksum so that the comparison is good
        message = mock.Mock()
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789",
                                                     "fileSize":4532,
                                                     "crc32":None}}}).encode()
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)

        #TODO Make a better check for download completion

        # Check to see what has been downloaded and written to a file
        written = "".join(map(lambda y: y.decode(),
                              filter(lambda x: x is not None,
                                     written_arr)))
        assert written == "This is totally a file.\nWhat are you talking about.\n"
        args = download_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == device_cloud.STATUS_SUCCESS

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientFileUploadAsyncSuccess(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("requests.post")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_post, mock_mqtt, mock_sleep, mock_exists,
                mock_isfile, mock_open, mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True, True]
        mock_isfile.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        file_content = "This is totally a file.\nWhat are you talking about.\n"
        file_bytes = file_content.encode()
        mock_iter = mock_open.return_value.__enter__.return_value.__iter__
        mock_iter.return_value = iter(map(lambda x: x.encode(), file_content))
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        post_kwargs = {}
        def post_func(url, data=None, verify=None, proxies={}):
            post_kwargs["url"] = url
            post_kwargs["data"] = data
            post_kwargs["verify"] = verify
            post_kwargs["proxies"] = proxies
            return mock.Mock(status_code=200)
        mock_post.side_effect = post_func
        upload_callback = mock.Mock()
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == device_cloud.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request upload
        result = self.client.file_upload("/path/to/some/filename.ext",
                                         callback=upload_callback)
        assert result == device_cloud.STATUS_SUCCESS
        checksum = 0
        checksum = crc32(file_bytes, checksum)
        checksum &= 0xffffffff
        upload_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.put"
        assert jload["1"]["params"]["fileName"] == "filename.ext"
        assert jload["1"]["params"]["crc32"] == checksum

        # Set up and 'receive' reply from Cloud
        message = mock.Mock()
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789"}}}).encode()
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)

        #TODO Make a better check for upload completion

        # Check to see what has been uploaded
        assert post_kwargs["url"] == "https://api.notarealcloudhost.com/file/123456789"
        assert post_kwargs["verify"] == "/top/secret/location"
        assert post_kwargs["data"] is mock_open.return_value.__enter__.return_value
        args = upload_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == device_cloud.STATUS_SUCCESS

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientInitFailFindConfig(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [False]

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except IOError:
            excepted = True

        # Check that the 'file' failed to be found
        assert excepted is True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientInitFailReadConfig(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = [IOError]

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except IOError:
            excepted = True

        # Check that the 'file' failed to be read correctly
        assert excepted is True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientInitFailReadDevId(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effects = [True, True]
        read_strings = [json.dumps(self.config_args), IOError]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except IOError:
            excepted = True

        # Check that the 'file' failed to be read correctly
        assert excepted is True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientInitFailWriteDevId(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, False]
        read_strings = [json.dumps(self.config_args), json.dumps(self.config_args)]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_write = mock_open.return_value.__enter__.return_value.write
        mock_read.side_effect = read_strings
        mock_write.side_effect = [IOError]

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        excepted = False
        try:
            self.client.initialize()
        except IOError:
            excepted = True

        # Check that the 'file' failed to be written correctly
        mock_write.assert_called()
        assert excepted is True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientInitMissingAppId(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except KeyError:
            excepted = True

        # Check that the app_id was not acceptable
        assert excepted is True
        assert "key" not in self.client.config

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientInitOverlengthAppId(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("this-app-id-is-surely-way-too-long-to-be-used-in-a-64-byte-key")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except KeyError:
            excepted = True

        # Check that the key was too long
        assert excepted is True
        assert len(self.client.config.key) > 64

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientLocationPublish(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue location for publishing
        result = self.client.location_publish(12.34, 56.78, heading=90.12,
                                              altitude=34.56, speed=78.90,
                                              accuracy=12.34, fix_type="gps")
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishLocation)
        assert pub.latitude == 12.34
        assert pub.longitude == 56.78
        assert pub.heading == 90.12
        assert pub.altitude == 34.56
        assert pub.speed == 78.90
        assert pub.accuracy == 12.34
        assert pub.fix_type == "gps"

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientTelemetryPublish(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Queue telemetry for publishing
        result = self.client.telemetry_publish("property_key", 26.6)
        assert result == device_cloud.STATUS_SUCCESS
        pub = self.client.handler.publish_queue.get()
        assert isinstance(pub, device_cloud._core.defs.PublishTelemetry)
        assert pub.name == "property_key"
        assert pub.value == 26.6

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ConfigMissingHost(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except KeyError:
            excepted = True

        # Check that the config was parsed with errors
        assert excepted is True
        assert "host" not in self.client.config.cloud
        assert "port" in self.client.config.cloud
        assert "token" in self.client.config.cloud

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()
        del self.config_args["cloud"]["host"]

class ConfigMissingPort(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except KeyError:
            excepted = True

        # Check that the config was parsed with errors
        assert excepted is True
        assert "host" in self.client.config.cloud
        assert "port" not in self.client.config.cloud
        assert "token" in self.client.config.cloud

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()
        del self.config_args["cloud"]["port"]

class ConfigMissingToken(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        excepted = False
        try:
            self.client.initialize()
        except KeyError:
            excepted = True

        # Check that the config was parsed with errors
        assert excepted is True
        assert "host" in self.client.config.cloud
        assert "port" in self.client.config.cloud
        assert "token" not in self.client.config.cloud

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()
        del self.config_args["cloud"]["token"]

class ConfigReadFile(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        self.client.initialize()

        # Check that the 'file' was read and parsed correctly
        mock_open.assert_any_call("some/other/directory/device_id", "r")
        mock_open.assert_any_call("some/other/directory/someotherfile.cfg", "r")
        assert mock_read.call_count == 2
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.cloud.port == 8883
        assert self.client.config.cloud.token == "abcdefghijklm"
        assert self.client.config.ca_bundle_file == "/top/secret/location"
        assert self.client.config.validate_cloud_cert == True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ConfigReadDefaults(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_isfile, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, False, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_write = mock_open.return_value.__enter__.return_value.write

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # Check that all defaults are being used
        mock_open.assert_any_call("./testing-client-connect.cfg", "r")
        mock_open.assert_any_call("./device_id", "w")
        mock_read.assert_called()
        mock_write.assert_called()
        assert self.client.config.ca_bundle_file.endswith("cacert.pem")
        assert self.client.config.cloud.host == "api.notarealcloudhost.com"
        assert self.client.config.cloud.port == 8883
        assert self.client.config.cloud.token == "abcdefghijklm"
        assert self.client.config.config_dir == "."
        assert self.client.config.config_file == "testing-client-connect.cfg"
        assert self.client.config.keep_alive == 0
        assert self.client.config.loop_time == 1
        assert self.client.config.thread_count == 3

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = {"cloud":{"host":"api.notarealcloudhost.com",
                           "port":8883, "token":"abcdefghijklm"}}

class ConfigWriteReadDeviceID(unittest.TestCase):
    @mock.patch("device_cloud._core.client.open")
    @mock.patch("device_cloud._core.client.os.path.exists")
    def runTest(self, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, False, True]
        read_strings = [json.dumps(self.config_args)]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_write = mock_open.return_value.__enter__.return_value.write
        mock_read.side_effect = read_strings

        # Initialize client
        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        # device_id is generated and written when the device_id file is not
        # found
        device_id = self.client.config.device_id
        mock_write.assert_called_once_with(device_id)
        #mock_read.assert_called_once()
        mock_open.reset_mock()
        mock_read.reset_mock()
        mock_write.reset_mock()
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), device_id]
        mock_read.side_effect = read_strings

        # device_id is read and used when it exists
        self.client_2 = device_cloud.Client("testing-client-2")
        self.client_2.initialize()
        assert mock_read.call_count == 2
        assert mock_write.call_count == 0
        mock_write.asser_not_called()
        assert self.client_2.config.device_id == device_id

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class HandleActionExecCallbackSuccess(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("device_cloud._core.defs.inspect")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_mqtt, mock_inspect, mock_sleep, mock_exists,
                mock_isfile, mock_open, mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_inspect.getargspec.return_value.args.__len__.return_value = 3
        mock_inspect.ismethod.return_value = False
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # disable the idle loop
        self.client.idle_sleep = 0.1

        # Set up action callback
        mqtt = self.client.handler.mqtt
        params = {"some_param":521, "some_other_param":6234}
        user_data = "User Data"
        callback = mock.Mock(return_value=(0, "I did it!"))
        action = device_cloud._core.defs.Action("some_action", callback, self.client, user_data)
        self.client.handler.callbacks.add_action(action)

        # Connect to Cloud
        assert self.client.connect(timeout=5) == device_cloud.STATUS_SUCCESS

        thing_key = mock_mqtt.call_args_list[0][0][0]
        assert thing_key == "{}-testing-client".format(helpers.uuid)

        # Set up and 'receive' a notification from Cloud
        notify_payload = {"sessionId":"thisdoesntreallyneedtobehere",
                          "thingKey":thing_key}
        message_1 = mock.Mock()
        message_1.payload = json.dumps(notify_payload).encode()
        message_1.topic = "notify/mailbox_activity"
        mqtt.messages.put(message_1)
        sleep(1)
        #TODO Make a better check for action handling

        # Published mailbox check
        mqtt.publish.assert_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "mailbox.check"
        callback.assert_not_called()

        # Set up and 'receive' reply from Cloud
        exec_payload = {"1":{"success":True,
                             "params":{"messages":[{"command":"method.exec",
                                                    "id":"impretendingtobeamailid",
                                                    "params":{"method":"some_action",
                                                              "thingDefKey":"testingthingdef",
                                                              "params":params},
                                                    "thingKey":thing_key}]}}}
        message_2 = mock.Mock()
        message_2.payload = json.dumps(exec_payload).encode()
        message_2.topic = "reply/0001"
        mqtt.messages.put(message_2)
        sleep(1)
        #TODO Make a better check for action handling

        # Called callback
        callback.assert_called()
        args = callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == params
        assert args[2] is user_data

        # Published result of callback
        assert mqtt.publish.call_count == 2
        args = mqtt.publish.call_args_list[1][0]
        assert args[0] == "api/0002"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "mailbox.ack"
        assert jload["1"]["params"]["errorCode"] == 0
        assert jload["1"]["params"]["errorMessage"] == "I did it!"
        assert jload["1"]["params"]["id"] == "impretendingtobeamailid"
        assert len(self.client.handler.reply_tracker) == 1

        # Set up and 'receive' reply from Cloud
        ack_payload = {"1":{"success":True}}
        message_3 = mock.Mock()
        message_3.payload = json.dumps(ack_payload).encode()
        message_3.topic = "reply/0002"
        mqtt.messages.put(message_3)
        sleep(1)
        #TODO Make a better check for action handling
        assert len(self.client.handler.reply_tracker) == 0

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

#class HandlePublishAllTypes(unittest.TestCase):
    #@mock.patch("ssl.SSLContext")
    #@mock.patch(builtin + ".open")
    #@mock.patch("os.path.isfile")
    #@mock.patch("os.path.exists")
    #@mock.patch("time.sleep")
    #@mock.patch("paho.mqtt.client.Client")
    #@mock.patch("socket.gethostbyname")
    #def runTest(self, mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                #mock_open, mock_context):
        ## Set up mocks
        #mock_exists.side_effect = [True, True, True]
        #mock_isfile.side_effect = [True]
        #read_strings = [json.dumps(self.config_args), helpers.uuid]
        #mock_read = mock_open.return_value.__enter__.return_value.read
        #mock_read.side_effect = read_strings
        #mock_mqtt.return_value = helpers.init_mock_mqtt()
        #mock_gethostbyname.return_value = ["1.1.1.1"]

        ## Initialize client
        #kwargs = {"loop_time":1, "thread_count":1}
        #self.client = device_cloud.Client("testing-client", kwargs)
        #self.client.initialize()

        ## Set up pending publishes
        #alarm = device_cloud._core.defs.PublishAlarm("alarm_key", 6,
                                            #message="I'm an alarm")
        #attr = device_cloud._core.defs.PublishAttribute("attribute_key",
                                               #"Attribute String")
        #loc = device_cloud._core.defs.PublishLocation(11.11, 22.22, heading=33.33,
                                             #altitude=44.44, speed=55.55,
                                             #accuracy=66.66, fix_type="gps")
        #event = device_cloud._core.defs.PublishLog("Event Message")
        #telem = device_cloud._core.defs.PublishTelemetry("property_key", 12.34)
        #publishes = [alarm, attr, loc, event, telem]
        #for pub in publishes:
            #self.client.handler.queue_publish(pub)

        ## Connect to Cloud
        #assert self.client.connect(timeout=5) == device_cloud.STATUS_SUCCESS
        #sleep(5)
        ##TODO Make a better check for publish handling
        #thing_key = mock_mqtt.call_args_list[0][0][0]
        #assert thing_key == "{}-testing-client".format(helpers.uuid)
        #mqtt = self.client.handler.mqtt

        ## Published all in queue
        #mqtt.publish.assert_called()
        #args = mqtt.publish.call_args_list[0][0]
        #print args
        #assert args[0] == "api/0001"
        #jload = json.loads(args[5])
        #assert len(jload) == 1
        #assert len(self.client.handler.reply_tracker) == 5
        #assert jload["1"]["command"] == "log.publish"
        #assert jload["1"]["params"]["thingKey"] == thing_key
        #assert jload["1"]["params"]["msg"] == "Event Message"

        #assert jload["2"]["command"] == "alarm.publish"
        #assert jload["2"]["params"]["thingKey"] == thing_key
        #assert jload["2"]["params"]["state"] == 6
        #assert jload["2"]["params"]["msg"] == "I'm an alarm"

        #assert jload["2"]["command"] == "attribute.publish"
        #assert jload["2"]["params"]["thingKey"] == thing_key
        #assert jload["2"]["params"]["key"] == "attribute_key"
        #assert jload["2"]["params"]["value"] == "Attribute String"
        #assert jload["3"]["command"] == "location.publish"
        #assert jload["3"]["params"]["thingKey"] == thing_key
        #assert jload["3"]["params"]["lat"] == 11.11
        #assert jload["3"]["params"]["lng"] == 22.22
        #assert jload["3"]["params"]["heading"] == 33.33
        #assert jload["3"]["params"]["altitude"] == 44.44
        #assert jload["3"]["params"]["speed"] == 55.55
        #assert jload["3"]["params"]["fixAcc"] == 66.66
        #assert jload["3"]["params"]["fixType"] == "gps"
        #assert jload["5"]["command"] == "property.publish"
        #assert jload["5"]["params"]["thingKey"] == thing_key
        #assert jload["5"]["params"]["key"] == "property_key"
        #assert jload["5"]["params"]["value"] == 12.34

        ## Set up and 'receive' reply from Cloud
        #ack_payload = {"1":{"success":True},
                       #"2":{"success":True},
                       #"3":{"success":True},
                       #"4":{"success":True},
                       #"5":{"success":True}}
        #message = mock.Mock()
        #message.payload = json.dumps(ack_payload).encode()
        #message.topic = "reply/0001"
        #mqtt.messages.put(message)
        #sleep(1)
        ##TODO Make a better check for publish handling
        #assert len(self.client.handler.reply_tracker) == 0

    #def setUp(self):
        ## Configuration to be 'read' from config file
        #self.config_args = helpers.config_file_default()

    #def tearDown(self):
        ## Ensure threads have stopped
        #self.client.handler.to_quit = True
        #if self.client.handler.main_thread:
            #self.client.handler.main_thread.join()

class HandlerInitMissingKey(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Initialize handler directly to pass invalid config
        config = device_cloud._core.defs.Config()
        config.update(self.config_args)
        totally_a_client = "No, really."
        excepted = False
        try:
            handler = device_cloud._core.handler.Handler(config, totally_a_client)
        except KeyError:
            excepted = True

        # Check that the key is missing
        assert excepted is True

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()


class HandlerInitWebsockets(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client (with a different configuration file)
        self.client = device_cloud.Client("testing-client")
        self.client.config.config_dir = "some/other/directory"
        self.client.config.config_file = "someotherfile.cfg"
        self.client.initialize()
        mqtt = self.client.handler.mqtt

        # Check that websockets was set
        mock_mqtt.called_with("testing-client", transport="websockets")

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()
        self.config_args["cloud"]["port"] = 443

class OTAExecute(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = "echo 'Hello'"
        mock_system.return_value = 0

        self.ota = device_cloud.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == device_cloud.STATUS_SUCCESS

        # Note: ota_handler.py captures stdout to a file, strip that off
        ota_log = ">> ota_install.log 2>&1"
        mock_system.assert_called_once_with(test_cmd + ota_log)

class OTAExecuteBadCommand(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = "eacho 'Hello'"
        mock_system.return_value = 127

        self.ota = device_cloud.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == device_cloud.STATUS_EXECUTION_ERROR

        # Note: ota_handler.py captures stdout to a file, strip that off
        ota_log = ">> ota_install.log 2>&1"
        mock_system.assert_called_once_with(test_cmd + ota_log)

class OTAExecuteNoCommand(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        test_cmd = None
        mock_system.return_value = -1

        self.ota = device_cloud.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd)

        assert result == device_cloud.STATUS_NOT_FOUND
        mock_system.assert_not_called()

class OTAExecuteBadWorkingDir(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        mock_system.return_value = 0
        mock_isdir.return_value = False
        test_cmd = "echo 'Hello'"

        self.ota = device_cloud.ota_handler.OTAHandler();
        result = self.ota._execute(test_cmd, ".....not_a_real_dir.....")

        assert result == device_cloud.STATUS_SUCCESS

        # Note: ota_handler.py captures stdout to a file, strip that off
        ota_log = ">> ota_install.log 2>&1"
        mock_system.assert_called_once_with(test_cmd + ota_log)

class OTAExecuteWorkingDir(unittest.TestCase):
    @mock.patch("os.path.isdir")
    @mock.patch("os.system")
    def runTest(self, mock_system, mock_isdir):
        mock_system.return_value = 0
        mock_isdir.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler();
        result = self.ota._execute("echo 'Hello'", "../")

        full_cmd = mock_system.call_args[0][0]
        pat = re.compile("cd \\.\\.\\/(;|( &)) echo 'Hello'")
        assert pat.match(full_cmd) != None
        assert result == device_cloud.STATUS_SUCCESS
        mock_system.assert_called_once()

class OTAPackageDownload(unittest.TestCase):
    @mock.patch("device_cloud._core.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = device_cloud.STATUS_SUCCESS

        self.client = device_cloud.Client("testing-client")
        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(self.client, "fake.tar.gz", 600)
        assert result == device_cloud.STATUS_SUCCESS

class OTAPackageDownloadNoClient(unittest.TestCase):
    @mock.patch("device_cloud._core.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = device_cloud.STATUS_SUCCESS

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(None, "fake.tar.gz", 600)
        assert result == device_cloud.STATUS_BAD_PARAMETER

class OTAPackageDownloadBadFile(unittest.TestCase):
    @mock.patch("device_cloud._core.client.Client.file_download")
    def runTest(self, mock_download):
        mock_download.return_value = device_cloud.STATUS_FAILURE

        self.client = device_cloud.Client("testing-client")
        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""
        result = self.ota._package_download(self.client, "fake.tar.gz", 600)
        assert result == device_cloud.STATUS_FAILURE

class OTAPackageUnzipOther(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def runTest(self, mock_isfile):
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.rar", "bbbb")
        assert result == device_cloud.STATUS_NOT_SUPPORTED

class OTAPackageUnzipTar(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile.extractall")
    @mock.patch("tarfile.TarFile.close")
    def runTest(self, mock_close, mock_extract, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == device_cloud.STATUS_SUCCESS

class OTAPackageUnzipZip(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("zipfile.ZipFile")
    @mock.patch("zipfile.ZipFile.extractall")
    @mock.patch("zipfile.ZipFile.close")
    def runTest(self, mock_close, mock_extract, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        result = self.ota._package_unzip("aaaa.zip", "bbbb")
        assert result == device_cloud.STATUS_SUCCESS

class OTAPackageUnzipOpenException(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile")
    def runTest(self, mock_tar, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        mock_open.side_effect = IOError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == device_cloud.STATUS_FILE_OPEN_FAILED

        mock_open.side_effect = OSError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == device_cloud.STATUS_FILE_OPEN_FAILED

class OTAPackageUnzipExtractException(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch("tarfile.open")
    @mock.patch("tarfile.TarFile")
    def runTest(self, mock_tar, mock_open, mock_isfile):
        mock_isfile.return_value = True
        mock_open.return_value = mock_tar

        self.ota = device_cloud.ota_handler.OTAHandler()
        self.ota._runtime_dir = ""

        mock_tar.extractall.side_effect = IOError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == device_cloud.STATUS_IO_ERROR

        mock_tar.extractall.side_effect = OSError
        result = self.ota._package_unzip("aaaa.tar.gz", "bbbb")
        assert result == device_cloud.STATUS_IO_ERROR

class OTAReadUpdateJSON(unittest.TestCase):
    @mock.patch("json.load")
    @mock.patch("os.path.isfile")
    @mock.patch(builtin + ".open")
    def runTest(self, mock_open, mock_isfile, mock_json):
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        result = self.ota._read_update_json("fake")
        assert result[0] == device_cloud.STATUS_SUCCESS
        assert result[1] != None

class OTAReadUpdateJSONBadFormat(unittest.TestCase):
    @mock.patch("json.load")
    @mock.patch("os.path.isfile")
    @mock.patch(builtin + ".open")
    def runTest(self, mock_open, mock_isfile, mock_json):
        mock_json.side_effect = ValueError
        mock_isfile.return_value = True

        self.ota = device_cloud.ota_handler.OTAHandler()
        result = self.ota._read_update_json("fake")
        assert result[0] == device_cloud.STATUS_IO_ERROR
        assert result[1] == None

class OTAReadUpdateJSONNonExistant(unittest.TestCase):
    @mock.patch("os.path.isfile")
    def runTest(self, mock_isfile):
        mock_isfile.return_value = False

        self.ota = device_cloud.ota_handler.OTAHandler()
        result = self.ota._read_update_json("")
        assert result[0] == device_cloud.STATUS_BAD_PARAMETER
        assert result[1] == None

class OTAUpdateCallback(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch(builtin + ".open")
    @mock.patch("threading.Thread.start")
    def runTest(self, mock_start, mock_open, mock_isfile):
        mock_isfile.return_value = False

        self.client = device_cloud.Client("testing-client")
        self.ota = device_cloud.ota_handler.OTAHandler()

        result = self.ota.update_callback(self.client, {}, ["aaaa"], None)
        assert result[0] == device_cloud.STATUS_INVOKED

class OTAUpdateCallbackInProgress(unittest.TestCase):
    @mock.patch("os.path.isfile")
    @mock.patch(builtin + ".open")
    @mock.patch("threading.Thread.start")
    def runTest(self, mock_start, mock_open, mock_isfile):
        mock_isfile.return_value = True

        self.client = device_cloud.Client("testing-client")
        self.ota = device_cloud.ota_handler.OTAHandler()

        result = self.ota.update_callback(self.client, {}, ["aaaa"], None)
        assert result[0] == device_cloud.STATUS_FAILURE

class OTAUpdateSoftware(unittest.TestCase):
    """
    Test "suite" that will run success and failure cases on the main
    "_update_software" method.
    """
    @mock.patch("device_cloud.Client")
    def setUp(self, mock_client):
        self.ota = device_cloud.ota_handler.OTAHandler()
        self.client = device_cloud.Client("testing-client")
        self.params = {"package": "fake"}
        self.update_data = {"pre_install": "pre", \
                            "install": "install", \
                            "post_install": "post", \
                            "err_action": "err"}
        self.request = mock.Mock()
        self.request.message_id = 1234

    @mock.patch("os.path.exists")
    @mock.patch(builtin + ".open")
    @mock.patch("os.remove")
    @mock.patch("os.path")
    @mock.patch("device_cloud.ota_handler.OTAHandler._execute")
    @mock.patch("device_cloud.ota_handler.OTAHandler._read_update_json")
    @mock.patch("device_cloud.ota_handler.OTAHandler._package_unzip")
    @mock.patch("device_cloud.ota_handler.OTAHandler._package_download")
    def runTest(self, mock_dl, mock_unzip, mock_read, mock_execute, mock_path, mock_remove, mock_open, mock_exists):
        # Store mocks for tests
        self.mock_dl = mock_dl
        self.mock_unzip = mock_unzip
        self.mock_read = mock_read
        self.mock_execute = mock_execute
        self.mock_path = mock_path
        self.mock_remove = mock_remove
        self.mock_write = mock_open.return_value.__enter__.return_value.write
        self.mock_exists = mock_exists

        # Run Tests
        self.successCase()
        self.downloadFailCase()
        self.unzipFailCase()
        self.dataReadFailCase()
        self.preInstallFailCase()
        self.installFailCase()
        self.postInstallFailCase()
        self.preInstallNoneCase()
        self.postInstallNoneCase()

    def resetMocks(self):
        self.mock_dl.reset_mock()
        self.mock_unzip.reset_mock()
        self.mock_read.reset_mock()
        self.mock_execute.reset_mock()
        self.mock_path.reset_mock()
        self.mock_remove.reset_mock()
        self.client.reset_mock()

        self.mock_execute.side_effect = None
        self.update_data = {"pre_install": "pre", \
                            "install": "install", \
                            "post_install": "post", \
                            "error_action": "err"}

        self.mock_path.isdir.return_value = False
        self.mock_path.isfile.return_value = False
        self.mock_dl.return_value = device_cloud.STATUS_SUCCESS
        self.mock_unzip.return_value = device_cloud.STATUS_SUCCESS
        self.mock_read.return_value = (device_cloud.STATUS_SUCCESS, self.update_data)
        self.mock_execute.return_value = device_cloud.STATUS_SUCCESS

    def successCase(self):
        self.resetMocks()

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") in self.client.log.call_args_list

    def downloadFailCase(self):
        self.resetMocks()
        self.mock_dl.return_value = device_cloud.STATUS_FAILURE

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_not_called()
        self.mock_read.assert_not_called()
        assert self.mock_execute.call_count == 0
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Download Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def unzipFailCase(self):
        self.resetMocks()
        self.mock_unzip.return_value = device_cloud.STATUS_IO_ERROR

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_not_called()
        assert self.mock_execute.call_count == 0
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Unzip Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def dataReadFailCase(self):
        self.resetMocks()
        self.mock_read.return_value = (device_cloud.STATUS_FAILURE, "")

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 0
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Data Read Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def preInstallFailCase(self):
        self.resetMocks()
        self.mock_execute.return_value = None
        self.mock_execute.side_effect = [device_cloud.STATUS_EXECUTION_ERROR, device_cloud.STATUS_SUCCESS, device_cloud.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 2
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Pre-Install Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def installFailCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [device_cloud.STATUS_SUCCESS, device_cloud.STATUS_EXECUTION_ERROR, device_cloud.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 3
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Install Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def postInstallFailCase(self):
        self.resetMocks()
        self.mock_execute.side_effect = [device_cloud.STATUS_SUCCESS, device_cloud.STATUS_SUCCESS, device_cloud.STATUS_EXECUTION_ERROR, device_cloud.STATUS_SUCCESS]

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 4
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Post-Install Failed!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") in self.client.log.call_args_list

    def preInstallNoneCase(self):
        self.resetMocks()
        self.update_data["pre_install"] = ""

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 2
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Pre-Install Failed!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list

    def postInstallNoneCase(self):
        self.resetMocks()
        self.update_data["post_install"] = ""

        self.ota._update_software(self.client, self.params, self.request)

        self.mock_dl.assert_called_once()
        self.mock_unzip.assert_called_once()
        self.mock_read.assert_called_once()
        assert self.mock_execute.call_count == 2
        assert mock.call(device_cloud.LOGINFO, "OTA Successful!") in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "Post-Install Failed!") not in self.client.log.call_args_list
        assert mock.call(device_cloud.LOGERROR, "OTA Failed!") not in self.client.log.call_args_list


class ActionAcknowledge(unittest.TestCase):
    @mock.patch("device_cloud._core.tr50.create_mailbox_ack")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open, mock_ack):
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        self.client.handler.send = mock.Mock()
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS

        result = self.client.action_acknowledge("message_id", 0, "")
        assert result == device_cloud.STATUS_SUCCESS
        self.client.handler.send.assert_called_once()
        mock_ack.assert_called_once()

    def setUp(self):
        self.config_args = helpers.config_file_default()

class ActionProgressUpdate(unittest.TestCase):
    @mock.patch("device_cloud._core.tr50.create_mailbox_update")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open, mock_update):
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        self.client.handler.send = mock.Mock()
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS

        result = self.client.action_progress_update("message_id", "update msg")
        assert result == device_cloud.STATUS_SUCCESS
        self.client.handler.send.assert_called_once()
        mock_update.assert_called_once()

    def setUp(self):
        self.config_args = helpers.config_file_default()

class OSALExecl(unittest.TestCase):
    @mock.patch("os.execvp")
    def runTest(self, mock_exec):
        mock_exec.return_value = 0
        result = device_cloud.osal.execl(["python", "hello.py"])
        assert result == device_cloud.osal.EXECUTION_FAILURE
        mock_exec.assert_called_once()

class OSALSystemShutdown(unittest.TestCase):
    @mock.patch("os.system")
    def runTest(self, mock_system):
        mock_system.return_value = 0
        result = device_cloud.osal.system_shutdown()
        assert result == 0
        mock_system.assert_called_once()

class OSALSystemReboot(unittest.TestCase):
    @mock.patch("os.system")
    def runTest(self, mock_system):
        mock_system.return_value = 0
        result = device_cloud.osal.system_reboot()
        assert result == 0
        mock_system.assert_called_once()

class OSALOSKernel(unittest.TestCase):
    def runTest(self):
        result = device_cloud.osal.os_kernel()
        if device_cloud.osal.LINUX:
            assert result == platform.release()
        elif device_cloud.osal.WIN32:
            assert result == platform.version()
        else:
            assert result == "Unknown"

class OSALOSVersion(unittest.TestCase):
    def runTest(self):
        result = device_cloud.osal.os_version()
        if device_cloud.osal.LINUX:
            expect = "{}-{}".format(platform.linux_distribution()[1], platform.linux_distribution()[2])
            assert result == expect
        elif device_cloud.osal.WIN32:
            assert result == platform.release()
        else:
            assert result == "Unknown"

class OSALOSName(unittest.TestCase):
    def runTest(self):
        result = device_cloud.osal.os_name()
        if device_cloud.osal.LINUX:
            rgx = re.compile("^.* \\(.*\\)$")
            assert rgx.match(result) != None
        elif device_cloud.osal.WIN32:
            assert result == platform.system()
        else:
            assert result == "Unknown"

class ActionCommandExecuteBasic(unittest.TestCase):
    @mock.patch("device_cloud._core.defs.Action")
    @mock.patch("subprocess.Popen")
    def runTest(self, mock_popen, mock_action):
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        action = device_cloud._core.defs.ActionCommand("name", "cmd", None)

        request = mock.Mock()
        request.params = None

        result = action.execute(request)
        assert result == (0, "command: ['cmd']  ,  stdout:   ,  stderr: ")
        mock_popen.assert_called_once()

# this test is failing randomly
#class ActionCommandExecuteParams(unittest.TestCase):
    #@mock.patch("device_cloud._core.defs.Action")
    #@mock.patch("subprocess.Popen")
    #def runTest(self, mock_popen, mock_action):
        #mock_proc = mock.Mock()
        #mock_proc.communicate.return_value = ("", "")
        #mock_proc.returncode = 0
        #mock_popen.return_value = mock_proc

        #action = device_cloud._core.defs.ActionCommand("name", "cmd", None)

        #request = mock.Mock()
        #request.params = {"t": True, "f": False, "v":"val"}

        #result = action.execute(request)
	## in py3 the parameter key/value pairs may not be in the
	## exected order.
        #if ('cmd' in result and '--v=val' in result and '--t' in result):
            #assert result == (0, "command: ['cmd', '--v=val', '--t']  ,  stdout:   ,  stderr: ")
        #mock_popen.assert_called_once()

class HandlerHandleActionException(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    def runTest(self, mock_exists, mock_open):
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings

        self.client = device_cloud.Client("testing-client")
        self.client.initialize()

        self.client.handler.callbacks.execute_action = mock.Mock()
        self.client.handler.callbacks.execute_action.side_effect = Exception
        self.client.handler.logger.error = mock.Mock()
        self.client.handler.send = mock.Mock()
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        request = mock.Mock()
        request.name = "req"

        result = self.client.handler.handle_action(request)

        assert result == device_cloud.STATUS_SUCCESS
        self.client.handler.callbacks.execute_action.assert_called_once()
        assert self.client.handler.logger.error.call_count == 2

    def setUp(self):
        self.config_args = helpers.config_file_default()

class RelayInitNoLogger(unittest.TestCase):
    def runTest(self):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345, True, None)
        assert self.relay
        assert self.relay.running == False
        assert self.relay.thread == None
        assert self.relay.log != None

class RelayStartAlreadyRunning(unittest.TestCase):
    def runTest(self):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.assertRaises(RuntimeError, self.relay.start)

#class RelayStartSSLFail(unittest.TestCase):
    #@mock.patch("websocket.WebSocketApp")
    #def runTest(self, mock_connect):
        #mock_connect.side_effect = ssl.SSLError
        #self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        #self.assertRaises(ssl.SSLError, self.relay.start)
        #assert self.relay.running == False
        #assert self.relay.wsock == None

class RelayStartSuccess(unittest.TestCase):
    @mock.patch("threading.Thread.start")
    @mock.patch("websocket.WebSocketApp")
    def runTest(self, mock_WebSocketApp, mock_tstart):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.start()
        assert self.relay.running == True
        assert self.relay.wsock != None
        assert self.relay.ws_thread != None

class RelayStartInsecure(unittest.TestCase):
    @mock.patch("threading.Thread.start")
    @mock.patch("websocket.WebSocketApp")
    def runTest(self, mock_WebSocketApp, mock_tstart):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345, False)
        self.relay.start()
        assert self.relay.running == True
        assert self.relay.wsock != None
        assert self.relay.ws_thread != None

class RelayStop(unittest.TestCase):
    def runTest(self):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        mock_thread = mock.Mock()
        self.relay.thread = mock_thread
        self.relay.wsock = mock.Mock()
        self.relay.track_ws = self.relay.wsock

        self.relay.stop()
        mock_thread.join.assert_called_once()
        assert self.relay.ws_thread == None

class RelayCreateRelay(unittest.TestCase):
    @mock.patch("threading.Thread.join")
    @mock.patch("threading.Thread.start")
    @mock.patch("websocket.WebSocketApp")
    def runTest(self, mock_WebSocketApp, mock_tstart, mock_tjoin):
        device_cloud.relay.create_relay("host1.aaa", "host2.aaa", 12345)
        assert device_cloud.relay.relays[0]

        self.relay = device_cloud.relay.relays[0]
        self.relay.wsock = mock.Mock()
        self.relay.track_ws = self.relay.wsock
        assert self.relay.running == True
        assert self.relay.wsock != None
        assert self.relay.ws_thread != None

        self.relay.stop()
        del device_cloud.relay.relays[0]

class RelayStopRelays(unittest.TestCase):
    @mock.patch("threading.Thread.join")
    @mock.patch("threading.Thread.start")
    @mock.patch("websocket.WebSocketApp")
    def runTest(self, mock_WebSocketApp, mock_tstart, mock_tjoin):
        device_cloud.relay.create_relay("host1.aaa", "host2.aaa", 12345)
        assert device_cloud.relay.relays[0]
        device_cloud.relay.create_relay("host3.aaa", "host4.aaa", 6789)
        assert device_cloud.relay.relays[1]
        device_cloud.relay.stop_relays()
        assert len(device_cloud.relay.relays) == 0

class RelayLoopNotRunning(unittest.TestCase):
    def runTest(self):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = False
        self.relay.wsock = mock.Mock()
        self.relay.lsock.append(mock.Mock())
        self.relay._on_local_message()
        # on message should see the it is not running and delete the
        # socket to an empy array
        assert self.relay.lsock == []

class RelayLoopWSClosed(unittest.TestCase):
    @mock.patch("select.select")
    def runTest(self, mock_select):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.relay.lsock.append(mock.Mock())
        mock_select.return_value = (self.relay.lsock, None, None)
        mock_recv = mock.Mock()
        mock_recv.return_value = None
        self.relay.lsock[0].recv = mock_recv

        self.relay._on_local_message()
        assert mock_recv.call_count == 1
        assert self.relay.wsock == None
        assert self.relay.lsock == []

class RelayLoopNoData(unittest.TestCase):
    @mock.patch("select.select")
    def runTest(self, mock_select):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.relay.wsock = mock.Mock()
        self.relay.lsock.append(mock.Mock())
        mock_select.return_value = (self.relay.lsock, None, None)
        mock_recv = mock.Mock()
        mock_recv.return_value = None
        self.relay.lsock[0].recv = mock_recv

        self.relay._on_local_message()
        assert mock_recv.call_count == 1
        assert self.relay.lsock == []

class RelayLoopWithData(unittest.TestCase):
    @mock.patch("socket.socket")
    @mock.patch("select.select")
    def runTest(self, mock_select, mock_recv):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.relay.wsock = MagicMock()
        self.relay.lsock = MagicMock()
        self.relay.lsocket_map[self.relay.lsock] = 0
        mock_select.return_value = ([self.relay.lsock], None, None)
        mock_recv = MagicMock()
        mock_recv.return_value = "data"
        mock_recv()
        self.relay.wsock.send = MagicMock(side_effect=self.send_side_effect)
        
        self.relay._on_local_message()
        assert mock_recv.call_count == 1
        assert self.relay.lsock == []

    def send_side_effect(self, *args, **kwargs):
        self.relay.running = False

#class RelayLoopNoLocal(unittest.TestCase):
    #@mock.patch("socket.socket")
    #@mock.patch("select.select")
    #def runTest(self, mock_select, mock_socket):
        #self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        #self.relay.running = True
        #self.relay.wsock = mock.Mock()
        #mock_select.return_value = ([self.relay.wsock], None, None)
        #mock_socket.side_effect = self.socket_side_effect
        #mock_recv = mock.Mock()
        #if sys.version_info.major == 2:
            #mock_recv.return_value = (0, device_cloud.relay.CONNECT_MSG)
        #else:
            #mock_recv.return_value = (0, device_cloud.relay.CONNECT_MSG.encode())
        #self.relay.wsock.recv = mock_recv
        #self.relay.wsock.recv()

        #self.relay._on_local_message()
        #assert mock_recv.call_count == 1
        #assert mock_socket.call_count == 1
        #assert self.relay.wsock == None
        #assert self.relay.lsock == None

    #def socket_side_effect(self, *args):
        #s = mock.Mock()
        #s.connect = mock.Mock()
        #self.relay.running = False
        #return s

class RelayLoopNoLocalError(unittest.TestCase):
    @mock.patch("socket.socket")
    @mock.patch("select.select")
    def runTest(self, mock_select, mock_socket):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.relay.wsock = mock.Mock()
        #mock_select.return_value = ([self.relay.wsock], None, None)
        mock_socket.side_effect = socket.error
        mock_recv = mock.Mock()
        if sys.version_info.major == 2:
            mock_recv.return_value = (0, device_cloud.relay.CONNECT_MSG)
        else:
            mock_recv.return_value = (0, device_cloud.relay.CONNECT_MSG.encode())

        self.relay.wsock.recv = mock_recv
        self.relay.wsock.recv()

        self.relay._on_message(self.relay.wsock,  device_cloud.relay.CONNECT_MSG)
        assert mock_recv.call_count == 1
        assert mock_socket.call_count == 1
        #assert self.relay.wsock == None
        assert self.relay.lsock == []

class RelayLoopLocalReadError(unittest.TestCase):
    @mock.patch("socket.socket")
    @mock.patch("select.select")
    def runTest(self, mock_select, mock_socket):
        self.relay = device_cloud.relay.Relay("host1.aaa", "host2.aaa", 12345)
        self.relay.running = True
        self.relay.wsock = mock.Mock(name="w")
        self.relay.lsock.append( mock.Mock(name="l"))
        mock_select.return_value = (self.relay.lsock, None, None)
        mock_recv = mock.Mock()
        mock_recv.return_value = ""
        self.relay.lsock[0].recv = mock_recv

        self.relay._on_local_message()
        assert mock_recv.call_count == 1
        assert mock_socket.call_count == 0
        assert self.relay.lsock == []

class ClientFileDownloadAsyncChecksumFail(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch("os.remove")
    @mock.patch(builtin + ".open")
    @mock.patch("os.rename")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("requests.get")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_get, mock_mqtt, mock_sleep, mock_exists,
                mock_isfile, mock_isdir, mock_rename, mock_open, mock_remove,
                mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True, False]
        mock_isdir.side_effect = [False, True]
        mock_isfile.side_effect = [True, False]
        mock_remove.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_client_read = mock_open.return_value.__enter__.return_value.read
        mock_client_read.side_effect = read_strings
        mock_handle_write = mock_open.return_value.__enter__.return_value.write
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_get.return_value.status_code = 200
        file_content = ["This ", "is ", "totally ", "a ", "file.\n",
                        "What ", "are ", "you ", "talking ", "about.\n"]
        mock_gethostbyname.return_value = ["1.1.1.1"]

        file_bytes = []
        for i in range(len(file_content)):
            file_bytes.append(file_content[i].encode())

        mock_get.return_value.iter_content.return_value = file_bytes
        written_arr = []
        mock_handle_write.side_effect = written_arr.append
        download_callback = mock.Mock()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()
        self.client.idle_sleep = 0.1

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == device_cloud.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request download
        result = self.client.file_download("filename.ext",
                                           "/destination/file.ext",
                                           callback=download_callback)
        assert result == device_cloud.STATUS_SUCCESS
        download_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.get"
        assert jload["1"]["params"]["fileName"] == "filename.ext"

        # Set up and 'receive' "bad" reply from Cloud
        checksum = 12345
        message = mock.Mock()

        # since the API checks the length to see if this is a resume
        # or not before failing due to checksum, setup the fileSize 0
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789",
                                                     "fileSize":0,
                                                     "crc32":checksum}}}).encode()
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)
        #TODO Make a better check for download completion

        # Check to see what has been downloaded and written to a file
        written = "".join(map(lambda y: y.decode(),
                              filter(lambda x: x is not None,
                                     written_arr)))
        # since this is a checksum fail, no sense validating the
        # content of written
        args = download_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == device_cloud.STATUS_FAILURE

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientFileDownloadAsyncRequestFail(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch("os.remove")
    @mock.patch(builtin + ".open")
    @mock.patch("os.rename")
    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("requests.get")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_get, mock_mqtt, mock_sleep, mock_exists,
                mock_isfile, mock_isdir, mock_rename, mock_open, mock_remove,
                mock_context):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isdir.side_effect = [False, True]
        mock_isfile.side_effect = [True, False]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_client_read = mock_open.return_value.__enter__.return_value.read
        mock_client_read.side_effect = read_strings
        mock_handle_write = mock_open.return_value.__enter__.return_value.write
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_get.return_value.status_code = 500
        file_content = ["This ", "is ", "totally ", "a ", "file.\n",
                        "What ", "are ", "you ", "talking ", "about.\n"]
        mock_gethostbyname.return_value = ["1.1.1.1"]

        file_bytes = []
        for i in range(len(file_content)):
            file_bytes.append(file_content[i].encode())

        mock_get.return_value.iter_content.return_value = file_bytes
        written_arr = []
        mock_handle_write.side_effect = written_arr.append
        download_callback = mock.Mock()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":1}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()
        self.client.idle_sleep = 0.1

        # Connect client to Cloud
        mqtt = self.client.handler.mqtt
        result = self.client.connect()
        assert result == device_cloud.STATUS_SUCCESS
        assert self.client.is_connected()

        # Request download
        result = self.client.file_download("filename.ext",
                                           "/destination/file.ext",
                                           callback=download_callback)
        assert result == device_cloud.STATUS_SUCCESS
        download_callback.assert_not_called()
        args = mqtt.publish.call_args_list[0][0]
        assert args[0] == "api/0001"
        jload = json.loads(args[1])
        assert jload["1"]["command"] == "file.get"
        assert jload["1"]["params"]["fileName"] == "filename.ext"

        # Set up and 'receive' "bad" reply from Cloud
        checksum = 0
        message = mock.Mock()
        message.payload = json.dumps({"1":{"success":True,
                                           "params":{"fileId":"123456789",
                                                     "fileSize":4532,
                                                     "crc32":checksum}}}).encode()
        message.topic = "reply/0001"
        mqtt.messages.put(message)
        sleep(1)
        #TODO Make a better check for download completion

        # Check to see what has been downloaded and written to a file
        written = "".join(map(lambda y: y.decode(),
                              filter(lambda x: x is not None,
                                     written_arr)))
        assert written == ""
        args = download_callback.call_args_list[0][0]
        assert args[0] is self.client
        assert args[1] == "filename.ext"
        assert args[2] == device_cloud.STATUS_FAILURE

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

    def tearDown(self):
        # Ensure threads have stopped
        self.client.handler.to_quit = True
        if self.client.handler.main_thread:
            self.client.handler.main_thread.join()

class ClientConnectMissingHost(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        self.client.config.cloud.host = ""

        # Connect successfully
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_BAD_PARAMETER
        mqtt.connect.assert_not_called()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientConnectMissingPort(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_gethostbyname, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()
        mock_gethostbyname.return_value = ["1.1.1.1"]

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        self.client.config.cloud.port = None

        # Connect successfully
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_BAD_PARAMETER
        mqtt.connect.assert_not_called()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

class ClientThingUpdate(unittest.TestCase):
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_open ):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        self.client.handler.send = mock.Mock()

        # error test
        self.client.handler.send.return_value = device_cloud.STATUS_FAILURE
        result = self.client.update_thing_details(name="Update Thing Name")
        assert result != device_cloud.STATUS_SUCCESS
        self.client.handler.send.assert_called_once()

        # success test
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name")
        assert result == device_cloud.STATUS_SUCCESS

        # =================================================================
        # parameter checks, test each param for success
        # =================================================================
        # 2 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription")
        assert result == device_cloud.STATUS_SUCCESS

        # 3 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid")
        assert result == device_cloud.STATUS_SUCCESS

        # 4 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn")
        assert result == device_cloud.STATUS_SUCCESS

        # 5 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei")
        assert result == device_cloud.STATUS_SUCCESS

        # 6 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid")
        assert result == device_cloud.STATUS_SUCCESS

        # 7 params
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid",
                                imsi="my imsi")
        assert result == device_cloud.STATUS_SUCCESS

        # 7 + empty list params
        unset = []
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid",
                                imsi="my imsi",
                                unset_fields=unset)
        assert result == device_cloud.STATUS_SUCCESS

        # 7 + populated list params
        unset = ['name','description','iccid', 'esn','imei','meid','imsi']
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid",
                                imsi="my imsi",
                                unset_fields=unset)
        assert result == device_cloud.STATUS_SUCCESS

        # negative tests: bad list type: scalar
        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid",
                                imsi="my imsi",
                                unset_fields="foo")
        assert result == device_cloud.STATUS_PARSE_ERROR

        # negative tests: bad list type: dict
        unset = {'key':'value'}

        self.client.handler.send.return_value = device_cloud.STATUS_SUCCESS
        result = self.client.update_thing_details(name="Update Thing Name",
                                description="this is a thing desription",
                                iccid="my iccid",
                                esn="my esn",
                                imei="my imei",
                                meid="my meid",
                                imsi="my imsi",
                                unset_fields=unset)
        assert result == device_cloud.STATUS_PARSE_ERROR

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()
