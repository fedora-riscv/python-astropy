%if 0%{?fedora}
%global with_python3 1
%endif
%global srcname astropy

Name: python-astropy
Version: 1.1.1
Release: 1%{?dist}
Summary: A Community Python Library for Astronomy
License: BSD

URL: http://astropy.org
Source0: http://pypi.python.org/packages/source/a/astropy/astropy-%{version}.tar.gz
Source1: astropy-README.dist
Source2: astropy-ply.py
# Repackaged documentation from
# https://kojipkgs.fedoraproject.org//packages/python-astropy/1.1.1/1.fc23/x86_64/python-astropy-doc-1.1.1-1.fc23.x86_64.rpm
# sphinx is too old in EL7.2 to build it (need 1.2.1)
Source3: python-astropy-doc-%{version}.tar.xz
Patch0: python-astropy-system-configobj.patch
Patch1: python-astropy-system-pytest.patch
Patch2: python-astropy-system-six.patch

BuildRequires: python2-devel python-setuptools numpy
BuildRequires: scipy h5py
BuildRequires: git Cython pytest python-six python-ply
BuildRequires: python-sphinx graphviz
BuildRequires: python-matplotlib
BuildRequires: python-configobj
BuildRequires: expat-devel
BuildRequires: cfitsio-devel
BuildRequires: wcslib-devel >= 4.25
BuildRequires: erfa-devel
# 
BuildRequires: texlive-ucs

BuildRequires: PyYAML

Requires: numpy
Requires: python-configobj pytest python-six python-ply
# Optionals
Requires: scipy h5py
Requires: PyYAML
Requires: /usr/bin/xmllint

Provides: bundled(jquery) = 1.11
Provides: python2-%{srcname} = %{version}-%{release}

%description
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package doc
Provides: python2-%{srcname}-doc = %{version}-%{release}
Summary: Documentation for %{name}, includes full API docs
# Disabled for the moment to avoid name collision
# of generated names between arches
# BuildArch: noarch
 
%description doc
This package contains the full API documentation for %{name}.

%if 0%{?with_python3}
%package -n python3-%{srcname}
Summary: A Community Python Library for Astronomy
BuildRequires: python3-devel python3-setuptools python3-numpy
BuildRequires: git python3-Cython python3-pytest python3-six python3-ply
BuildRequires: python3-scipy python3-h5py
BuildRequires: python3-sphinx graphviz
BuildRequires: python3-matplotlib
BuildRequires: python3-configobj
#
BuildRequires: expat-devel
BuildRequires: wcslib-devel >= 4.25
BuildRequires: erfa-devel
BuildRequires: cfitsio-devel
BuildRequires: python3-devel
#
BuildRequires: texlive-ucs
BuildRequires: python3-PyYAML

Requires: python3-numpy
Requires: python3-configobj
Requires: python3-pytest
Requires: python3-six
Requires: python3-ply
# Optionals
Requires: python3-scipy python3-h5py
Requires: python3-PyYAML
Requires: /usr/bin/xmllint

Provides: bundled(jquery) = 1.11

%description -n python3-%{srcname}
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package -n python3-%{srcname}-doc
Summary: Documentation for %{name}, includes full API docs
# Disabled for the moment to avoid name collision
# of generated names between arches
# BuildArch: noarch
 
%description -n python3-%{srcname}-doc
This package contains the full API documentation for %{name}.

%endif # with_python3

%package -n %{srcname}-tools
Summary: Astropy utility tools
BuildArch: noarch
%if 0%{?fedora} >= 22
Requires: python3-%{srcname} = %{version}-%{release}
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
# Use system pytest
%patch1 -p1
%patch2 -p1
# Use system ply
cp %{SOURCE2} astropy/extern/ply.py

# Remove expat, erfa, cfitsio and wcslib
rm -rf cextern/expat
rm -rf cextern/erfa
rm -rf cextern/cfitsio
rm -rf cextern/wcslib

echo "[build]" >> setup.cfg
echo "use_system_libraries=1" >> setup.cfg

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif # with_python3


%build
CFLAGS="%{optflags}" %{__python2} setup.py build --offline
# Requires sphinx 1.2.1
%if 0%{?fedora}
%{__python2} setup.py build_sphinx --offline
%endif
rm -f docs/_build/html/.buildinfo

%if 0%{?with_python3}
pushd %{py3dir}
CFLAGS="%{optflags}" %{__python3} setup.py build --offline
#%{__python3} setup.py build_sphinx --offline
#rm -f docs/_build/html/.buildinfo
popd
mkdir -p docs/_build3/
#cp -r %{py3dir}/docs/_build/html docs/_build3/
%endif # with_python3

%install
%if 0%{?fedora} >= 22

%{__python2} setup.py install --skip-build --root %{buildroot} --offline

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot} --offline
popd
%endif # with_python3

%else

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot} --offline
popd
%endif # with_python3

%{__python2} setup.py install --skip-build --root %{buildroot} --offline

%endif # fedora >= 22


find %{buildroot} -name "*.so" | xargs chmod 755

# Unpack docs
mkdir -p docs/_build
tar xf %SOURCE3 -C docs/_build

%check
pushd %{buildroot}/%{python2_sitearch}
py.test-%{python2_version} -k "not test_web_profile" astropy
popd

%if 0%{?with_python3}
pushd %{buildroot}/%{python3_sitearch}
py.test-%{python3_version} -k "not test_web_profile" astropy
popd
%endif # with_python3
 
%files
%doc README.rst README.dist
%license licenses/LICENSE.rst
%{python2_sitearch}/*

%files -n %{srcname}-tools
%{_bindir}/*
%if 0%{?fedora} < 22
# These two are provided by pyfits
%exclude %{_bindir}/fitsdiff
%exclude %{_bindir}/fitscheck
%endif # fedora < 22

%files doc
%doc README.rst README.dist docs/_build/html
%license licenses/LICENSE.rst

%if 0%{?with_python3}
%files -n python3-%{srcname}
%doc README.rst README.dist
%license licenses/LICENSE.rst
%{python3_sitearch}/*

%files -n python3-%{srcname}-doc
%doc README.rst README.dist docs/_build/html
%license licenses/LICENSE.rst

%endif # with_python3

%changelog
* Sun Jan 10 2016 Sergio Pascual <sergiopr@fedoraproject.org> - 1.1.1-1
- New upstream (1.1.1)

* Wed Oct 28 2015 Orion Poplawski <orion@cora.nwra.com> - 1.0.5-1
- New upstream (1.0.5)
- Update pytest23 patch

* Wed Jul 15 2015 Orion Poplawski <orion@cora.nwra.com> - 1.0.3-4.1
- Handle changes regarding python3 and pyfits-tools in fedora >= 22

* Mon Jul 13 2015 Orion Poplawski <orion@cora.nwra.com> - 1.0.3-4
- Make python3 default only in F22+
- Add patch to support pytest 2.3.5 in EL7.
- Do not apply system six patch on EL for now, too old.
- Do not build on ppc64 - tests fail

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
