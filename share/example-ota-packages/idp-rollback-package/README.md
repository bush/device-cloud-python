Application Update With Rollback Example
========================================

Last revision
-------------
Thursday December 13th

Description
-----------
This document provides an example on how to take a filesystem snapshot and
rollback in case of a failed OTA operation.

 *Note: the ota_manifest.spec and update.json files are autogenerated when using the HDC UI "Update" work flow.  Those files are shown below by way of example.*

ota_manifest.spec
-----------------
This is the manifest file that contains the high level information about the update, the platform to update and the update package itself. A few things to note:

- "archive_format" has to be specified to match the compression type used to compress the update package and for this context, as kernel update is only supported for linux platforms, only ".tar.gz" is supported.
- "sha256" has to match the sha256sum of the update package, otherwise it is going to fail.
- The format of this file has to be preserved in order to be uploaded to ePO


```
{
	"manifest": {
		"identifier": "Wind River Software Update Manifest",
		"operation": "app-install",
		"release" : {
			"version" : "new_app",
			"type" : "licensed"
		},
		"platforms": [{
			"product": "cpe:2.3:o:WindRiver:wrlinux:7.0.0.19:rcpl0019:*:en-US:*:hdc:intel-quark:*",
			"mfr_vendor_id" : "WindRiver",
			"mfr_device_id" : "IOT"
		}],
		"channelMode": "append",
			"channels" : [{
			"alias": "iot_ota",
			"name": "WR OTA",
			"type": "epo",
			"archive_format":"tar.gz",
			"url": "system-update.tar.gz",
			"sha256": "c37e38658859c1e0129c70ef46272a88cc6b5b1cc50cbe440a47ae795b381442",
			"language": "0000"
		}],
		"packages": [{ "name": "system-update.rpm" } ],
		"rebootOnCompletion": "no"
	}
}
```

update.json
-----------
This file contains more detailed information about the update and what to be done in all phases of the update. There are 4 phases:

- pre_install
- install
- post_install
- error_action

error_action is only triggered if any of the first 3 phases failed. These phases can be single line commands or scripts; and the scripts can be of any kind as long as the device support it. It is user's responsibility to make sure that the command/script provided will be able to execute. In this example we don't care about executable permissions, since we call the interpreter directly, e.g. `sh <script_name>`

```
{
    "name":"iot-app-complete update",
    "version":"2.0.0",
    "description":"Updating iot-app-complete",
    "pre_install":"sh pre_install.sh iot-app-complete",
    "install":"sh install.sh iot-app-complete",
    "post_install":"sh post_install.sh iot-app-complete",
    "error_action":"sh err_install.sh iot-app-complete",
    "reboot":"no",
    "compatibility": {
            "os_version":  "cpe:2.3:o:WindRiver:wrlinux:7.0.0.15:rcpl0015:*:en-US:*:hdc:intel-quark:*",
            "mfg_device_id":  "device_regex",
            "mfg_vendor_id": "mfg_regex",
            "model_name":    "model_regex",
            "serial": "serial_num_regex"
    },
    "extra_key_value_ary": [ { "key":"value" }],
    "custom_obj": { }
}
```

pre_install.sh
--------------
This is the phase in which all the preparations before an install are done. This is the phase where the snap shot must be taken before anything is changed.

 *Please see the pre_install.sh script for details*

install.sh
-----------
This example install.sh is designed to fail in order to demonstrate rollback.
This example deletes the security credentials and touches a file */BROKEN*.  By removing the security credentials, the device will be effectively *bricked *.   Note: this is exemplary only.  Your install.sh script should do something more useful.  The key thing to remember is that if the install.sh script exits with a non zero value for any reason, the error_action script will be called.

*Please see the install.sh script for details*

err_install.sh
---------------
This script is defined as the "error_action" in the update.json file.  This script will be called if there is a non-zero result returned in any of the install phases.  In this example, we trigger a rollback using the snapshot taken in the pre_install phase and reboot.

*Please see the err_install.sh script for details*

Result
--------
Upon completion of the update, the cloud will receive an error and the state is
rolled back to the initial state before OTA started.
