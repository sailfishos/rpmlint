# We don't want rpmlint-mini installed on the OBS so:
#!BuildIgnore: rpmlint-mini

Name:           rpmlint
BuildRequires:  rpm-python
BuildRequires:  python-rpm-macros
BuildRequires:  python3-rpm-macros
BuildRequires:  python3-setuptools
BuildRequires:  python3-toml
BuildRequires:  python3-xdg
BuildRequires:  python3-zstd
Summary:        Rpm correctness checker
Version:        2.0.0
Release:        1
Source0:        %{name}-%{version}.tar.xz
Source1:        CheckDBUSServices.py
Source2:        DesktopTranslationCheck.py
Source3:        CheckGNOMEMacros.py
Source4:        CheckAlternativesGhostFiles.py
Source5:        CheckPolkitPrivs.py
Source6:        LibraryPolicyCheck.py
Source7:        CheckIconSizes.py
Source50:       sailfish.toml
Url:            http://rpmlint.zarb.org/
License:        GPLv2+
Requires:       rpm-python, /usr/bin/readelf, file, findutils, gnu-cpio, bash
Requires:       desktop-file-utils
Requires:       python3-magic
Requires:       python3-toml
Requires:       python3-xdg
Requires:       python3-setuptools
Requires:       python3-zstd
BuildArch:      noarch
# Apply patches to upstream and then in ./upstream use:
#  git format-patch --base=<upstream-tag> <upstream-tag>..<sfos/tag> -o ../rpm/
# this set is:
#  git format-patch --base=master master..jolla/rpmlint-1.12pre -o ../rpm/
Patch0:         0001-ZipCheck-Ignore-any-Exception-here.patch
Patch1:         0002-We-don-t-run-tests-during-the-OBS-build.patch
Patch2:         0003-Add-a-TreatErrorsAsWarnings-configuration-option.patch
Patch4:         0005-Disable-Erlang-checks.patch
Patch5:         0006-Remove-rpm-dependency.patch
Patch6:         0007-Revert-Report-total-time-spent-in-linter.patch
Patch7:         0008-Fix-failure-when-checking-rust-library-files.patch

%description
Rpmlint is a tool to check common errors on rpm packages. Binary and
source packages can be checked.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
%make_build
%py3_build

%install
%py3_install

# Install our checks
pushd $RPM_BUILD_ROOT/%{python3_sitelib}/rpmlint/checks/
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE6} .
cp %{SOURCE7} .
popd

rm -rf  $RPM_BUILD_ROOT/%{_datadir}/man

mkdir -p %{buildroot}%{_sysconfdir}/xdg/rpmlint/
# Install the configdefaults
%__install -m 644 %{SOURCE50} %{buildroot}%{_sysconfdir}/xdg/rpmlint/

%files
%defattr(-,root,root,0755)
%license COPYING
%doc README*
%{_bindir}/*
%dir %{_sysconfdir}/xdg/rpmlint/
%{_sysconfdir}/xdg/rpmlint/*
%{python3_sitelib}
