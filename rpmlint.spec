#!BuildIgnore: rpmlint-mini

Name:           rpmlint
BuildRequires:  rpm-python
Summary:        Rpm correctness checker
Version:        1.4
Release:        1
Source0:        %{name}-%{version}.tar.xz
Source1:        config
Source1001:     config.in
Source2:        DesktopTranslationCheck.py
Source3:        DuplicatesCheck.py
Source4:        CheckBuildRoot.py
Source5:        CheckExecDocs.py
Source6:        CheckPkgConfig.py
Source7:        LibraryPolicyCheck.py
Source8:        CheckCommonFiles.py
Source9:        CheckInitScripts.py
Source10:       CheckIconSizes.py
Source15:       CheckPolkitPrivs.py
Source16:       CheckDBUSServices.py
Source17:       CheckFilelist.py
Source18:       CheckDBusPolicy.py
Source19:       CheckAlternativesGhostFiles.py
Source20:       rpmgroups.config
Source22:       CheckGNOMEMacros.py
Source23:       CheckBuildDate.py
Source100:      syntax-validator.py
Url:            http://rpmlint.zarb.org/
License:        GPLv2+
Group:          System/Packages
Requires:       rpm-python, /usr/bin/readelf, file, findutils, cpio, bash
Requires:       desktop-file-utils
Requires:       python-magic
BuildArch:      noarch
Patch0:         meego.patch
Patch1:         rpmlint-1.4-encoding.patch

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%setup -q -n rpmlint-%{version}
%patch0 -p1
%patch1 -p1 -b .enc
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE3} .
cp -p %{SOURCE4} .
cp -p %{SOURCE5} .
cp -p %{SOURCE6} .
cp -p %{SOURCE7} .
cp -p %{SOURCE8} .
cp -p %{SOURCE9} .
cp -p %{SOURCE10} .
cp -p %{SOURCE15} .
cp -p %{SOURCE16} .
cp -p %{SOURCE17} .
cp -p %{SOURCE18} .
cp -p %{SOURCE19} .
cp -p %{SOURCE22} .
cp -p %{SOURCE23} .

%build
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
# the provided bash-completion does not work and only prints bash errors
rm -rf  $RPM_BUILD_ROOT/etc/bash_completion.d
mv $RPM_BUILD_ROOT/etc/rpmlint/config $RPM_BUILD_ROOT/usr/share/rpmlint/config
head -n 8 $RPM_BUILD_ROOT/usr/share/rpmlint/config > $RPM_BUILD_ROOT/etc/rpmlint/config
# make sure that the package is sane
python -tt %{SOURCE100} $RPM_BUILD_ROOT/usr/share/rpmlint/*.py $RPM_BUILD_ROOT/usr/share/rpmlint/config
%__install -m 644 %{SOURCE20} %{buildroot}/%{_sysconfdir}/rpmlint/

%files
%defattr(-,root,root,0755)
%doc COPYING ChangeLog INSTALL README*
%{_bindir}/*
%{_datadir}/rpmlint
%config(noreplace) /etc/rpmlint/config
%config %{_sysconfdir}/rpmlint/rpmgroups.config
%dir /etc/rpmlint
%{_datadir}/man/man1/rpmlint.1.gz

