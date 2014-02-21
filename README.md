sync-tot
========

A Python script which finds the latest build from HTTP builds hosting and upload it onto TOT

Overview
--------

TOT (https://github.com/OpenFibers/php-tot) is a PHP application which could be hosted on a web server. You can upload your IPA from desktop and then install OTA (Over The Air) on your iOS devices.

If you want to use TOT with your daily build system, the best way is the build system pushing IPA to TOT after building. Sync-tot.py does the integration in pulling way - everytime it got executed, sync-tot.py will find the latest build (current implementation will try to find build on web server) and upload it onto TOT.

Syntax
------

    sync-tot.py config.json

Config file is in JSON format (http://en.wikipedia.org/wiki/JSON). Let's say your build could be found at "http://foo.com/allbuilds/iOS-client.123/InHouse_123.ipa" where 123 is the build number which will increase for every new build. Your config file should look like this:
```json
{
	"base_url"      : "http://foo.com/allbuilds/",
	"build_pattern" : "iOS-client.(\\d+)",
	"build_path"    : "iOS-client.{bn}/InHouse_{bn}.ipa",
	"tot_url"       : "http://bar.com/tot/",
}
```

"build_pattern" is a regular expression that sync-tot.py uses it to filter the build number.

You may use "{bn}" to take the place of build number in "build_path".

Requirements
------------

You need Python (http://www.python.org/) 2.7.x to run this tool script.

sync-tot.py uses poster (https://pypi.python.org/pypi/poster/) to POST package onto TOT.

License
-------

sync-tot.py is available under the MIT license.
