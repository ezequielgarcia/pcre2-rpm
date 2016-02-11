# This is stable release:
#%%global rcversion RC1
Name:       pcre2
Version:    10.21
Release:    %{?rcversion:0.}2%{?rcversion:.%rcversion}%{?dist}
%global     myversion %{version}%{?rcversion:-%rcversion}
Summary:    Perl-compatible regular expression library
Group:      System Environment/Libraries
# the library:                          BSD
# pcre2test (linked to GNU readline):   BSD (linked to GPLv3+)
# COPYING:                              see LICENCE file
# LICENSE:                              BSD text and declares Public Domain
#                                       for testdata
#Not distributed in binary package
# autotools:                            GPLv3+ with exception
# install-sh:                           MIT
# testdata:                             Public Domain
License:    BSD
URL:        http://www.pcre.org/
Source:     ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/%{?rcversion:Testing/}%{name}-%{myversion}.tar.bz2
# Do no set RPATH if libdir is not /usr/lib
Patch0:     pcre2-10.10-Fix-multilib.patch
# Report unmatched closing parantheses properly, in upstream after 10.21
Patch1:     pcre2-10.21-Detect-unmatched-closing-parentheses-in-the-pre-scan.patch
# Fix pcre2test for expressions with a callout inside a look-behind assertion,
# upstream bug #1783, fixed in upstream after 10.21
Patch2:     pcre2-10.21-Fix-pcre2test-loop-when-a-callout-is-in-an-initial-l.patch
# Fix workspace overflow for (*ACCEPT) with deeply nested parentheses,
# upstream bug #1791, fixed in upstream after 10.21
Patch3:     pcre2-10.21-Fix-workspace-overflow-for-deep-nested-parentheses-w.patch

# New libtool to get rid of RPATH and to use distribution autotools
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  coreutils
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  readline-devel

%description
PCRE2 is a re-working of the original PCRE (Perl-compatible regular
expression) library to provide an entirely new API.

PCRE2 is written in C, and it has its own API. There are three sets of
functions, one for the 8-bit library, which processes strings of bytes, one
for the 16-bit library, which processes strings of 16-bit values, and one for
the 32-bit library, which processes strings of 32-bit values. There are no C++
wrappers.

The distribution does contain a set of C wrapper functions for the 8-bit
library that are based on the POSIX regular expression API (see the pcre2posix
man page). These can be found in a library called libpcre2posix. Note that
this just provides a POSIX calling interface to PCRE2; the regular expressions
themselves still follow Perl syntax and semantics. The POSIX API is
restricted, and does not give full access to all of PCRE2's facilities.


%package devel
Summary:    Development files for %{name}
Group:      Development/Libraries
Requires:   %{name}%{?_isa} = %{version}-%{release}
Requires:   gcc

%description devel
Development files (headers, libraries for dynamic linking, documentation)
for %{name}.  The header file for the POSIX-style functions is called
pcre2posix.h.

%package static
Summary:    Static library for %{name}
Group:      Development/Libraries
Requires:   %{name}-devel%{_isa} = %{version}-%{release}

%description static
Library for static linking for %{name}.

%package tools
Summary:    Auxiliary utilities for %{name}
# pcre2test (linked to GNU readline):   BSD (linked to GPLv3+)
License:    BSD and GPLv3+
Group:      Development/Tools
Requires:   %{name}%{_isa} = %{version}-%{release}

%description tools
Utilities demonstrating PCRE2 capabilities like pcre2grep or pcre2test.

%prep
%setup -q -n %{name}-%{myversion}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
# Because of multilib patch
libtoolize --copy --force
autoreconf -vif

%build
# There is a strict-aliasing problem on PPC64, bug #881232
%ifarch ppc64
%global optflags %{optflags} -fno-strict-aliasing
%endif
%configure \
%ifarch s390 s390x sparc64 sparcv9
    --disable-jit \
    --disable-pcre2grep-jit \
%else
    --enable-jit \
    --enable-pcre2grep-jit \
%endif
    --disable-bsr-anycrlf \
    --disable-coverage \
    --disable-ebcdic \
    --disable-never-backslash-C \
    --enable-newline-is-lf \
    --enable-pcre2-8 \
    --enable-pcre2-16 \
    --enable-pcre2-32 \
    --disable-pcre2test-libedit \
    --enable-pcre2test-libreadline \
    --disable-pcre2grep-libbz2 \
    --disable-pcre2grep-libz \
    --disable-rebuild-chartables \
    --enable-shared \
    --enable-stack-for-recursion \
    --enable-static \
    --enable-unicode \
    --disable-valgrind
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
# Get rid of unneeded *.la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
# These are handled by %%doc in %%files
rm -rf $RPM_BUILD_ROOT%{_docdir}/pcre2

%check
make %{?_smp_mflags} check VERBOSE=yes

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%{_libdir}/*.so.*
%{!?_licensedir:%global license %%doc}
%license COPYING LICENCE
%doc AUTHORS ChangeLog NEWS README

%files devel
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*.h
%{_mandir}/man1/pcre2-config.*
%{_mandir}/man3/*
%{_bindir}/pcre2-config
%doc doc/*.txt doc/html
%doc HACKING ./src/pcre2demo.c

%files static
%{_libdir}/*.a
%{!?_licensedir:%global license %%doc}
%license COPYING LICENCE

%files tools
%{_bindir}/pcre2grep
%{_bindir}/pcre2test
%{_mandir}/man1/pcre2grep.*
%{_mandir}/man1/pcre2test.*

%changelog
* Thu Feb 11 2016 Petr Pisar <ppisar@redhat.com> - 10.21-2
- Report unmatched closing parantheses properly
- Fix pcre2test for expressions with a callout inside a look-behind assertion
  (upstream bug #1783)
- Fix workspace overflow for (*ACCEPT) with deeply nested parentheses
  (upstream bug #1791)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 10.21-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 12 2016 Petr Pisar <ppisar@redhat.com> - 10.21-1
- 10.21 bump

* Wed Jan 06 2016 Petr Pisar <ppisar@redhat.com> - 10.21-0.2.RC1
- Adapt a test to French locale on RHEL

* Tue Jan 05 2016 Petr Pisar <ppisar@redhat.com> - 10.21-0.1.RC1
- 10.21-RC1 bump

* Mon Oct 26 2015 Petr Pisar <ppisar@redhat.com> - 10.20-3
- Fix compiling patterns with PCRE2_NO_AUTO_CAPTURE (upstream bug #1704)

* Mon Oct 12 2015 Petr Pisar <ppisar@redhat.com> - 10.20-2
- Fix compiling classes with a negative escape and a property escape
  (upstream bug #1697)
- Fix integer overflow for patterns whose minimum matching length is large
  (upstream bug #1699)

* Fri Jul 03 2015 Petr Pisar <ppisar@redhat.com> - 10.20-1
- 10.20 bump

* Fri Jun 19 2015 Petr Pisar <ppisar@redhat.com> - 10.20-0.1.RC1
- 10.20-RC1 bump
- Replace dependency on glibc-headers with gcc (bug #1230479)
- Preserve soname

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 10.10-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri May 29 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 10.10-3
- fixed Release field

* Fri May 29 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 10.10-2.1
- Backport fix for AArch64

* Tue May 05 2015 Petr Pisar <ppisar@redhat.com> - 10.10-2
- Package pcre2demo.c as a documentation for pcre2-devel

* Fri Mar 13 2015 Petr Pisar <ppisar@redhat.com> - 10.10-1
- PCRE2 library packaged

