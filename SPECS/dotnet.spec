# Avoid provides/requires from private libraries
%global privlibs             libhostfxr
%global privlibs %{privlibs}|libclrjit
%global privlibs %{privlibs}|libcoreclr
%global privlibs %{privlibs}|libcoreclrtraceptprovider
%global privlibs %{privlibs}|libdbgshim
%global privlibs %{privlibs}|libhostpolicy
%global privlibs %{privlibs}|libmscordaccore
%global privlibs %{privlibs}|libmscordbi
%global privlibs %{privlibs}|libsos
%global privlibs %{privlibs}|libsosplugin
%global __provides_exclude ^(%{privlibs})\\.so
%global __requires_exclude ^(%{privlibs})\\.so

# Filter flags not supported by clang/dotnet:
#  -fcf-protection is not supported by clang
#  -fstack-clash-protection is not supported by clang
#  -specs= is not supported by clang
#  -fpie is added manually instead of via -specs
%global dotnet_cflags %(echo %optflags | sed -e 's/-fcf-protection//' | sed -e 's/-fstack-clash-protection//' | sed -re 's/-specs=[^ ]*//g')
%global dotnet_ldflags %(echo %{__global_ldflags} | sed -re 's/-specs=[^ ]*//g')

%if 0%{?fedora}
%global use_bundled_libunwind 0
%else
%global use_bundled_libunwind 1
%endif

%global simple_name dotnet

%global host_version 2.1.30
%global runtime_version 2.1.30
%global sdk_version 2.1.526

Name:                 dotnet
Version:              %{sdk_version}
Release:              1%{?dist}.openela
Summary:              .NET Core CLI tools and runtime
License:              MIT and ASL 2.0 and BSD
URL:                  https://github.com/dotnet/

# The source is generated on a RHEL box via:
# ./build-dotnet-tarball v%%{sdk_version}-SDK

Source0:              dotnet-v%{sdk_version}-SDK.tar.gz
Source1:              check-debug-symbols.py
Source2:              dotnet.sh

Patch10:              corefx-optflags-support.patch
Patch11:              corefx-32956-alpn.patch
# This patch is generally applied at tarball-build time, except when we dont build the tarball
Patch12:              build-corefx-disable-werror.patch

Patch100:             coreclr-pie.patch
Patch101:             coreclr-libunwind-fno-common.patch

Patch300:             core-setup-4510-commit-id.patch
Patch301:             core-setup-pie.patch

Patch400:             cli-telemetry-optout.patch
Patch401:             core-openela-rid.patch

ExclusiveArch:        x86_64

BuildRequires:        clang
BuildRequires:        cmake
# Bootstrap SDK needs OpenSSL 1.0 to run, but we can build and then
# run with either OpenSSL 1.0 or 1.1
%if 0%{?fedora} >= 26 || 0%{?rhel} >= 8
BuildRequires:        compat-openssl10
%endif
BuildRequires:        git
BuildRequires:        glibc-langpack-en
BuildRequires:        hostname
BuildRequires:        krb5-devel
BuildRequires:        libcurl-devel
BuildRequires:        libicu-devel
%if ! %{use_bundled_libunwind}
BuildRequires:        libunwind-devel
%endif
BuildRequires:        lldb-devel
BuildRequires:        llvm
BuildRequires:        lttng-ust-devel
BuildRequires:        make
BuildRequires:        openssl-devel
BuildRequires:        python3
BuildRequires:        strace
BuildRequires:        zlib-devel

Requires:             %{simple_name}-sdk-2.1%{?_isa} >= %{sdk_version}-%{release}

%description
.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, macOS and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

.NET Core contains a runtime conforming to .NET Standards a set of
framework libraries, an SDK containing compilers and a 'dotnet'
application to drive everything.


%package -n %{simple_name}-host

Version:              %{host_version}
Summary:              .NET command line launcher

%description -n %{simple_name}-host
The .NET Core host is a command line program that runs a standalone
.NET core application or launches the SDK.

.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%package -n %{simple_name}-host-fxr-2.1

Version:              %{host_version}
Summary:              .NET Core command line host resolver

# Theoretically any version of the host should work. But lets aim for the one
# provided by this package, or from a newer version of .NET Core
Requires:             %{simple_name}-host%{?_isa} >= %{host_version}-%{release}

%description -n %{simple_name}-host-fxr-2.1
The .NET Core host resolver contains logic to resolve and select the
right version of the .NET Core SDK or runtime to use.

.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

%package -n %{simple_name}-runtime-2.1

Version:              %{runtime_version}
Summary:              NET Core 2.1 runtime

Requires:             %{simple_name}-host-fxr-2.1%{?_isa} >= %{host_version}-%{release}

# libicu is dlopen()ed
Requires:             libicu

%description -n %{simple_name}-runtime-2.1
The .NET Core runtime contains everything needed to run .NET Core applications.
It includes a high performance Virtual Machine as well as the framework
libraries used by .NET Core applications.

.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

%package -n %{simple_name}-sdk-2.1

Version:              %{sdk_version}
Summary:              .NET Core 2.1 Software Development Kit

Requires:             %{simple_name}-sdk-2.1.5xx%{?_isa} >= %{sdk_version}-%{release}

%description -n %{simple_name}-sdk-2.1
The .NET Core SDK is a collection of command line applications to
create, build, publish and run .NET Core applications.

.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.

%package -n %{simple_name}-sdk-2.1.5xx

Version:              %{sdk_version}
Summary:              .NET Core 2.1.5xx Software Development Kit

Requires:             %{simple_name}-runtime-2.1%{?_isa} >= %{runtime_version}-%{release}

%description -n %{simple_name}-sdk-2.1.5xx
The .NET Core SDK is a collection of command line applications to
create, build, publish and run .NET Core applications.

.NET Core is a fast, lightweight and modular platform for creating
cross platform applications that work on Linux, Mac and Windows.

It particularly focuses on creating console applications, web
applications and micro-services.


%prep
%setup -q -n %{simple_name}-v%{sdk_version}-SDK

pushd src/corefx
%patch10 -p1
%patch11 -p1
%patch12 -p1
popd

pushd src/coreclr
%patch100 -p1
%patch101 -p1
popd

pushd src/core-setup
%patch300 -p1
%patch301 -p1
popd

pushd src/cli
%patch400 -p1
popd

# Fix bad hardcoded path in build
sed -i 's|/usr/share/dotnet|%{_libdir}/%{simple_name}|' src/core-setup/src/corehost/common/pal.unix.cpp

# Disable warnings
sed -i 's|skiptests|skiptests ignorewarnings|' repos/coreclr.proj

# If CLR_CMAKE_USE_SYSTEM_LIBUNWIND=TRUE is missing, add it back
grep CLR_CMAKE_USE_SYSTEM_LIBUNWIND repos/coreclr.proj || \
    sed -i 's|\$(BuildArguments) </BuildArguments>|$(BuildArguments) cmakeargs -DCLR_CMAKE_USE_SYSTEM_LIBUNWIND=TRUE</BuildArguments>|' repos/coreclr.proj

%if %{use_bundled_libunwind}
# Use bundled libunwind
sed -i 's|-DCLR_CMAKE_USE_SYSTEM_LIBUNWIND=TRUE|-DCLR_CMAKE_USE_SYSTEM_LIBUNWIND=FALSE|' repos/coreclr.proj
%endif

cat source-build-info.txt

%patch401 -p1

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1

export LLVM_HOME=/opt/rh/llvm-toolset-6.0/root/usr
export CMAKE_INCLUDE_PATH="/opt/rh/llvm-toolset-6.0/root/usr/include"

export CFLAGS="%{dotnet_cflags}"
export CXXFLAGS="%{dotnet_cflags}"
export LDFLAGS="%{dotnet_ldflags}"

test -f Tools/ilasm/ilasm

Tools/dotnetcli/dotnet --info

VERBOSE=1 ./build.sh \
  /v:n \
  /p:MinimalConsoleLogOutput=false \
  /p:ContinueOnPrebuiltBaselineError=true


%install
install -d -m 0755 %{buildroot}%{_libdir}/%{simple_name}/
ls bin/x64/Release
tar xf bin/x64/Release/dotnet-sdk-%{sdk_version}-*.tar.gz -C %{buildroot}%{_libdir}/%{simple_name}/

# Fix permissions on files
find %{buildroot}%{_libdir}/%{simple_name}/ -type f -name '*.props' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/%{simple_name}/ -type f -name '*.targets' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/%{simple_name}/ -type f -name '*.dll' -exec chmod -x {} \;
find %{buildroot}%{_libdir}/%{simple_name}/ -type f -name '*.pubxml' -exec chmod -x {} \;

# Provided by dotnet-host from another SRPM
# Add ~/.dotnet/tools to $PATH for all users
#install -dm 0755 %%{buildroot}%%{_sysconfdir}/profile.d/
#install %%{SOURCE2} %%{buildroot}%%{_sysconfdir}/profile.d/

# Provided by dotnet-host from another SRPM
#install -dm 755 %%{buildroot}/%%{_datadir}/bash-completion/completions
# dynamic completion needs the file to be named the same as the base command
#install src/cli/scripts/register-completions.bash %%{buildroot}/%%{_datadir}/bash-completion/completions/dotnet

# TODO: the zsh completion script needs to be ported to use #compdef
#install -dm 755 %%{buildroot}/%%{_datadir}/zsh/site-functions
#install src/cli/scripts/register-completions.zsh %%{buildroot}/%%{_datadir}/zsh/site-functions/_dotnet

# Provided by dotnet-host from another SRPM
#install -d -m 0755 %%{buildroot}%%{_bindir}
#ln -s %%{_libdir}/%%{simple_name}/dotnet %%{buildroot}%%{_bindir}/

# Provided by dotnet-host from another SRPM
#install -d -m 0755 %%{buildroot}%%{_mandir}/man1/
#find -iname 'dotnet*.1' -type f -exec cp {} %%{buildroot}%%{_mandir}/man1/ \;

# Check debug symbols in all elf objects. This is not in %%check
# because native binaries are stripped by rpm-build after %%install.
# So we need to do this check earlier.
echo "Testing build results for debug symbols..."
%{SOURCE1} -v %{buildroot}%{_libdir}/%{simple_name}/

# Self-check
%{buildroot}%{_libdir}/%{simple_name}/dotnet --info

# Provided by dotnet-host from another SRPM
rm %{buildroot}%{_libdir}/%{simple_name}/LICENSE.txt
rm %{buildroot}%{_libdir}/%{simple_name}/ThirdPartyNotices.txt
rm %{buildroot}%{_libdir}/%{simple_name}/dotnet


%files -n %{simple_name}-host-fxr-2.1
%dir %{_libdir}/%{simple_name}/host/fxr
%{_libdir}/%{simple_name}/host/fxr/%{host_version}

%files -n %{simple_name}-runtime-2.1
%dir %{_libdir}/%{simple_name}/shared
%dir %{_libdir}/%{simple_name}/shared/Microsoft.NETCore.App
%{_libdir}/%{simple_name}/shared/Microsoft.NETCore.App/%{runtime_version}

%files -n %{simple_name}-sdk-2.1
# empty package useful for dependencies

%files -n %{simple_name}-sdk-2.1.5xx
%dir %{_libdir}/%{simple_name}/sdk
%{_libdir}/%{simple_name}/sdk/%{sdk_version}

%changelog
* Thu Jan 25 2024 Release Engineering <releng@openela.org> - %{sdk_version}.openela
- Add OpenELA Runtime ID (adapted from Michael Young)

* Mon Aug 16 2021 Omair Majid <omajid@redhat.com> - 2.1.526-1
- Update to .NET SDK 2.1.526 and Runtime 2.1.30
- Resolves: RHBZ#1993896

* Tue Aug 03 2021 Omair Majid <omajid@redhat.com> - 2.1.525-1
- Update to .NET SDK 2.1.525 and Runtime 2.1.29
- Resolves: RHBZ#1988581

* Tue Apr 27 2021 Omair Majid <omajid@redhat.com> - 2.1.524-1
- Update to .NET SDK 2.1.524 and Runtime 2.1.28
- Resolves: RHBZ#1953766

* Thu Apr 08 2021 Omair Majid <omajid@redhat.com> - 2.1.523-1
- Update to .NET Core SDK 2.1.523 and Runtime 2.1.27
- Resolves: RHBZ#1947454

* Tue Mar 09 2021 Omair Majid <omajid@redhat.com> - 2.1.522-2
- Update to .NET Core SDK 2.1.522 and Runtime 2.1.26
- Resolves: RHBZ#1933334

* Wed Feb 10 2021 Omair Majid <omajid@redhat.com> - 2.1.521-2
- Update to .NET Core SDK 2.1.521 and Runtime 2.1.25
- Resolves: RHBZ#1921939

* Tue Jan 12 14:41:40 EST 2021 Omair Majid <omajid@redhat.com> - 2.1.520-1
- Update to .NET Core SDK 2.1.520 and Runtime 2.1.24
- Resolves: RHBZ#1905575

* Tue Oct 06 2020 Omair Majid <omajid@redhat.com> - 2.1.519-2
- Bump release
- Resolves: RHBZ#1884080

* Thu Oct 01 2020 Omair Majid <omajid@redhat.com> - 2.1.519-1
- Update to .NET Core SDK 2.1.519 and Runtime 2.1.23
- Drop patches merged upstream
- Resolves: RHBZ#1884080

* Fri Sep 04 2020 Omair Majid <omajid@redhat.com> - 2.1.518-1
- Update to .NET Core SDK 2.1.518 and Runtime 2.1.22
- Resolves: RHBZ#1874064

* Mon Aug 17 2020 Omair Majid <omajid@redhat.com> - 2.1.517-1
- Update to .NET Core SDK 2.1.517 and Runtime 2.1.21
- Resolves: RHBZ#1866119

* Fri Jul 17 2020 Omair Majid <omajid@redhat.com> - 2.1.516-1
- Update to .NET Core SDK 2.1.516 and Runtime 2.1.20
- Resolves: RHBZ#1851971
- Resolves: RHBZ#1856937

* Thu Jun 11 2020 Omair Majid <omajid@redhat.com> - 2.1.515-2
- Update to .NET Core SDK 2.1.515 and Runtime 2.1.19
- Resolves: RHBZ#1843672

* Mon Jun 01 2020 Omair Majid <omajid@redhat.com> - 2.1.514-3
- Update to .NET Core SDK 2.1.514 and Runtime 2.1.18
- Resolves: RHBZ#1828392

* Mon Mar 23 2020 Omair Majid <omajid@redhat.com> - 2.1.513-2
- Update to .NET Core SDK 2.1.513 and Runtime 2.1.17
- Resolves: RHBZ#1815640

* Sat Mar 07 2020 Omair Majid <omajid@redhat.com> - 2.1.512-1
- Update to .NET Core Runtime 2.1.16 and SDK 2.1.512
- Resolves: RHBZ#1799068

* Fri Jan 17 2020 Omair Majid <omajid@redhat.com> - 2.1.511-2
- Update to .NET Core Runtime 2.1.15 and SDK 2.1.511
- Resolves: RHBZ#1786190

* Thu Aug 29 2019 Omair Majid <omajid@redhat.com> - 2.1.509-2
- Update to .NET Core Runtime 2.1.13 and SDK 2.1.509
- Resolves: RHBZ#1742959

* Thu Aug 15 2019 Omair Majid <omajid@redhat.com> - 2.1.508-3
- Remove dotnet and dotnet host packages
- Resolves: RHBZ#1740879

* Tue Aug 13 2019 Omair Majid <omajid@redhat.com> - 2.1.508-2
- Bump release
- Resolves: RHBZ#1740308

* Thu Jul 11 2019 Omair Majid <omajid@redhat.com> - 2.1.508-1
- Update to .NET Core Runtime 2.1.12 and SDK 2.1.508
- Resolves: RHBZ#1728823

* Wed Jun 12 2019 Omair Majid <omajid@redhat.com> - 2.1.507-4
- Bump version
- Related: RHBZ#1712158

* Mon May 20 2019 Omair Majid <omajid@redhat.com> - 2.1.507-2
- Link against strerror_r correctly
- Resolves: RHBZ#1712158

* Thu May 02 2019 Omair Majid <omajid@redhat.com> - 2.1.507-1
- Update to .NET Core Runtime 2.1.11 and SDK 2.1.507
- Resolves: RHBZ#1705284

* Wed Apr 17 2019 Omair Majid <omajid@redhat.com> - 2.1.506-2
- Switch away from SCL dependencies for clang/llvm/lldb
- Resolves: RHBZ#1700908

* Tue Apr 09 2019 Omair Majid <omajid@redhat.com> - 2.1.506-1
- Update to .NET Core Runtime 2.1.10 and SDK 2.1.506
- Resolves: RHBZ#1696371

* Fri Feb 22 2019 Omair Majid <omajid@redhat.com> - 2.1.504-1
- Update to .NET Core Runtime 2.1.8 and SDK 2.1.504
- Sync with Fedora copr spec file
- Resolves: RHBZ#1646713

* Fri Oct 12 2018 Omair Majid <omajid@redhat.com> - 2.1.403-4
- Disable telemetry via code, not just environment variable
- Resolves: rhbz#1638093

* Thu Oct 11 2018 Omair Majid <omajid@redhat.com> - 2.1.403-3
- Disable telemetry by default
- Resolves: rhbz#1638093

* Wed Oct 10 2018 Omair Majid <omajid@redhat.com> - 2.1.403-2
- Target the latest ASP.NET Core version instead of 2.1.1
- Resolves: rhbz#1636585

* Thu Oct 04 2018 Omair Majid <omajid@redhat.com> - 2.1.403-1
- Update to .NET Core Runtime 2.1.5 and SDK 2.1.403
- Resolves: rhbz#1634182

* Mon Oct 01 2018 Omair Majid <omajid@redhat.com> - 2.1.402-5
- Backport fix to correct order of SSL_CERT_FILE and SSL_CERT_DIR lookup
- Resolves: rhbz#1633742

* Thu Sep 27 2018 Omair Majid <omajid@redhat.com> - 2.1.402-4
- Add ~/.dotnet/tools to $PATH to make it easier to use dotnet tools
- Resolves: rhbz#1630439

* Tue Sep 25 2018 Omair Majid <omajid@redhat.com> - 2.1.402-3
- Update .NET Core Runtime 2.1.4 and SDK 2.1.402
- Resolves: rhbz#1628997

* Tue Sep 11 2018 Omair Majid <omajid@redhat.com> - 2.1.401-3
- Use standard flags to build .NET Core
- Resolves: rhbz#1624105

* Tue Sep 11 2018 Omair Majid <omajid@redhat.com> - 2.1.401-2
- Bundle libunwind
- Resolves: rhbz#1626285

* Fri Aug 17 2018 Omair Majid <omajid@redhat.com> - 2.1.401-1
- Update .NET Core Runtime 2.1.3 and SDK 2.1.401
- Drop upstreamed patches

* Mon Aug 06 2018 Omair Majid <omajid@redhat.com> - 2.1.302-1
- Initial build.
- Un-SCLized the package.

* Wed Jul 4 2018 Omair Majid <omajid@redhat.com> - 2.1.302-1
- Update to .NET Core Runtime 2.1.2 and SDK 2.1.302

* Wed Jun 20 2018 Omair Majid <omajid@redhat.com> - 2.1.301-5
- Add sdk-2.1.3xx subpackage

* Tue Jun 19 2018 Omair Majid <omajid@redhat.com> - 2.1.301-4
- Rebuild to pick up new lttng-ust

* Tue Jun 19 2018 Omair Majid <omajid@redhat.com> - 2.1.301-3
- Add workaround for unreadable system certificates
- Resolves: rhbz#1588099

* Tue Jun 19 2018 Omair Majid <omajid@redhat.com> - 2.1.301-2
- Add updated man pages
- Resolves: rhbz#1584790

* Thu Jun 14 2018 Omair Majid <omajid@redhat.com> - 2.1.301-1
- Update to .NET Core SDK 2.1.301

* Wed May 30 2018 Omair Majid <omajid@redhat.com> - 2.1.300-7
- Explicitly require a modified libcurl

* Tue May 29 2018 Omair Majid <omajid@redhat.com> - 2.1.300-6
- Install bash completions in %%{_root_datadir}

* Mon May 28 2018 Omair Majid <omajid@redhat.com> - 2.1.300-5
- Add provides for dotnet-sdk-2.1.3xx

* Mon May 28 2018 Omair Majid <omajid@redhat.com> - 2.1.300-4
- Remove patch for ASP.NET Core templates. No longer needed for 2.1.

* Fri May 25 2018 Omair Majid <omajid@redhat.com> - 2.1.300-3
- Remove net46 symlink

* Thu May 24 2018 Omair Majid <omajid@redhat.com> - 2.1.300-2
- Rebuild to pick up updated dependencies

* Thu May 24 2018 Omair Majid <omajid@redhat.com> - 2.1.300-1
- New package. Import from Fedora (DotNet SIG package).
