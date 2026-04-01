Name:           xuanwu-bluetooth-bridge
Version:        1.0.0
Release:        1%{?dist}
Summary:        XuanWu Bluetooth bridge service
License:        Apache-2.0
BuildArch:      noarch

Requires:       python3
Requires:       bluez

%description
Standalone Bluetooth bridge service for XuanWu gateway deployments.

%install
mkdir -p %{buildroot}/opt/xuanwu/bluetooth-bridge
cp -r * %{buildroot}/opt/xuanwu/bluetooth-bridge
mkdir -p %{buildroot}/usr/lib/systemd/system
cp packaging/linux/xuanwu-bluetooth-bridge.service %{buildroot}/usr/lib/systemd/system/

%files
/opt/xuanwu/bluetooth-bridge
/usr/lib/systemd/system/xuanwu-bluetooth-bridge.service
