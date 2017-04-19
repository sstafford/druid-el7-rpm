%define __jar_repack 0
%define _unpackaged_files_terminate_build 0
%define _missing_doc_files_terminate_build 0
%define debug_package %{nil}
%define _user        druid
%define _group       druid
%define _prefix      /opt
%define _install_dir %{_prefix}/%{name}
%define _conf_dir    %{_sysconfdir}/%{name}
%define _log_dir     %{_var}/log/%{name}
%define _data_dir    %{_sharedstatedir}/%{name}
%define _pid_dir     %{_var}/run/%{name}

Name: druid
Version: %{version}
Release: %{build_number}
Summary: Druid is a time series database for metrics data collection.
Group: Applications/Internet
License: GPL
URL: http://http://druid.io/
Source0: %{name}-%{version}-bin.tar.gz
#Source1: %{name}.sysconfig
Source2: %{name}-broker.service
Source3: %{name}-coordinator.service
Source4: %{name}-historical.service
Source5: %{name}-manager.service
Source6: %{name}-overlord.service

BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Prefix: %{_prefix}
Provides: %{name}
AutoReqProv: no
BuildRequires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# ============================== DESCRIPTION ==================================
%description
An open-source, real-time data store designed to power interactive applications at scale.

# ================================== PRE ======================================
%pre
getent group %{_group} >/dev/null || groupadd -r %{_group}
getent passwd %{_user} >/dev/null || \
    useradd -r -g %{_user} -d %{_data_dir} -s /sbin/nologin \
    -c "Druid Server Service" %{_user}
exit 0

# ================================= POST ======================================
%post
%systemd_post druid-broker.service
%systemd_post druid-coordinator.service
%systemd_post druid-historical.service
%systemd_post druid-manager.service
%systemd_post druid-overlord.service


# ================================= PREUN =====================================
%preun
%systemd_preun druid-broker.service
%systemd_preun druid-coordinator.service
%systemd_preun druid-historical.service
%systemd_preun druid-manager.service
%systemd_preun druid-overlord.service


# ================================= POSTUN ====================================
%postun
# When the last version of a package is erased, $1 is 0
# Otherwise it's an upgrade and we need to restart the service
if [ $1 -ge 1 ]; then
    /usr/bin/systemctl restart zookeeper.service
fi
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :


# ================================= PREP ======================================
%prep
%setup -q -n %{name}-%{version}

# ================================= BUILD =====================================
%build


# ================================ INSTALL ====================================
%install

# Create empty directories for run-time data
mkdir -p %{buildroot}%{_log_dir}
mkdir -p %{buildroot}%{_data_dir}
mkdir -p %{buildroot}%{_pid_dir}

# Create the root install location
mkdir -p %{buildroot}%{_install_dir}/

# install druid libraries
mkdir -p %{buildroot}%{_install_dir}/lib
%{__cp} -Rv lib/* %{buildroot}%{_install_dir}/lib

# install druid management scripts
mkdir -p %{buildroot}%{_install_dir}/bin
%{__cp} -Rv bin/* %{buildroot}%{_install_dir}/bin

# install druid extensions
mkdir -p %{buildroot}%{_install_dir}/extensions
%{__cp} -Rv extensions/* %{buildroot}%{_install_dir}/extensions

# install druid configuration files
mkdir -p %{buildroot}%{_conf_dir}/
%{__cp} -Rv conf/druid/* %{buildroot}%{_conf_dir}
ln -sf %{_install_dir}/extensions %{buildroot}%{_conf_dir}/extensions

#install -p -D -m 644 %{S:1} %{buildroot}%{_conf_dir}/
mkdir -p %{buildroot}/etc/sysconfig/
echo "DRUID_LIB_DIR=%{_install_dir}/lib"  >> %{buildroot}/etc/sysconfig/%{name}
echo "DRUID_CONF_DIR=%{_conf_dir}" >> %{buildroot}/etc/sysconfig/%{name}
echo "DRUID_LOG_DIR=%{_log_dir}" >> %{buildroot}/etc/sysconfig/%{name}
echo "DRUID_PID_DIR=%{_pid_dir}" >> %{buildroot}/etc/sysconfig/%{name}

# Install the service scripts
mkdir -p %{buildroot}%{_unitdir}/
cat %{S:2} | sed 's#^ExecStart=.*#ExecStart=%{_install_dir}/bin/node.sh broker start#g' \
           | sed 's#^ExecStop=.*#ExecStop=%{_install_dir}/bin/node.sh broker stop#g' \
           > %{buildroot}%{_unitdir}/`basename %{S:2}`

cat %{S:3} | sed 's#^ExecStart=.*#ExecStart=%{_install_dir}/bin/node.sh coordinator start#g' \
           | sed 's#^ExecStop=.*#ExecStop=%{_install_dir}/bin/node.sh coordinator stop#g' \
           > %{buildroot}%{_unitdir}/`basename %{S:3}`

cat %{S:4} | sed 's#^ExecStart=.*#ExecStart=%{_install_dir}/bin/node.sh historical start#g' \
           | sed 's#^ExecStop=.*#ExecStop=%{_install_dir}/bin/node.sh historical stop#g' \
           > %{buildroot}%{_unitdir}/`basename %{S:4}`

cat %{S:5} | sed 's#^ExecStart=.*#ExecStart=%{_install_dir}/bin/node.sh middleManager start#g' \
           | sed 's#^ExecStop=.*#ExecStop=%{_install_dir}/bin/node.sh middleManager stop#g' \
           > %{buildroot}%{_unitdir}/`basename %{S:5}`

cat %{S:6} | sed 's#^ExecStart=.*#ExecStart=%{_install_dir}/bin/node.sh overlord start#g' \
           | sed 's#^ExecStop=.*#ExecStop=%{_install_dir}/bin/node.sh overlord stop#g' \
           > %{buildroot}%{_unitdir}/`basename %{S:6}`


# ================================= FILES =====================================
%files
%defattr(-,%{_user},%{_group},755)
%{_unitdir}/%{name}-broker.service
%{_unitdir}/%{name}-coordinator.service
%{_unitdir}/%{name}-historical.service
%{_unitdir}/%{name}-manager.service
%{_unitdir}/%{name}-overlord.service
/etc/sysconfig/%{name}

#%{_install_dir}
%{_pid_dir}

# Identify config files that should not be replaced during an RPM upgrade
%config(noreplace) %{_conf_dir}/*

# Assign user permissions
%attr(-,%{_user},%{_group}) %{_install_dir}
%attr(0755,%{_user},%{_group}) %dir %{_log_dir}
%attr(0700,%{_user},%{_group}) %dir %{_data_dir}
%attr(0700,%{_user},%{_group}) %dir %{_pid_dir}

# ================================= CLEAN =====================================
%clean
rm -rf %{buildroot}


# =============================== CHANGELOG ==================================
%changelog
* Mon Apr 17 2017 Shawn Stafford <shawn@staffco.org> 0.9.2-1
- Initial version
