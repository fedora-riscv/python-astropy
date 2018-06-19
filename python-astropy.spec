# Works with system erfa
%bcond_without system_erfa

# EPEL has older wcslib
%if 0%{?fedora} 
%bcond_without system_wcslib
%else
%bcond_with system_wcslib
%endif

%global srcname astropy

Name: python-astropy
Version: 3.0.3
Release: 2%{?dist}
Summary: A Community Python Library for Astronomy
License: BSD

URL: http://astropy.org
Source0: https://pypi.io/packages/source/a/astropy/astropy-%{version}.tar.gz
Source1: astropy-README.dist
Source2: astropy-ply.py
Patch0: python-astropy-system-configobj.patch
Patch1: python-astropy-system-six.patch
# Disable known failing tests, taken from Debian
# https://salsa.debian.org/debian-astro-team/astropy/blob/3b20ea052ab8bd0af505380eb4f0c357c901bb3b/debian/patches/Mark-all-known-test-failures-as-xfail.patch
Patch2: python-astropy-Mark-all-known-test-failures-as-xfail.patch

BuildRequires: git
BuildRequires: cfitsio-devel
BuildRequires: expat-devel
%if %{with system_erfa}
BuildRequires: erfa-devel
%else
Provides: bundled(erfa) = 1.3.0
%endif
%if %{with system_wcslib}
BuildRequires: wcslib-devel >= 5.14
%else
Provides: bundled(wcslib) = 5.16
%endif
BuildRequires: texlive-ucs

%description
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package -n python%{python3_pkgversion}-%{srcname}
Summary: A Community Python Library for Astronomy
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-setuptools
BuildRequires: python%{python3_pkgversion}-numpy
BuildRequires: python%{python3_pkgversion}-Cython
BuildRequires: python%{python3_pkgversion}-pytest
BuildRequires: python%{python3_pkgversion}-pytest-astropy
BuildRequires: python%{python3_pkgversion}-six
BuildRequires: python%{python3_pkgversion}-ply
BuildRequires: python%{python3_pkgversion}-scipy
BuildRequires: python%{python3_pkgversion}-h5py
BuildRequires: python%{python3_pkgversion}-sphinx graphviz
BuildRequires: python%{python3_pkgversion}-matplotlib
BuildRequires: python%{python3_pkgversion}-configobj
BuildRequires: python%{python3_pkgversion}-pandas
BuildRequires: python%{python3_pkgversion}-PyYAML

Requires: python%{python3_pkgversion}-numpy
Requires: python%{python3_pkgversion}-configobj
Requires: python%{python3_pkgversion}-pytest
Requires: python%{python3_pkgversion}-six
Requires: python%{python3_pkgversion}-ply
# Optionals
Requires: python%{python3_pkgversion}-scipy
Requires: python%{python3_pkgversion}-h5py
Requires: python%{python3_pkgversion}-PyYAML
Requires: /usr/bin/xmllint

%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}
Provides: bundled(jquery) = 1.11

# wcsaxes has been merged into astropy, therefore we obsolete and provide
# the old python3-wcsaxes package here
Provides:  python%{python3_pkgversion}-wcsaxes = %{version}-%{release}
Obsoletes: python%{python3_pkgversion}-wcsaxes < 0.9-9

%description -n python%{python3_pkgversion}-%{srcname}
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package -n python%{python3_pkgversion}-%{srcname}-doc
Summary: Documentation for %{name}, includes full API docs
# Disabled for the moment to avoid name collision
# of generated names between arches
# BuildArch: noarch
%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}-doc}

# wcsaxes has been merged into astropy, therefore we obsolete and provide
# the old python3-wcsaxes-doc package here
Provides:  python%{python3_pkgversion}-wcsaxes-doc = %{version}-%{release}
Obsoletes: python%{python3_pkgversion}-wcsaxes-doc < 0.9-9

%description -n python%{python3_pkgversion}-%{srcname}-doc
This package contains the full API documentation for %{name}.


%package -n %{srcname}-tools
Summary: Astropy utility tools
BuildArch: noarch
%if 0%{?fedora}
Requires: python%{python3_pkgversion}-%{srcname} = %{version}-%{release}
Obsoletes: pyfits-tools < 3.3-6
Provides: pyfits-tools = %{version}-%{release}
%else
Requires: python-%{srcname} = %{version}-%{release}
%endif


%description -n %{srcname}-tools
Utilities provided by Astropy
 
%prep
%setup -qn %{srcname}-%{version}
cp %{SOURCE1} README.dist
# Required to support wcslib 4.5
find -name wcsconfig.h -delete
rm -rf astropy*egg-info
# Use system configobj
%patch0 -p1
## Use system six
%patch1 -p1
# Use system ply
cp %{SOURCE2} astropy/extern/ply.py
# Mark known test failures as xfail
%patch2 -p1

# Remove expat, erfa, cfitsio and wcslib
rm -rf cextern/cfitsio
%if %{with system_erfa}
rm -rf cextern/erfa
%endif
rm -rf cextern/expat
%if %{with system_wcslib}
rm -rf cextern/wcslib
%endif

echo "[build]" >> setup.cfg
#echo "use_system_libraries=1" >> setup.cfg
echo "use_system_cfitsio=1" >> setup.cfg
%if %{with system_erfa}
echo "use_system_erfa=1" >> setup.cfg
%endif
echo "use_system_expat=1" >> setup.cfg
%if %{with system_wcslib}
echo "use_system_wcslib=1" >> setup.cfg
%endif


%build
%global py_setup_args --offline
# Use cairo backend due to https://bugzilla.redhat.com/show_bug.cgi?id=1394975
export MPLBACKEND=cairo
%{py3_build}
%{__python3} setup.py build_sphinx --offline
rm -f docs/_build/html/.buildinfo

%install
%{py3_install}

find %{buildroot} -name "*.so" | xargs chmod 755

%check
# Tests on s390x tend to stuck (already for scipy used by astropy)
%ifnarch s390x
pushd %{buildroot}/%{python3_sitearch}
py.test-%{python3_version} -k "not test_write_read_roundtrip" astropy
# Remove spurious test relict
rm -fr .pytest_cache
popd
%endif # ifnarch s390x
 

%files -n %{srcname}-tools
%{_bindir}/*

%files -n python%{python3_pkgversion}-%{srcname}
%doc README.rst README.dist
%license LICENSE.rst
%{python3_sitearch}/*

%files -n python%{python3_pkgversion}-%{srcname}-doc
%doc README.rst README.dist docs/_build/html
%license LICENSE.rst

%changelog
* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 3.0.3-2
- Rebuilt for Python 3.7

* Tue Jun 05 2018 Sergio Pascual <sergiopr@fedoraproject.org> - 3.0.3-1
- New release (3.0.3)

* Sat May 26 2018 Christian Dersch <lupinix@mailbox.org> - 3.0.2-1
- new version

* Sat Mar 17 2018 Christian Dersch <lupinix@mailbox.org> - 3.0.1-1
- new version
- cleaned up excluded tests, adapted patch from Debian for known failures
- removed Python 2 bits (in new package python2-astropy), astropy moved to
  Python 3 only

* Wed Mar 14 2018 Christian Dersch <lupinix@mailbox.org> - 2.0.5-1
- new version
- enabled fixed tests

* Fri Feb 23 2018 Christian Dersch <lupinix@mailbox.org> - 2.0.4-3
- rebuilt for cfitsio 3.420 (so version bump)

* Wed Feb 14 2018 Christian Dersch <lupinix@mailbox.org> - 2.0.4-2
- Provide and Obsolete python-wcsaxes, which has been merged into astropy

* Tue Feb 13 2018 Christian Dersch <lupinix@mailbox.org> - 2.0.4-1
- update to bugfix release 2.0.4
- fixes FTBFS on rawhide (due to fixes for newer numpy etc.)
- disabled tests on s390x as they hang sometimes (same as with scipy)
- removed python-astropy-fix-hdf5-test.patch (applied upstream)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Oct 09 2017 Sergio Pascual <sergiopr@fedoraproject.org> - 2.0.2-2
- Use system erfa

* Sun Oct 08 2017 Christian Dersch <lupinix@mailbox.org> - 2.0.2-1
- new version

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 01 2017 Christian Dersch <lupinix@mailbox.org> - 1.3.3-1
- new version

* Sun Apr 02 2017 Christian Dersch <lupinix@mailbox.org> - 1.3.2-1
- new version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 5 2017 Orion Poplawski <orion@cora.nwra.com> - 1.3-1
- Update to 1.3

* Wed Dec 21 2016 Orion Poplawski <orion@cora.nwra.com> - 1.3-0.1.rc1
- Update to 1.3rc1

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 1.2.1-6
- Rebuild for Python 3.6

* Mon Nov 21 2016 Orion Poplawski <orion@cora.nwra.com> - 1.2.1-5
- Use bundled erfa and wcslib where necessary (bug #1396601)
- Specify scipy version requirements
- Use cairo matplotlib backend due to ppc64 segfault
- Add BR on pandas for tests

* Sun Nov 06 2016 Björn Esser <fedora@besser82.io> - 1.2.1-4
- Rebuilt for ppc64

* Fri Sep 30 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.2.1-3
- Fix wrong provides of python3-astropy in python2-astropy (bz #1380135)

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Jul 15 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.2.1-1
- New upstream (1.2.1)

* Thu Apr 14 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.1.2-1
- New upstream (1.1.2)
- Uses wcslib 5

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 11 2016 Orion Poplawski <orion@cora.nwra.com> - 1.1.1-2
- Modernize spec
- Prepare for python3 in EPEL

* Sun Jan 10 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.1.1-1
- New upstream (1.1.1)

* Wed Jan 06 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.1-1.post2
- New upstream (1.1.post2)

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Fri Nov 06 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.6-2
- Enabled again tests that failed with numpy 1.10

* Wed Oct 28 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.6-1
- New upstream (1.0.6), with better support of numpy 1.10

* Fri Oct 09 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.5-2
- Fixes test problem https://github.com/astropy/astropy/issues/4226

* Tue Oct 06 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.5-1
- New upstream (1.0.5)

* Mon Sep 14 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.4-2
- Disable some tests that fail with numpy 1.10

* Thu Sep 03 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.4-1
- New upstream (1.0.4)

* Tue Jun 30 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.3-4
- Reenable tests
- Handle changes regarding python3 and pyfits-tools in fedora >= 22

* Mon Jun 29 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.3-3
- Obsolete pyfits-tools (fixes bz #1236562)
- astropy-tools requires python3

* Tue Jun 16 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.3-1
- New upstream (1.0.3), with 2015-06-30 leap second

* Tue Apr 21 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0.2-1
- New upstream (1.0.2)

* Thu Feb 19 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 1.0-1
- New upstream (1.0)

* Thu Jan 22 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.4-1
- New upstream (0.4.4)

* Fri Jan 16 2015 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.3-1
- New upstream (0.4.3)

* Tue Dec 09 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.2-5
- Disable tests for the moment

* Tue Dec 09 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.2-4
- Update patch for bug 2516

* Mon Dec 08 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.2-3
- Mark problematic tests as xfail via patch

* Fri Dec 05 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.2-2
- Fix to use configobj 5
- Patches reorganized

* Thu Sep 25 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.2-1
- New upstream (0.4.2)

* Mon Sep 01 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.4.1-1
- New upstream (0.4.1)
- Unbundling patches modified
- No checks for the moment

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Orion Poplawski <orion@cora.nwra.com> - 0.3.2-5
- Rebuild for Python 3.4

* Thu May 22 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.2-4
- Build with wcslib 4.23
- Skip test, bug 2171

* Thu May 22 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.2-3
- Astropy bundles jquery
- Unbundle plpy

* Thu May 22 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.2-2
- Add missing patches

* Mon May 19 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.2-1
- New upstream (0.3.2)
- Enable checks
- Patch to fix upstream bug 2171
- Disable problematic test (upstream 2516)

* Wed May 14 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 0.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Tue Mar 25 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.1-2
- Disable checks until https://github.com/astropy/astropy/issues/2171 is fixed
- Patch to fix https://github.com/astropy/astropy/pull/2223

* Wed Mar 05 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3.1-1
- New upstream version (0.3.1)
- Remove require python(3)-matplotlib-qt4 (bug #1030396 fixed)
- Run the tests on the installed files
- Add patch to run with six 1.5.x

* Mon Jan 27 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-7
- Add missing requires python3-six

* Sat Jan 18 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-6
- Do not exclude hidden file, it breaks tests

* Thu Jan 16 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-5
- Remove split -devel subpackage, it does not make much sense

* Fri Jan 10 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-4
- Disable noarch for doc subpackages to avoid name colision

* Fri Jan 10 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-3
- Enable HDF5 version check (fixed in h5py)
- Patch for failing test with wcslib 4.20
- Require python(3)-matplotlib-qt4 due to bug #1030396

* Sun Jan 05 2014 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-2
- Disable HDF5 version check

* Mon Nov 25 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-1
- New upstream (0.3)

* Tue Nov 19 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-0.3.rc1
- New upstream, first release candidate Testing 0.3rc1

* Wed Nov 06 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-0.2.b1
- Split utility scripts in subpackage

* Tue Nov 05 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.3-0.1.b1
- Testing 0.3 (0.3b1)

* Mon Oct 28 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.2.5-1
- New upstream version (0.2.5)

* Tue Oct 22 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.2.4-4
- Split header files into devel subpackages

* Mon Oct 21 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.2.4-3
- Disable tests in Rawhide

* Thu Oct 10 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.2.4-3
- Add a patch to build with cfitsio 3.35

* Wed Oct 02 2013 Sergio Pascual <sergiopr@fedoraproject.org> - 0.2.4-1
- Initial spec
