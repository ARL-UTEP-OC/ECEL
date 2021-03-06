Name:           snoopy
Version:        2.4.6
Release:        1%{?dist}
Summary:        Snoopy is a wrapper around execve() that logs all executed commands by all users and processes to syslog.
License:        GPLv2
URL:            https://github.com/a2o/snoopy
Source0:        snoopy-%{version}.tar.gz

%description
Snoopy is designed to aid a sysadmin by providing a log of commands executed. Snoopy is completely transparent to the user and applications. It is linked into programs to provide a wrapper around calls to execve(). Logging is done via syslog.

%prep
%autosetup

%build
%configure
make %{?_smp_mflags}

%install
%make_install

mkdir -p %{buildroot}/etc
install -m 0644 etc/snoopy.ini %{buildroot}/%{_sysconfdir}/snoopy.ini

%files
%doc ChangeLog COPYING
%{_bindir}/*
%{_libdir}/*
%{_sbindir}/*
%{_sysconfdir}/*

%post -p /usr/sbin/snoopy-enable
%preun -p /usr/sbin/snoopy-disable

%changelog
* Tue Nov 4 2014 Jeremy Brown <jwbrown77@yahoo.com> 2.0.0rc12-1
- Initial RPM spec for snoopy.
