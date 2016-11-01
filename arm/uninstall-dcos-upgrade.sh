#!/usr/bin/bash

/opt/mesosphere/bin/pkgpanda uninstall && \
rm -rf /opt/mesosphere /etc/mesosphere && \
rm -rf /etc/profile.d/dcos.sh /etc/systemd/system/dcos-cfn-signal.service /etc/systemd/system/dcos-download.service /etc/systemd/system/dcos-link-env.service /etc/systemd/system/dcos-setup.service /etc/systemd/system/multi-user.target.wants/dcos-setup.service /etc/systemd/system/multi-user.target.wants/dcos.target
