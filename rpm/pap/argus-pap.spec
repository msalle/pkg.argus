## Turn off meaningless jar repackaging on SL6
%define __jar_repack 0
%define __os_install_post %{nil}

%global base_version 1.7.0
%global base_release 0

%if 0%{?rhel} == 5
%define jdk_version 1.7.0
%else
%define jdk_version 1.8.0
%endif

%if 0%{?rhel} >= 7 || 0%{?fedora} >= 21
%define maven maven
%else
%define maven apache-maven
%endif

Name: argus-pap

Version: 1.7.0
Release: 0%{?dist}
Summary: Argus PAP service

Group: System Environment/Daemons
License: ASL 2.0
URL: https://twiki.cern.ch/twiki/bin/view/EGEE/AuthorizationFramework

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: %{maven}
BuildRequires: java-%{jdk_version}-openjdk-devel

Requires: java-%{jdk_version}-openjdk
Requires: canl-java
Requires: bouncycastle-pkix

%description

Argus is a system meant to render consistent authorization decisions for
distributed services (e.g. compute elements, portals). In order to achieve
this consistency a number of points must be addressed. First, it must be
possible to author and maintain consistent authorization policies. This is
handled by the Policy Administration Point (PAP) component in the service.
Second, authored policies must be evaluated in a consistent manner, a task
performed by the Policy Decision Point (PDP). Finally, the data provided for
evaluation against policies must be consistent (in form and definition) and
this is done by the Policy Enforcement Point (PEP).

This package provides the Argus PAP service.

%prep
%setup -n argus-pap

%build
mvn -U -B %{mvn_settings} package

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
tar -C $RPM_BUILD_ROOT -xvzf target/%{name}.tar.gz

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Stop service on update
if [ $1 -gt 1 ] ; then
    /sbin/service argus-pap stop > /dev/null 2>&1 || :

    # Remove old jars
    if [ -d "/var/lib/argus/pap/lib" ]; then
        rm -f /var/lib/argus/pap/lib/*.jar
        rm -f /var/lib/argus/pap/lib/endorsed/*.jar
        rm -f /var/lib/argus/pap/lib/provided/*.jar
    fi
fi

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service argus-pap stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del argus-pap
fi


# register the service in init.d
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add argus-pap
fi

%postun
if [ $1 -eq 1 ] ; then
    # Restart the service after the update
    /sbin/service argus-pap start > /dev/null 2>&1 || :
fi

%files

%defattr(-,root,root,-)
%{_initrddir}/argus-pap

%dir %{_sysconfdir}/argus/pap

%config(noreplace) %{_sysconfdir}/sysconfig/argus-pap
%config(noreplace) %{_sysconfdir}/argus/pap/pap_configuration.ini
%config(noreplace) %{_sysconfdir}/argus/pap/pap_authorization.ini
%config(noreplace) %{_sysconfdir}/argus/pap/pap-admin.properties

%config %{_sysconfdir}/argus/pap/attribute-mappings.ini

%dir %{_sysconfdir}/argus/pap/logging
%dir %{_sysconfdir}/argus/pap/logging/standalone
%dir %{_sysconfdir}/argus/pap/logging/client

%config %{_sysconfdir}/argus/pap/logging/standalone/logback.xml
%config %{_sysconfdir}/argus/pap/logging/client/logback.xml

%{_sbindir}/*
%{_bindir}/*

%{_datadir}/argus/pap

%dir %{_docdir}/argus/pap

%{_docdir}/argus/pap/RELEASE-NOTES.txt
%{_docdir}/argus/pap/LICENSE.txt

%dir %{_localstatedir}/lib/argus/pap
%dir %{_localstatedir}/lib/argus/pap/repository
%dir %{_localstatedir}/lib/argus/pap/lib
%dir %{_localstatedir}/lib/argus/pap/lib/endorsed
%dir %{_localstatedir}/lib/argus/pap/lib/provided

%{_localstatedir}/lib/argus/pap/lib/*.jar
%{_localstatedir}/lib/argus/pap/lib/endorsed/*.jar
%{_localstatedir}/lib/argus/pap/lib/provided/*.jar

%dir %{_localstatedir}/log/argus/pap

%if 0%{?rhel} >= 7 || 0%{?fedora} >= 21
/lib/systemd/system/argus-pap.service
%else
%exclude /lib/systemd/system/argus-pap.service
%endif

%changelog
* Tue Nov 17 2015 Marco Caberletti <marco.caberletti at cnaf.infn.it> - 1.7.0-0
- Support for Systemd

* Thu Jul 2 2015 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.6.3-0
- Move to java 8

* Mon Feb 2 2015 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.6.2-1
- Bumped version to 1.6.2-1

* Thu Apr 11 2013 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.6.1-1
- Fix for https://savannah.cern.ch/bugs/?101151

* Tue Oct 16 2012 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.6.0-1
- CANL-based Argus PAP.
- Decouple PAP pom version from rpm version.

* Thu Mar 15 2012 Andrea Ceccanti <andrea.ceccanti at cnaf.infn.it> - 1.5.1-1
- Self managed packaging
