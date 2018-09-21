%define revcount %(git rev-list HEAD | wc -l)
%define treeish %(git rev-parse --short HEAD)
%define localmods %(git diff-files --exit-code --quiet  || date +.m%%j%%H%%M%%S)

%define srcdir   %{getenv:PWD}
%define debug_package %{nil}

Name: keycloak
Version: 1.8.0
Release: %{revcount}.%{treeish}%{localmods}
Summary: Keycloak Identity Service

Distribution: RedHat/Services
Group: System Environment/Daemons
License: ASL 2.0
Vendor: Fedora Project
Packager: Karl Redgate <Karl.Redgate@gmail.com>
Requires: java >= 1.8

Source0: http://downloads.jboss.org/keycloak/1.8.0.Final/keycloak-1.8.0.Final.tar.gz

%define _topdir %(echo $PWD)/rpm
BuildRoot: %{_topdir}/BUILDROOT

%description
Provide an identity service.

%prep
%setup -q -n %{name}-%{version}.Final

%build
: Do nothing - this is a tarball of binaries

%install
%{__install} --directory --mode=755 $RPM_BUILD_ROOT/opt/%{name}-%{version}
# ( cd %{name}-%{version}.Final ; cp -r . $RPM_BUILD_ROOT/opt/%{name}-%{version} )
cp --update -r . $RPM_BUILD_ROOT/opt/%{name}-%{version}

: Remove Windows and Debian stuff
rm -rf $RPM_BUILD_ROOT/opt/%{name}-%{version}/bin/service/
rm -f $RPM_BUILD_ROOT/opt/%{name}-%{version}/bin/*.bat
rm -f $RPM_BUILD_ROOT/opt/%{name}-%{version}/bin/*.ps1
rm -f $RPM_BUILD_ROOT/opt/%{name}-%{version}/bin/init.d/wildfly-init-debian.sh

: Create ghost sentinel files
%{__install} --mode=644 /dev/null $RPM_BUILD_ROOT/opt/%{name}-%{version}/standalone/configuration/keycloak.jks
%{__install} --directory --mode=755 $RPM_BUILD_ROOT/opt/%{name}-%{version}/standalone/log
%{__install} --mode=644 /dev/null $RPM_BUILD_ROOT/opt/%{name}-%{version}/standalone/log/server.log

ln -s /opt/%{name}-%{version} $RPM_BUILD_ROOT/opt/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
# Keycloak Properties
%config /opt/%{name}-%{version}/standalone/configuration/application-roles.properties
%config /opt/%{name}-%{version}/standalone/configuration/application-users.properties
%config /opt/%{name}-%{version}/standalone/configuration/keycloak-server.json
%config /opt/%{name}-%{version}/standalone/configuration/logging.properties
%config /opt/%{name}-%{version}/standalone/configuration/mgmt-groups.properties
%config /opt/%{name}-%{version}/standalone/configuration/mgmt-users.properties
%config /opt/%{name}-%{version}/standalone/configuration/standalone.xml
%config /opt/%{name}-%{version}/standalone/configuration/standalone-ha.xml
# User Password configuration settings
%config /opt/%{name}-%{version}/bin/add-user.properties
# Logging Properties
%config /opt/%{name}-%{version}/bin/jboss-cli-logging.properties
%ghost /opt/%{name}-%{version}/standalone/configuration/keycloak.jks
%ghost /opt/%{name}-%{version}/standalone/log/server.log
/opt/%{name}-%{version}
/opt/%{name}

%pre

%post
[ "$1" -gt 1 ] && {
    : Upgrading
}

[ "$1" = 1 ] && {
    : New install
}

: ignore test return value

%verifyscript

: verification

%preun
[ "$1" = 0 ] && {
    : cleanup
}

: ignore test return value

%postun

[ "$1" = 0 ] && {
    : This is really an uninstall
}

: ignore test errs

%changelog

* Fri Sep 21 2018 Karl Redgate <www.redgates.com>
- Initial packaging

# vim:autoindent expandtab sw=4
