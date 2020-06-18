##Init variables

%define module i2c-piix4
%define version 5.6.11

## Package info declaration

Name:           %{module}-aura-dkms
Version:        %{version}
Release:        1%{?dist}
Summary:        The i2c-piix4 kernel driver, patched to be used with OpenRGB: https://gitlab.com/CalcProgrammer1/OpenRGB

Group: System Environment/Kernel
License: GPLv2
URL: https://bugzilla.kernel.org/show_bug.cgi?id=202587

Requires: dkms >= 1.00
Requires: bash

%description
The i2c-piix4 kernel driver, patched to be used with OpenRGB: https://gitlab.com/CalcProgrammer1/OpenRGB

%prep
mkdir -p "%{_sourcedir}/%{name}" && cd "%{_sourcedir}/%{name}"

cp ../dkms.conf ../Makefile .
cp ../i2c-piix4.c i2c-piix4.c

patch --no-backup-if-mismatch -Np4 < ../piix4.patch

%install
# Copy dkms.conf
install -Dm644 %{_builddir}/%{name}/dkms.conf %{buildroot}/usr/src/%{name}-%{version}/dkms.conf

# Set name and version
sed -e "s/@_PKGBASE@/%{name}/" \
    -e "s/@PKGVER@/%{version}/" \
    -i "%{buildroot}/usr/src/%{name}-%{version}/dkms.conf"

# Copy sources (including Makefile)
cp -r %{_sourcedir}/%{name}/{i2c-piix4.c,Makefile} %{buildroot}/usr/src/%{name}-%{version}/

# udev rule to alow users part of the 'wheel' group to access i2c without root privileges
install -Dm644 %{_sourcedir}/90-i2c-aura.rules %{buildroot}/etc/udev/rules.d/90-i2c-aura.rules

# modprobe needed modules at boot
install -Dm644 %{_sourcedir}/i2c-aura.conf %{buildroot}/etc/modules-load.d/i2c-aura.conf

%clean
if [ "$RPM_BUILD_ROOT" != "/" ]; then
    rm -rf $RPM_BUILD_ROOT
fi

%files
%defattr(-,root,root)
%config /etc/modules-load.d/i2c-aura.conf
/etc/udev/rules.d/90-i2c-aura.rules
/usr/src/%{name}-%{version}/

%pre

%post

dkms add -m %{name} -v %{version} --rpm_safe_upgrade

    if [ `uname -r | grep -c "BOOT"` -eq 0 ] && [ -e /lib/modules/`uname -r`/build/include ]; then
        dkms build -m %{name} -v %{version}
        dkms install -m %{name} -v %{version}
    elif [ `uname -r | grep -c "BOOT"` -gt 0 ]; then
        echo -e ""
        echo -e "Module build for the currently running kernel was skipped since you"
        echo -e "are running a BOOT variant of the kernel."
    else
        echo -e ""
        echo -e "Module build for the currently running kernel was skipped since the"
        echo -e "kernel headers for this kernel do not seem to be installed."
    fi
exit 0

%preun
echo -e
echo -e "Uninstall of %{name} module (version %{version}) beginning:"
dkms remove -m %{name} -v %{version} --all --rpm_safe_upgrade
exit 0
