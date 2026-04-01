Name:           xuanwu-nearlink-bridge
Version:        1.0.0
Release:        1%{?dist}
Summary:        XuanWu NearLink bridge service
License:        Apache-2.0
BuildArch:      noarch

Requires:       python3

%description
Standalone NearLink bridge service for XuanWu gateway deployments.

%install
mkdir -p %{buildroot}/opt/xuanwu/nearlink-bridge
cp -r * %{buildroot}/opt/xuanwu/nearlink-bridge
mkdir -p %{buildroot}/usr/lib/systemd/system
cp packaging/linux/xuanwu-nearlink-bridge.service %{buildroot}/usr/lib/systemd/system/

%files
/opt/xuanwu/nearlink-bridge
/usr/lib/systemd/system/xuanwu-nearlink-bridge.service
