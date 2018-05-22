Description
===========
The device manager will publish an attribute called
"remote_access_support" with a value defind below.  The iot.cfg will
contain the default remote_access_support values, but if the service
is not listening locally, the details will not be published.

Once the device_manager.py is run, it will read the iot.cfg and then
check the requested service, e.g. is the telnet port 23 listening.  If
the service is listening on the device, the device manager will
publish an attribute including that service.  The content of the
attribute is a list of services and ports supported.

The goal is that this attribute "remote_access_support" will be used
by the UI to setup a remote session.  If the device does not publish
the attribute, then the device is assumed to not support remote
access.

Note: the device manager does not start the remote access services.
The OS is expected to have the services properly configured.

Multi Channel
-------------
Multiple connections are supported to the same remote access connection, e.g.:
```sh
ssh localhost -p 1234
```
Repeat the above N times.

Reconnecting
------------
You can exit and reconnection on the same remote access session.


Requirements
------------
Device Manager:
  * device manager will read the iot.cfg for remote_access_support
  * device manager will check to see if the configured service port is listening
    * if it is listening, add it to the remote attributes list
    * if it is not listening, then do not add it to the list.
  * device manager will publish an attribute called "remote_access_support"
  * the content of the "remote_access_support" attribute will be a
  JSON list of protocols (see format below)
  * the protocol name will be used by the UI to display the type of
  service
  * the port will be used in the action to connect to the device
  * optional parameters for a maximum session timeout will be used as
  hints or defaults in the UI
 

JSON String Published As Attribute
----------------------------------
The following is published as a JSON string:
(added white space for readability)
```
[
	{ "protocol": "Telnet", "port": "23", "session_timeout": "60" },
	{ "protocol": "SSH", "port": "22" }, 
	{ "protocol": "VNC", "port": "5900" },
	{ "protocol": "HTTP", "port": "80" }
]    
```

Changes To iot.cfg 
------------------
```
	"remote_access_support":[
		{ "name": "Telnet", "port":"23", "session_timeout":"120" },
		{ "name": "SSH",    "port":"22"   },
		{ "name": "VNC",    "port":"5900" },
		{ "name": "HTTP",   "port":"80"   }
	]
```

Required paramters:
  * name: name of the protocol to display in the UI
  * port: port that is bound on the device
Optional parameters:
  * session_timeout in minutes:
