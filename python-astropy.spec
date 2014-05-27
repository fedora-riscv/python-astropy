%global with_python3 1
%global upname astropy

Name: python-astropy
Version: 0.3.2
Release: 5%{?dist}
Summary: A Community Python Library for Astronomy
License: BSD

URL: http://astropy.org
Source0: http://pypi.python.org/packages/source/a/astropy/astropy-%{version}.tar.gz
Source1: astropy-README.dist
Patch0: python-astropy-system-wcslib.patch
Patch1: python-astropy-system-configobj.patch
Patch2: python-astropy-system-pytest.patch
Patch3: python-astropy-system-six.patch
# The fix works with 3.4 but no with 3.3.2
#Patch4: python-astropy-bug2171.patch
Patch4: python-astropy-skiptest2171.patch
Patch5: python-astropy-skiptest.patch
Patch6: python-astropy-system-ply.patch
Patch7: python-astropy-wcslib323.patch

BuildRequires: python2-devel python-setuptools numpy
BuildRequires: scipy h5py
BuildRequires: git Cython pytest python-six python-ply
BuildRequires: python-sphinx graphviz
BuildRequires: python-matplotlib
BuildRequires: python-configobj
BuildRequires: expat-devel
BuildRequires: cfitsio-devel
BuildRequires: wcslib-devel >= 4.23
BuildRequires: erfa-devel

Requires: numpy
Requires: python-configobj pytest python-six python-ply
# Optionals
Requires: scipy h5py
Requires: /usr/bin/xmllint

Provides: bundled(jquery) = 1.10

# we don't want to provide private python extension libs
%global __provides_exclude_from ^(%{python2_sitearch}|%{python3_sitearch})/.*\\.so$

%description
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package doc
Summary: Documentation for %{name}, includes full API docs
# Disabled for the moment to avoid name collision
# of generated names between arches
# BuildArch: noarch
 
%description doc
This package contains the full API documentation for %{name}.

%if 0%{?with_python3}
%package -n python3-%{upname}
Summary: A Community Python Library for Astronomy
BuildRequires: python3-devel python3-setuptools python3-numpy
BuildRequires: git python3-Cython python3-pytest python3-six python3-ply
BuildRequires: python3-scipy python3-h5py
BuildRequires: python3-sphinx graphviz
BuildRequires: python3-matplotlib
BuildRequires: python3-configobj
#
BuildRequires: expat-devel
BuildRequires: wcslib-devel >= 4.23
BuildRequires: erfa-devel
BuildRequires: cfitsio-devel
BuildRequires: python3-devel

Requires: python3-numpy
Requires: python3-configobj
Requires: python3-pytest
Requires: python3-six
Requires: python3-ply
# Optionals
Requires: python3-scipy python3-h5py
Requires: /usr/bin/xmllint

Provides: bundled(jquery) = 1.10

%description -n python3-%{upname}
The Astropy project is a common effort to develop a single core package 
for Astronomy.  Major packages such as PyFITS, PyWCS, vo, and asciitable 
already merged in, and many more components being worked on. In 
particular, we are developing imaging, photometric, and spectroscopic 
functionality, as well as frameworks for cosmology, unit handling, and 
coordinate transformations.

%package -n python3-%{upname}-doc
Summary: Documentation for %{name}, includes full API docs
# Disabled for the moment to avoid name collision
# of generated names between arches
# BuildArch: noarch
 
%description -n python3-%{upname}-doc
This package contains the full API documentation for %{name}.

%endif # with_python3

%package -n %{upname}-tools
Summary: Astropy utility tools
BuildArch: noarch
Requires: python-%{upname} = %{version}-%{release}

%description -n %{upname}-tools
Utilities provided by Astropy: 'volint' for validating a Virtual Observatory 
files, 'wcslint' for validating the WCS keywords in a FITS file.
 
%prep
%setup -qn %{upname}-%{version}
cp %{SOURCE1} README.dist
rm -rf astropy*egg-info

# Remove expat, erfa, cfitsio and wcslib
rm -rf cextern/expat
rm -rf cextern/erfa
rm -rf cextern/cfitsio
rm -rf cextern/wcslib
%patch0 -p1
# WCSLIB 4.23
%patch7 -p1

# Unbundle configobj
rm -rf astropy/extern/configobj*
%patch1 -p1

# Unbundle pytest
rm -rf astropy/extern/pytest*
%patch2 -p1

# Unbundle six
rm -rf astropy/extern/six.py*
%patch3 -p1

# Unbundle ply
rm -rf astropy/extern/ply*
%patch6 -p1

# https://github.com/astropy/astropy/issues/2171
%patch4 -p1
# https://github.com/astropy/astropy/issues/2516
%patch5 -p1

echo "[build]" >> setup.cfg
echo "use_system_expat=1" >> setup.cfg
echo "use_system_cfitsio=1" >> setup.cfg
echo "use_system_erfa=1" >> setup.cfg
echo "use_system_wcslib=1" >> setup.cfg

find -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python2}|'

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
find %{py3dir} -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
%endif # with_python3


%build
CFLAGS="%{optflags}" %{__python2} setup.py build 
%{__python2} setup.py build_sphinx
rm -f docs/_build/html/.buildinfo

%if 0%{?with_python3}
pushd %{py3dir}
CFLAGS="%{optflags}" %{__python3} setup.py build
# Not working, python3-sphinx bug
# https://bugzilla.redhat.com/show_bug.cgi?id=1014505
#%{__python3} setup.py build_sphinx
popd
# Copying the python2 docs for the moment
mkdir -p docs/_build3/
cp -r docs/_build/html docs/_build3/
%endif # with_python3

%install

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot}
popd
%endif # with_python3

%{__python2} setup.py install --skip-build --root %{buildroot}

find %{buildroot} -name "*.so" | xargs chmod 755

# install_scripts target seems to overwrite the shebang of the scripts
# it doesn't matter the the order of the installs
# fixing it here
for i in %{buildroot}/usr/bin/*; do 
 sed -i '1s|^#!%{__python3}|#!%{__python2}|' $i
done

%check
pushd %{buildroot}/%{python2_sitearch}
py.test-%{python2_version}  astropy
popd

%if 0%{?with_python3}
pushd %{buildroot}/%{python3_sitearch}
py.test-%{python3_version}  astropy
popd
%endif # with_python3
 
%files
%doc README.rst README.dist licenses/LICENSE.rst
%{python2_sitearch}/*

%files -n %{upname}-tools
%{_bindir}/*
# These two are provided by pyfits
%exclude %{_bindir}/fitsdiff
%exclude %{_bindir}/fitscheck

%files doc
%doc README.rst README.dist licenses/LICENSE.rst docs/_build/html

%if 0%{?with_python3}
%files -n python3-%{upname}
%doc README.rst licenses/LICENSE.rst README.dist
%{python3_sitearch}/*

%files -n python3-%{upname}-doc
%doc README.rst README.dist licenses/LICENSE.rst docs/_build3/html

%endif # with_python3

%changelog
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
- Disable proplematic test (2516)

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
