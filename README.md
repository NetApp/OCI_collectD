# OCI write plugin for collectd

The OCI collectd write plugin is a publishing extension for [collectd](https://collectd.org/), an open source statistic gathering daemon. With this extension all configured collectd metrics are automatically published to OCI server. This plugin allows monitoring of servers and applications.

## Attention:
 * Python 2.7 is required
 * Internet access is required for installation
 * SELinux is not supported
 * Supported Linux distributions and versions
   - RHEL/CentOS 7
   - Amazon AMI
   - Ubuntu LTS 16.04
   - Debian 9
   - SUSE Linux Enterprise Server 12

## Installation
 * Download [installation script](https://raw.githubusercontent.com/peter-z-xu/collectd-oci/master/src/setup.py), place it on the host and execute it:
```
chmod +x setup.py
sudo ./setup.py
```

 * Follow on screen instructions

## Configuration

### Plugin specific configuration
The default location of the configuration file used by collectd-oci plugin is: `/etc/collectd.d/oci.conf`. This file allows modification of the following parameters:
 * __host__ - The hostname or IP address for OCI server.
 * __token__ - The authentication token to report integration data into OCI server.
 * __report_interval__ - The interval in second to report data. The minimum value allowed is 60 and the maximum value allowed is 3600.
 * __failed_report_queue_size__ - The queue size to save failed report data for retry, the default is 0 to disable it.
  The minimum value allowed is 0 and the maximum value allowed is 10000.
 * __aggregation_type__ - The aggregration type for guaged values. In one report, there can be multiple samples, this is the type for you to specify how to aggregate the samples.
  The default is average, but you can specify other values like minimum, maximum, last.
 * __plugins__ - The collectd plugins to report. There can be many collectd plugins to collect both system and application data, however, you may not want to report all of them.
  This is the configuration to specify the plugins to report, by default, it is "cpu,memory". The configuration should be comma separated without whitespaces.
 * __logging_level__ - The logging level, debug, info, warning or error. The default is info.

#### Example configuration file
```
LoadPlugin python
<Plugin python>
    ModulePath "/usr/share/collectd/collectd-oci-plugin"
    LogTraces true
    Interactive false
    Import "oci"
    Encoding "utf-8"
    <Module oci>
        host "10.97.120.180"
        token "b3569d68-63bd-4c2e-ab5d-2f236fc86673"
        report_interval "60"
        failed_report_queue_size "0"
        aggregation_type "average"
        plugins "cpu,memory"
        logging_level "info"
    </Module>
</Plugin>
```

## Usage
Once the plugin is configured correctly, restart collectd to load new configuration.
```
For systemd as system and service manager, sudo systemctl restart collectd
Otherise, sudo /etc/init.d/collectd restart
```

From now on your collectd metrics will be published to OCI server

## Troubleshooting
OCI plugin logs into /var/log/collectd_oci.log. You can update the logging_level for debugging purpose.
The OCI collectd plugin log can be filtered for OCI plugin events using grep:
```
grep "[NetAppOnCommandInsightPlugin]" /var/log/collectd_oci.log
```

## Contributing

1. Create your fork by clicking Fork button on top of the page.
2. Download your repository: `git clone https://github.com/USER/collectd-oci.git`
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'My new feature description'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## License
The MIT License (MIT)

Copyright (c) 2017. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
