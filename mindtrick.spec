%define revcount %(git rev-list HEAD | wc -l)
%define treeish %(git rev-parse --short HEAD)
%define localmods %(git diff-files --exit-code --quiet  || date +.m%%j%%H%%M%%S)

%define srcdir   %{getenv:PWD}
%define theme opt/keycloak/standalone/configuration/themes/redgates

Summary: Mindtrick Identity Server
Name: mindtrick
Version: 1.0
Release: %{revcount}.%{treeish}%{localmods}
Distribution: Redgates
Group: System Environment/Daemons
License: MIT
Vendor: Karl Redgate
Packager: Karl Redgate <Karl.Redgate@gmail.com>
BuildArch: noarch

Source0: https://jdbc.postgresql.org/download/postgresql-9.4.1207.jre7.jar

%define _topdir %(echo $PWD)/rpm
BuildRoot: %{_topdir}/BUILDROOT

Requires: keycloak
Requires: redgates-federation
Requires: jq
Requires(pre): shadow-utils
Requires(postun): shadow-utils

%description
Provide an indentity service.

%prep
%build

%install
%{__install} --directory --mode=755 $RPM_BUILD_ROOT/opt/keycloak/modules/org/postgres/main
%{__install} --mode=755 %{srcdir}/postgres/* $RPM_BUILD_ROOT/opt/keycloak/modules/org/postgres/main/
%{__install} --mode=755 $RPM_BUILD_ROOT/../SOURCES/postgresql-9.4.1207.jre7.jar $RPM_BUILD_ROOT/opt/keycloak/modules/org/postgres/main/postgresql.jar

%{__install} --directory --mode=755 $RPM_BUILD_ROOT/etc/init/
%{__install} --mode=755 %{srcdir}/init/*.conf $RPM_BUILD_ROOT/etc/init/

%{__install} --directory --mode=755 $RPM_BUILD_ROOT/usr/libexec/mindtrick/setup
%{__install} --mode=755 %{srcdir}/libexec/mindtrick/setup/* $RPM_BUILD_ROOT/usr/libexec/mindtrick/setup/

%{__install} --directory --mode=755 $RPM_BUILD_ROOT/usr/libexec/mindtrick/keycloak
%{__install} --mode=755 %{srcdir}/libexec/mindtrick/keycloak/* $RPM_BUILD_ROOT/usr/libexec/mindtrick/keycloak/

( cd %{srcdir} ; tar cf - share/mindtrick ) | ( cd $RPM_BUILD_ROOT/usr ; tar xvf - )

%{__install} --directory --mode=755 $RPM_BUILD_ROOT/%{theme}
( cd %{srcdir}/theme ; tar cf - . ) | ( cd $RPM_BUILD_ROOT/%{theme} ; tar xvf - )
%{__install} --directory --mode=755 $RPM_BUILD_ROOT/var/log/mindtrick

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
/etc/init/keycloak.conf
/etc/init/membership.conf
/opt/keycloak/modules/org/postgres/main/module.xml
/opt/keycloak/modules/org/postgres/main/postgresql.jar
/usr/libexec/mindtrick/
/usr/share/mindtrick/
%dir /var/log/mindtrick
/%{theme}

%pre

function group_exists() {
    getent group $* > /dev/null 2>&1
}

function user_exists() {
    getent passwd $* > /dev/null 2>&1
}

group_exists jedi || groupadd jedi || :
user_exists redgates  || useradd redgates  -g jedi --create-home --shell /bin/false || :
user_exists mindtrick || useradd mindtrick -g jedi --create-home --shell /bin/false || :

usermod --groups jedi ec2-user

%post
[ "$1" -gt 1 ] && {
    : Upgrading
}

[ "$1" = 1 ] && {
    : New install
    /usr/libexec/mindtrick/setup/create-keycloak-users
    /usr/libexec/mindtrick/setup/generate-keys
    /usr/libexec/mindtrick/setup/modify-config-file
    /usr/libexec/mindtrick/setup/add_hostname_to_hosts
}

/usr/libexec/mindtrick/setup/update-aliases
/usr/libexec/mindtrick/setup/start-services

: ignore test return value

%verifyscript

# Use --dump instead of --list to get the following
# path size mtime digest mode owner group isconfig isdoc rdev symlink
# user --setperms and --setugids to repair
#
# Date verification
# rpm --query --dump mindtrick | \
# while read path size mtime digest mode owner group isconfig isdoc rdev symlink
# do
#    echo $path should be $mtime but is $(stat --format=%Y $path)
# done
#
# Date fix
# touch --date=@1451922626 /etc/init/keycloak.conf

echo "Failed verification" 1>&2
exit 1

%preun
[ "$1" = 0 ] && {
    : cleanup
}

: ignore test return value

%postun

[ "$1" = 0 ] && {
    : This is really an uninstall
    groupmems --group jedi --del ec2-user
    userdel --remove mindtrick
    userdel --remove redgates
    groupdel jedi
}

: ignore test errs

%changelog

* Fri Sep 21 2018 Karl Redgate <www.redgates.com>
- Initial release

# vim:autoindent expandtab sw=4
