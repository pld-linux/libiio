#
# Conditional build:
%bcond_without	apidocs		# API documentation

Summary:	Library for interfacing with Linux IIO devices
Name:		libiio
Version:	0.25
Release:	1
License:	LGPL v2.1+ (library), GPL v2 (utilities)
Group:		Libraries
Source0:	https://github.com/analogdevicesinc/libiio/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	c8d5ea5ab44c2e99fab82baea9c92c57
Source1:	iiod.sysconfig
URL:		http://analogdevicesinc.github.io/libiio/
BuildRequires:	avahi-devel
BuildRequires:	bison
BuildRequires:	cmake >= 3.10
%{?with_apidocs:BuildRequires:	doxygen}
BuildRequires:	flex
BuildRequires:	libaio-devel
BuildRequires:	libserialport-devel
BuildRequires:	libusb-devel
BuildRequires:	libxml2-devel
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.011
BuildRequires:	zstd-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
libiio is used to interface to the Linux Industrial Input/Output (IIO)
Subsystem. The Linux IIO subsystem is intended to provide support for
devices that in some sense are analog to digital or digital to analog
converters (ADCs, DACs). This includes, but is not limited to ADCs,
Accelerometers, Gyros, IMUs, Capacitance to Digital Converters (CDCs),
Pressure Sensors, Color, Light and Proximity Sensors, Temperature
Sensors, Magnetometers, DACs, DDS (Direct Digital Synthesis), PLLs
(Phase Locked Loops), Variable/Programmable Gain Amplifiers (VGA,
PGA), and RF transceivers. You can use libiio natively on an embedded
Linux target (local mode), or use libiio to communicate remotely to
that same target from a host Linux, Windows or MAC over USB or
Ethernet or Serial.

%package devel
Summary:	Header files for libiio
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for libiio.

%package apidocs
Summary:	libiio API documentation
Group:		Documentation
BuildArch:	noarch

%description apidocs
libiio API documentation.

%package utils
Summary:	Linux Industrial I/O Subsystem utilities
Requires:	%{name} = %{version}-%{release}

%description utils
Linux Industrial I/O Subsystem utilities.

%package -n iiod
Summary:	Linux Industrial I/O Subsystem daemon
Requires:	%{name} = %{version}-%{release}

%description -n iiod
Linux Industrial I/O Subsystem daemon.

%prep
%setup -q

sed -i 's|/etc/default/iiod|/etc/sysconfig/iiod|' iiod/init/iiod.service.cmakein

%build
%cmake -B build \
	-DINSTALL_UDEV_RULE:BOOL=OFF \
	-DSYSTEMD_UNIT_INSTALL_DIR:PATH=%{systemdunitdir} \
	%{cmake_on_off apidocs WITH_DOC} \
	-DWITH_HWMON:BOOL=ON \
	-DWITH_SERIAL_BACKEND:BOOL=ON \
	-DWITH_SYSTEMD:BOOL=ON \
	-DWITH_TESTS:BOOL=ON \
	-DWITH_ZSTD:BOOL=ON

%{__make} -C build

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%{?with_apidocs:%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/libiio*-doc}

install -D %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/iiod

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%post -n iiod
%systemd_post iiod.service

%preun -n iiod
%systemd_preun iiod.service

%postun -n iiod
%systemd_reload

%files
%defattr(644,root,root,755)
%doc CONTRIBUTING.md Contributors.md README.md
%attr(755,root,root) %{_libdir}/libiio.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libiio.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libiio.so
%{_includedir}/iio.h
%{_pkgconfigdir}/libiio.pc

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc build/html/*
%endif

%files utils
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/iio_attr
%attr(755,root,root) %{_bindir}/iio_genxml
%attr(755,root,root) %{_bindir}/iio_info
%attr(755,root,root) %{_bindir}/iio_readdev
%attr(755,root,root) %{_bindir}/iio_reg
%attr(755,root,root) %{_bindir}/iio_stresstest
%attr(755,root,root) %{_bindir}/iio_writedev

%files -n iiod
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/iiod
%attr(755,root,root) %{_sbindir}/iiod
%{systemdunitdir}/iiod.service
