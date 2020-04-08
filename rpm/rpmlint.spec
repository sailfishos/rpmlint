#!BuildIgnore: rpmlint-mini
%define python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")

Name:           rpmlint
BuildRequires:  rpm-python
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-toml
BuildRequires:  python3-xdg
Summary:        Rpm correctness checker
Version:        1.12pre
Release:        1
Source0:        %{name}-%{version}.tar.xz
Source1:        CheckDBUSServices.py
Source2:        DesktopTranslationCheck.py
Source3:        CheckGNOMEMacros.py
Source4:        CheckAlternativesGhostFiles.py
Source5:        CheckPolkitPrivs.py
Source6:        LibraryPolicyCheck.py
Source7:        CheckIconSizes.py
Source50:       configdefaults.toml
Url:            http://rpmlint.zarb.org/
License:        GPLv2+
Requires:       rpm-python, /usr/bin/readelf, file, findutils, cpio, bash
Requires:       desktop-file-utils
Requires:       python3-magic
Requires:       python3-toml
Requires:       python3-xdg
Requires:       python3-setuptools
BuildArch:      noarch
# Apply patches to upstream and then in ./upstream use:
#  git format-patch --base=<upstream-tag> <upstream-tag>..<sfos/tag> -o ../rpm/
# this set is:
#  git format-patch --base=master master..jolla/rpmlint-1.12pre -o ../rpm/
Patch0:         0001-ZipCheck-Ignore-any-Exception-here.patch
Patch1:         0002-We-don-t-run-tests-during-the-OBS-build.patch
Patch2:         0003-Fix-rpmlintrc-user-specified-rpmlintrc-check.patch
Patch3:         0004-Add-info-as-an-alias-for-verbose-to-be-back-compatib.patch
Patch4:         0005-Use-v-for-verbose-and-V-for-version.patch
Patch5:         0006-Say-what-config-files-are-causing-problems.patch
Patch6:         0007-Add-a-TreatErrorsAsWarnings-configuration-option.patch

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
make %{?_smp_mflags}

%install

# Use pip3 to install and not direct call to setuptools
pip3 install --no-deps --root=$RPM_BUILD_ROOT --no-index .

# Install our checks
pushd $RPM_BUILD_ROOT/%{python3_sitearch}/rpmlint/checks/
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE6} .
cp %{SOURCE7} .
popd

rm -rf  $RPM_BUILD_ROOT/%{_datadir}/man

mkdir -p %{buildroot}/%{_sysconfdir}/xdg/rpmlint/
# Install the configdefaults
%__install -m 644 %{SOURCE50} %{buildroot}/%{python3_sitearch}/rpmlint/

%files
%defattr(-,root,root,0755)
%doc COPYING README*
%{_bindir}/*
%dir %{_sysconfdir}/xdg/rpmlint/
%{python3_sitearch}
