#!BuildIgnore: rpmlint-mini

Name:           rpmlint
BuildRequires:  rpm-python
Summary:        Rpm correctness checker
Version:        1.11
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
# Apply patches to upstream and then in ./upstream use:
#  git format-patch --base=<upstream-tag> <upstream-tag>..<sfos/tag> -o ../rpm/
Patch0:         0001-Ignore-the-DistURL-tag-as-obs-adds-one-of-these.patch
Patch1:         0002-ZipCheck-Also-ignore-RuntimeError.patch
Patch2:         0003-ZipCheck-Ignore-IOError-and-zlib.error.patch

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

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
#rm -rf  $RPM_BUILD_ROOT/etc/bash_completion.d
rm -rf  $RPM_BUILD_ROOT/%{_datadir}/man
mv $RPM_BUILD_ROOT/etc/rpmlint/config $RPM_BUILD_ROOT/usr/share/rpmlint/config
head -n 8 $RPM_BUILD_ROOT/usr/share/rpmlint/config > $RPM_BUILD_ROOT/etc/rpmlint/config
# make sure that the package is sane
python -tt %{SOURCE100} $RPM_BUILD_ROOT/usr/share/rpmlint/*.py $RPM_BUILD_ROOT/usr/share/rpmlint/config
%__install -m 644 %{SOURCE20} %{buildroot}/%{_sysconfdir}/rpmlint/

%files
%defattr(-,root,root,0755)
%doc COPYING INSTALL README*
%{_bindir}/*
%{_datadir}/rpmlint
%config(noreplace) %{_sysconfdir}/rpmlint/config
%config %{_sysconfdir}/rpmlint/rpmgroups.config
%dir /etc/rpmlint
%{_sysconfdir}/bash_completion.d/rpmlint
