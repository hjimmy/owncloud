#
# spec file for package owncloud
#
# Copyright (c) 2012 ownCloud, Inc.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes, issues or comments via http://github.com/owncloud/
#

#
%if 0%{?suse_version}
%define apache_serverroot /srv/www/htdocs
%define apache_confdir /etc/apache2/conf.d
%define apache_user wwwrun
%define apache_group www
%else
%if 0%{?fedora_version} || 0%{?rhel_version} || 0%{?centos_version}
%define apache_serverroot /var/www/html
%define apache_confdir /etc/httpd/conf.d
%define apache_user apache
%define apache_group apache
%define __jar_repack 0
%else
%define apache_serverroot /var/www
%define apache_confdir /etc/httpd/conf.d
%define apache_user www
%define apache_group www
%endif
%endif

Name:           owncloud

## define prerelease %nil, if this is *not* a prerelease.
%define prerelease %nil
%define base_version 6.0.9
%define tar_version %{base_version}%{prerelease}

%if 0%{?centos_version} == 600 || 0%{?fedora_version} || "%{prerelease}" == ""
# For beta and rc versions we use the ~ notation, as documented in
# http://en.opensuse.org/openSUSE:Package_naming_guidelines
Version:       	%{base_version}
%if "%{prerelease}" == ""
Release:        1.1
%else
Release:       	0.1.1.%{prerelease}
%endif
%else
Version:       	%{base_version}~%{prerelease}
Release:        1.1
%endif

Source0:        http://download.owncloud.org/community/testing/owncloud-%{tar_version}.tar.bz2
Source1:        apache_secure_data
Source2:        README
Source3:        README.SELinux
Url:            http://www.owncloud.org
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Summary:        The ownCloud Server - Private file sync and share server
License:        AGPL-3.0 and MIT
Group:          Productivity/Networking/Web/Utilities

%if 0%{?fedora_version} || 0%{?rhel_version} >= 6 || 0%{?centos_version} >= 6
Requires:       httpd sqlite php php-json php-mbstring php-process php-pear-Net-Curl php-gd php-pear-MDB2-Driver-mysqli php-xml php-zip
BuildRequires:  httpd
%endif

%if 0%{?rhel_version} == 5 || 0%{?centos_version} == 5
Requires:       httpd sqlite php53 >= 5.3.3 php53-json php53-mbstring php53-process php53-pear-Net-Curl php53-gd php53-pear-MDB2-Driver-mysqli php53-xml php53-zip
%endif

%if 0%{?suse_version}
BuildRequires:	fdupes
# Reqires: php5-zlib -- You must let rpm find the library dependencies by itself.
%if 0%{?suse_version} != 1110
# For all SUSEs except SLES 11
Requires:       apache2 apache2-mod_php5 php5 >= 5.3.3 sqlite3 php5-sqlite php5-mbstring php5-zip php5-json php5-posix curl php5-curl php5-gd php5-ctype php5-xmlreader php5-xmlwriter php5-pear php5-iconv
BuildRequires:  apache2 unzip
%else
# SLES 11 requires
# require mysql directly for SLES 11
Requires:       apache2 apache2-mod_php53 php53 >= 5.3.3 mysql php53-sqlite php53-mbstring php53-zip php53-json php53-posix curl php53-curl php53-gd php53-ctype php53-xmlreader php53-xmlwriter php53-pear php53-iconv
BuildRequires:  apache2 unzip
%endif
%endif

Requires:       ntp curl %{name}-3rdparty
%if 0%{?suse_version}
# SUSE does not include the fileinfo module in php-common.
Requires:       php-fileinfo
%if 0%{?suse_version} != 1110
Recommends:     php5-mysql mysql php5-imagick libreoffice-writer
%else
Recommends:     php53-mysql mysql php53-imagick
%endif
%else
Requires:       mysql
%endif

%description
ownCloud Server provides you a private file sync and share
cloud. Host this server to easily sync business or private documents
across all your devices, and share those documents with other users of
your ownCloud server on their devices.

ownCloud - Your Cloud, Your Data, Your Way!  www.owncloud.org


%package 3rdparty
License:      PHP-3.01
Group:        Development/Libraries/PHP
Summary:      3rdparty libraries for ownCloud
Requires:     %{name} = %{version}
%description 3rdparty
3rdparty libraries needed for running ownCloud. 
Contained in separate package due to different source code licenses.


%prep
%setup -q -n owncloud
cp %{SOURCE2} .
cp %{SOURCE3} .
#%%patch0 -p0

%build

%install
# no server side java code contained, alarm is false
export NO_BRP_CHECK_BYTECODE_VERSION=true
idir=$RPM_BUILD_ROOT/%{apache_serverroot}/%{name}
mkdir -p $idir
mkdir -p $idir/data
cp -aRf * $idir
cp -aRf .htaccess $idir
# $idir/l10n to disappear in future
rm -f $idir/l10n/l10n.pl

# create the AllowOverride directive
install -p -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT/%{apache_confdir}/owncloud.conf
ocpath="%{apache_serverroot}/%{name}"
sed -i -e"s|DATAPATH|${ocpath}|g" $RPM_BUILD_ROOT/%{apache_confdir}/owncloud.conf

# clean sources of odfviewer
rm -rf ${idir}/apps/files_odfviewer/src
rm -rf ${idir}/3rdparty/phpass/c
rm -rf ${idir}/3rdparty/phpdocx/pdf/lib/ttf2ufm
rm -rf ${idir}/3rdparty/phpdocx/pdf/tcpdf/fonts/utils/ttf2ufm
rm -rf ${idir}/3rdparty/phpdocx/pdf/tcpdf/fonts/utils/pfm2afm

%if 0%{?suse_version}
# link duplicate doc files
%fdupes $RPM_BUILD_ROOT/%{apache_serverroot}/%{name}
%endif

%post
%if 0%{?suse_version}
## If we stopped apache in pre section, we now should restart. -- but *ONLY* then!
## Maybe delegate that task to occ upgrade? They also need to handle this, somehow.
# rcapache2 start
%endif

# relabel data directory for SELinux to allow ownCloud write access on redhat platforms
%if 0%{?fedora_version} || 0%{?rhel_version} || 0%{?centos_version}
if [ -x /usr/sbin/sestatus ] ; then \
  sestatus | grep -E '^(SELinux status|Current).*(enforcing|permissive)' > /dev/null && { 
    semanage fcontext -a -t httpd_sys_rw_content_t '/var/www/html/owncloud/data'
    restorecon '/var/www/html/owncloud/data'
    semanage fcontext -a -t httpd_sys_rw_content_t '/var/www/html/owncloud/config'
    restorecon '/var/www/html/owncloud/config'
    semanage fcontext -a -t httpd_sys_rw_content_t '/var/www/html/owncloud/apps'
    restorecon '/var/www/html/owncloud/apps'
  }
fi
true
%endif

%postun
# remove SELinux ownCloud label if not updating
[ $1 -eq 0 ] || exit 0
%if 0%{?fedora_version} || 0%{?rhel_version} || 0%{?centos_version}
if [ -x /usr/sbin/sestatus ] ; then \
  sestatus | grep -E '^(SELinux status|Current).*(enforcing|permissive)' > /dev/null && { 
    semanage fcontext -l | grep '/var/www/%{name}/data' && {
      semanage fcontext -d -t httpd_sys_rw_content_t '/var/www/html/%{name}/data'
      restorecon '/var/www/html/%{name}/data'
    }
    semanage fcontext -l | grep '/var/www/html/%{name}/config' && {
      semanage fcontext -d -t httpd_sys_rw_content_t '/var/www/html/%{name}/config'
      restorecon '/var/www/html/%{name}/config'
    }
    semanage fcontext -l | grep '/var/www/html/%{name}/apps' && {
      semanage fcontext -d -t httpd_sys_rw_content_t '/var/www/html/%{name}/apps'
      restorecon '/var/www/html/%{name}/apps'
    }
  }
fi
true
%endif

%pre
%if 0%{?suse_version}
# avoid fatal php errors, while we are changing files
# rcapache2 stop
%endif

%clean
rm -rf "$RPM_BUILD_ROOT"

%files
%defattr(0640,root,%{apache_group},0750)
%exclude %{apache_serverroot}/%{name}/3rdparty/PEAR*
%exclude %{apache_serverroot}/%{name}/3rdparty/System.php
%exclude %{apache_serverroot}/%{name}/3rdparty/XML/Parser.php

%dir %{apache_serverroot}/%{name}
%{apache_serverroot}/%{name}/3rdparty
%doc %{apache_serverroot}/%{name}/AUTHORS
%doc %{apache_serverroot}/%{name}/COPYING-AGPL
%{apache_serverroot}/%{name}/core
%{apache_serverroot}/%{name}/db_structure.xml
%{apache_serverroot}/%{name}/index.php
%{apache_serverroot}/%{name}/lib
%{apache_serverroot}/%{name}/ocs
%{apache_serverroot}/%{name}/public.php
%doc %{apache_serverroot}/%{name}/README*
%{apache_serverroot}/%{name}/remote.php
%{apache_serverroot}/%{name}/search
%{apache_serverroot}/%{name}/settings
%{apache_serverroot}/%{name}/status.php
%{apache_serverroot}/%{name}/themes
%{apache_serverroot}/%{name}/cron.php
%{apache_serverroot}/%{name}/.htaccess
%{apache_serverroot}/%{name}/robots.txt
%{apache_serverroot}/%{name}/index.html
%{apache_serverroot}/%{name}/console.php
%{apache_serverroot}/%{name}/version.php

%defattr(0755,%{apache_user},%{apache_group},0770)
%{apache_serverroot}/%{name}/occ
%defattr(-,%{apache_user},%{apache_group},0770)
%{apache_serverroot}/%{name}/data
# config can be chown-ed to root:www after the initial DB config is done.
%dir %{apache_serverroot}/%{name}/config
%dir %{apache_serverroot}/%{name}/apps

%defattr(0640,root,%{apache_group},0750)
%{apache_serverroot}/%{name}/apps/*
%{apache_serverroot}/%{name}/config/*

%config %attr(0644,root,root) %{apache_confdir}/owncloud.conf

%doc README README.SELinux

%files 3rdparty
%defattr(0640,root,%{apache_group},0750)
%{apache_serverroot}/%{name}/3rdparty/PEAR/
%{apache_serverroot}/%{name}/3rdparty/PEAR.php
%{apache_serverroot}/%{name}/3rdparty/PEAR5.php
%{apache_serverroot}/%{name}/3rdparty/PEAR-LICENSE
%{apache_serverroot}/%{name}/3rdparty/System.php
%{apache_serverroot}/%{name}/3rdparty/XML/Parser.php

%changelog
* Fri Jul  3 2015 jnweiger@gmail.com
- Update to version 6.0.9
* Thu Jul  2 2015 jw@owncloud.com
- suse needs explicit requires to php-fileinfo
* Wed Jul  1 2015 jw@owncloud.com
- Update to version 6.0.9~RC1
* Wed Jun 24 2015 jw@owncloud.com
- Version 6.0.9~beta
* Fri Jun  5 2015 freitag@owncloud.com
  owncloud 6.0.8
  * Update to final tarball 6.0.8
  * Remove hacky Substring support for MSSQL#14499
  * unable to rename, file is not writable #14728
  * catch any whitespaces which might get written to the output buffer while... #14150
  * occ upgrade fail "Maximum execution time of 3600 seconds exceeded" #14156
* Tue Jun  2 2015 jw@owncloud.com
- Version 6.0.8~RC2
  New community:6.0:testing project, to keep community:6.0 clean.
* Wed Mar 11 2015 jw@owncloud.com
- version 6.0.7
* Mon Nov 10 2014 freitag@owncloud.com
- Update to version 6.0.6
  Oct 22. 2014
  - Fix finding old versions in special cases
  - Make versions and encryption aware of copy operations
  - Force loading encryption app in all needed cases
  - Better filesystem scanning error messages
  - LDAP wizard fixes
  - Add configuration switch to enable preview mimetypes
  - Create backup of all encryption keys before recovery
  - Add displayname for admins
  - Several security fixes
  - Lots of smaller improvements
* Thu Aug 28 2014 jnweiger@gmail.com
- make occ mode 755
  for https://github.com/owncloud/core/issues/10685
* Wed Aug 27 2014 jw@owncloud.com
- toplevel l10n is gone. Confirmed with Frank.
* Wed Aug 27 2014 juewei@localhost
  * Release  "6.0.5" Aug 26. 2014
  - Documentation improvements
  - fix anonymous upload if logged-in
  - Fix handling of special characters in group names
  - Fix downloading of big files in special situations
  - More consistent handling of debug mode
  - Fix sharing email notifications
  - Disabling upload button if upload is not possible
  - Fix detection of system wide mount points
  - Handle video viewer in sharing links correctly
  - Update encryption keys recursively if a folder was moved
  - Enable download button for public folders
  - Handle exceptions if file to too big for trash-bin correctly
  - Quota fixes
  - Avoid unnecessary writing to the DB when preferences are not changed
  - Disable download button if zip download is disabled
  - Fix searching for users in special situations
  - Mount-point handling fixes
  - Correctly handle storage stats for trash bin
  - Remove etag warning for trash bin
  - Hardened SFTP host verification
* Tue Aug 19 2014 jw@owncloud.com
- fixed copyright in specfile.
* Wed Jun 25 2014 freitag@owncloud.com
- Add alias entry to apache conf for debians, fix for ubu 14.04
* Tue Jun 24 2014 freitag@owncloud.com
  Release  "6.0.4" June 23. 2014
  - Several LDAP fixes and improvements
  - Add deprecated warning to load function
  - File scanner fixes
  - Heart beat fixes
  - Encryption fixes for some corner cases
  - Fix conflict dialog translations
  - Fix button text overflow
  - Fix search with Oracle
  - php upload errors are written to log
  - ocs status code fixes
  - Add PostgreSQL version warning
* Tue Apr 29 2014 freitag@owncloud.com
  Release  "6.0.3" April 29. 2014
  - Several security fixes. (Will be disclosed 2 weeks after the release)
  - Appframework extensions to improve the compatibility with 3rdparty apps
  - LDAP performance improvements
  - Fix updating of email adresses from LDAP
  - Fix WebDAV timestamp format handling
  - Disable internet connection check if a proxy is configured
  - Fix a potential file chunking problem on a server that is running out of storage
  - Do not expire file chunks while checking their existence
  - Fix loading of authentication apps in any case
  - Performance improvements by reducing the number of chmod operations.
  - Make the trusted domain upgrade feature more robust.
  - Don´ allow creating a "Shared" folder.
  - Fixed "select all" + download on public page
  - Fix share as link with email multiple users
  - Reset time of last update feed polling to fix the updater
  - Share API fixes
  - Admin option for public upload with encryption enabled
  - Fix CIFS with home shares
  - Detect a missing "data" directory mount
  - Fix the filesize calculation of encrypted files
  - Fixes in the OpenStack support
  - Fixes in the SWIFT support
  - Don't block PHP sessions during download
  - Fix sharing oc addressbooks
  - Several ownCloud Documents improvements and fixes
  - Several smaller bugfixes
* Mon Mar  3 2014 danimo@owncloud.com
- update tar ball
* Sun Mar  2 2014 danimo@owncloud.com
  Release  "6.0.2", March 3. 2014
- Several security fixes
- Improved trash bin performance for deleting lots of files
- Mobile interface improvements
- Fix key problems in encryption mode in rare situations
- Smaller LDAP improvements
- Fix the keep-alive ping for non standard php session lifetimes
- Cleanup storage table when deleting an entry
- Fix compatibility with xsendfile mode
- Fix file size calculation in encryption mode
- Fix image previews in trash bin
- Fix public upload with enabled enryption
- Added APC enabled check
- Correctly localise date in notification emails
- Improve compatibility with some CIFS servers
- Fix shared files and Gallery
- Several Contacts compatibility improvements
- Several Documents improvements
- A lot of smaller bug fixes
* Wed Jan 22 2014 danimo@owncloud.com
- Update to ownCloud 6.0.1
* Fri Jan 17 2014 freitag@owncloud.com
- Fixed tab versus space problem for deb.
* Fri Jan 17 2014 freitag@owncloud.com
- Added proper deb style configuration.
* Sat Dec 14 2013 freitag@owncloud.com
- Update to patch version ownCloud 6.0.0a
* Tue Dec 10 2013 danimo@owncloud.com
- Update to ownCloud 6 final
* Sat Dec  7 2013 freitag@owncloud.com
- Updated metadata for rc4
* Sat Dec  7 2013 freitag@owncloud.com
- Update to ownCloud 6 RC 4
* Mon Dec  2 2013 freitag@owncloud.com
- Fix recommends, added libreoffice and php5-imagemagic
* Mon Dec  2 2013 freitag@owncloud.com
- Update to second release candidate of oC6
* Thu Nov 28 2013 PVince81@opensuse.org
- setting version name to lowercase to make RPM/Zypper correctly upgrade from beta
* Thu Nov 28 2013 freitag@owncloud.com
- first release candidate of ownCloud 6
* Wed Nov 20 2013 danimo@owncloud.com
- fifth beta version of ownCloud 6
* Wed Nov 13 2013 danimo@owncloud.com
- forth beta version of ownCloud 6
* Thu Nov  7 2013 danimo@owncloud.com
- third beta version of ownCloud 6
* Thu Oct 31 2013 freitag@owncloud.com
- Fix version tag in dsc file.
* Wed Oct 30 2013 freitag@owncloud.com
- Remove files from file section.
* Wed Oct 30 2013 freitag@owncloud.com
- second beta version of ownCloud 6
* Wed Oct 23 2013 freitag@owncloud.com
- remove binaries and devel stuff
* Wed Oct 23 2013 freitag@owncloud.com
- add version.php to filelist
* Wed Oct 23 2013 freitag@owncloud.com
- Update to first beta of ownCloud 6
* Sun Sep 29 2013 freitag@owncloud.com
- Update to ownCloud 5.0.12 RC1
* Wed Aug 28 2013 danimo@owncloud.com
- Update to ownCloud 5.0.11 RC1
* Tue Aug  6 2013 freitag@owncloud.com
- Fixed file list
* Tue Aug  6 2013 freitag@owncloud.com
- Update to ownCloud 5.0.10 RC1
* Mon Jun  3 2013 freitag@owncloud.com
- Update to ownCloud 5.0.7 RC1
* Mon May 13 2013 freitag@owncloud.com
- Update to ownCloud 5.0.6 RC2
* Tue May  7 2013 freitag@owncloud.com
  Release  "5.0.6" RC 1 May 9. 2013
  - Fix renaming of shared files
  - Fix UUID handling with LDAP
  - Fix several undelete files issues
  - Fix LDAP cachekey handling
  - Several OCS API fixes
  - Dropbox mounting fixes
  - Remove ldap group name restrictions
  - Fix fetching of the userlist with multiple user backends
  - Turn off password autocompletion
  - Translation fixes of the Shared folder
  - Fix the fileactions order for filetypes
  - Allow to ship a default theme
  - Disallow URLs containing "@"
  - Smaller layout improvemens
  - Log an upgrade warning
  - Log a trash bin cleanup message
  - Improved quota calculation
  - Several Calendar fixes
  - Use displaynames in contacts
  - Check for existing address books during migrate->import
  - Texteditor fixes
  - Order images in Gallery
* Wed Apr 10 2013 freitag@owncloud.com
- Update to daily build.
* Wed Apr  3 2013 danimo@owncloud.com
  Release  "5.0.3" April 3. 2013
  - Correctly handle .part files
  - Improve PostgreSQL support
  - Fix database upgrading from old versions
  - Improved app styles
* Tue Apr  2 2013 danimo@owncloud.com
  Release  "5.0.2" April 2. 2013
  - Fix versioning string
  - Fix compatibility with older MySQL versions
* Tue Apr  2 2013 danimo@owncloud.com
  Release  "5.0.1" April 2. 2013
  - Fixed classnames and improved autoloaded to improve copatibility with older
    PHP versions
  - Show a warning if an insecure PHP version is used.
  - Filesizes are displayed correctly.
  - Fixed groups in usermanagement
  - Several Internet Explorer fixes
  - Use display-names in more places
  - Fix upgrading of cache
  - Fix navigation scrollbar for lots of apps
  - Fixed ETag handling to prevent wrong conflict files
  - Fix public link handling
  - Better indexes to improve performance
  - Several Windows server fixes
  - Fix renames of shared files
  - Fix PostgreSQL compatibility
  - Improve error reporting for app installation
  - Improved compatibility with Novell eDirectory
  - Several LDAP fixes
  - Improved sorting in usermanagement
  - Improved background jobs
  - Several CardDAV contacts fixes
  - Several mediaplayer fixes
  - Fixes for text editor
  - Several lucene search fixes
  - Several smaller fixes
  - contacts: SQL Injection (oC-SA-2013-012)
  - Multiple XSS vulnerabilities (oC-SA-2013-011)
* Tue Mar 12 2013 freitag@owncloud.com
  Release  "5.0.0" Feb 14. 2013
  - New design
  - Restore deleted files
  - New fulltext search
  - Display names
  - New photo gallery
  - Improved calendar and contacts
  - Improved bookmarks
  - New documentation system
  - Improved file cache
  - Improved security checks
  - Security hardening in templates"
  - Security hardening: Implemented Content Security Policy
  - Better versioning of better autoexpire
  - Extended external storage
  - New OCS REST API support
  - Improved apps management
* Tue Feb 19 2013 freitag@owncloud.com
  Release  "4.5.7" Feb 19. 2013
  - Fix for 3rd party apps dropping the database
  - Fix SubAdmins management
  - Fix PHP warnings
  - Fix compatibility with some CIFS shares
  - More robust apps management
  - Remove not needed AWS tests
  - Improved mime type parsing
  - Several sharing fixes
  - Offer the option to change he password only supported by he backend
  - More robust auto language detection
  - Revoke DB rights on install only if the db is newly created
  - Fix rendering of database connection error page
  - LDAP: update quota more often
  - Multiple XSS vulnerabilities (oC-SA-2013-003)
  - Multiple CSRF vulnerabilities (oC-SA-2013-004)
  - PHP settings disclosure (oC-SA-2013-005)
  - Multiple code executions (oC-SA-2013-006)
  - Privilege escalation in the calendar application (oC-SA-2013-007)
* Sat Feb  9 2013 freitag@owncloud.com
- Fix if unbalance.
* Sat Feb  9 2013 freitag@owncloud.com
- Fix dependencies for CentOS 5 versus CentOS 6.
* Tue Jan 22 2013 freitag@owncloud.com
- Fix: install forgotten .htaccess file to server root.
* Tue Jan 22 2013 freitag@owncloud.com
  Release 4.5.6 Jan 22. 2013
  - Improved language detection
  - Improved translations
  - Fix link to bugtracker
  - Several IE 6/7/8 fixes
  - SabreDAV updated to 1.6.6
  - Improved error reporting
  - Support special characters in mountpoint
  - Interpret http 403 and 401 as not authorized in user_webdavauth
  - Several fixes for special characters in files and folders
  - Improved PostgreSQL support
  - Check database names for valid characters
  - Fix default email address calculation
  - Remove debug output on send password page
  - Add SMTP port configuration option
  - Only show the max possible upload of 2GB on a 32 bit system
  - Show progress during file downloads
  - Security: Fix multiple XSS problems: CVE-2013-0201,  CVE-2013-0202, CVE-2013-0203
  - Security: Fix Code execution in external storage: CVE-2013-0204
  - Security: Removed remoteStorage app because of unfixed security problems.-
* Thu Dec 20 2012 freitag@owncloud.com
- Release 4.5.5, Dec 20, 2012
  - Show drag and drop shadow for Firefox
  - Fix Knowledgebase under certain conditions
  - Fix setting of sharing password
  - Fix setting of sharing password
  - Several sharing fixes
  - Fixversioning during sharing
  - Fix mounting of external filesystems especially CIFS
  - Fix several PHP warnings
  - Show /Shared as standard directory
  - Fix session management for running several ownClouds on the same host
  - Fix WebDAV quota enforement
  - Fix CalDAV with LDAP users
  - Better warning about missing dependencies
  - Add warning about conflicting WebDAV auth and LDAP backend
  - Restore send sharing link my email
  - Fix encoding problem with mounting of CIFS filesystems
  - Fix mimetype icons for new files
  - Fix the folder size calculation
  - Fix for deleting multiple files
  - Fix for controling the data dir with LDAP
  - Security: Auth bypass in user_webdavauth and user_ldap (oC-SA-2012-006)
  - Security: XSS vulnerability in bookmarks (oC-SA-2012-007)
* Mon Dec  3 2012 msrex@owncloud.com
- fix %%postun for SElinux
  >>>>>>> ./owncloud.changes.r31130cdd438d36f5f274bc701e4891bb
* Sun Dec  2 2012 freitag@owncloud.com
- Release  "4.5.4", Dec 3. 2012
  * Fix a regression for system where output buffering is disabled
  * Fix a problem with old file versions stored in the filesystem cache
  * Fix group and subadmin ajax bug
  * Important LDAP fix
  * Improved Updater
* Tue Nov 27 2012 freitag@owncloud.com
-  Release 4.5.3, Nov 26. 2012
  * Fix the new from url button
  * Fix a memory overflow with downloading of big files via WebDAV
  * Better error output in case of DB problems
  * Fix problems with uploading files who have special characters in the name
  * Improved reverse proxy and load balancer support
  * Fix wrong folder size calculation
  * Improved share link generation
  * Fix the syncing of the Shared folder
  * Fix Sharing by link from within Shared folder
  * Several LDAP integration fixes
  * Fix support for PostgreSQL
  * Several WebDAV fixes
  * Fix drag and drop uploading
  * Improved translations
  * Several Gallery fixes
  * Several Contacts fixes
  * Smaller fixes
* Wed Nov 14 2012 freitag@owncloud.com
  * Release 4.5.2 Nov 14, 2012
  - Fix syncing of shared folder
  - Various sharing bugs fixed
  - Fix bug with deleting users
  - Fix check if resharing is allowed
  - Fix webdavauth app
  - Several ldap fixes
  - Fix data migration
  - Fix folder uploads
  - Fix generatino of etags
  - fix user specific mount configuration
  - Several PostgreSQL fixes
  - Improved performance of file updates
  - Fix some php warnings
  - Fix filesize calculation
  - add visual feedback if password is set
  - Various smaller fixes
  - Several critical security fixes
  - XSS vulnerability in user_webdavauth (oC-SA-2012-003)
  - Code Execution in /lib/migrate.php (oC-SA-2012-004)
  - Code Execution in /lib/filesystem.php (oC-SA-2012-005)
* Thu Oct 25 2012 freitag@owncloud.com
- Update to new released tarball of version 4.5.1.
* Wed Oct 24 2012 freitag@owncloud.com
  * Release 4.5.1 Oct 24, 2012
  - Fix path encoding in breadcrumb
  - Fix sharing of files with special characters
  - Fix upercase/lowercase probelm in usernames with WQebDAV
  - Fix LDAP plugin with Postgres
  - Fix userID migration
  - Fix sharing of mounted Files
  - Delete userfiles after deleting a user
  - Make Webinterface work with nonstandard path
  - Fix retieval of Quota, Email via LDAP
  - Show a warning in installer if .htaccess is not working
  - Fix Shared folder caching
  - Increase security by using openssl random number generator
  - Fix syncing of rollback files
  - Fix the swift files backend
  - Disallow user to delete own account
  - Various smaller fixes
* Wed Oct 10 2012 freitag@owncloud.com
  * Release  4.5.0  Oct 9. 2012
  - Faster Syncing
  - Sub Administrators
  - GUI for mounting of external storage
  - Improved File Versioning
  - Enhanced Sharing
  - Reworked LDAP
  - Big File Chunking
* Wed Aug 15 2012 freitag@owncloud.com
  * Release 4.0.7 Aug 15, 2012
  - Show Login Button when user and password are autocompleted
  - Sanitize LDAP base, user and groups
  - Fix non active Adressbooks
  - Calendar: Remove double html encoding
  - Fix label for versioning in admin settings
  - Add parent directory into filecache if it doesnÂ´t exist
  - Handle non writable files correctly
  - Disable webfinger completely if not activated
  - Security: Disable user listings in DAV
  - Check file blacklist for file renames
  - Security: Fix XSS bug in Gallery
  - Security: Several CSRF security fixes
  - Security: Validate cookie to prevent auth bypasses
  Special thanks to Julien Cayssol for reporting several security problems
* Tue Jul 31 2012 freitag@owncloud.com
  * Release  "4.0.6" Aug 1. 2012
  - More robust LDAP integration during unexpected collisions
  - Fix sharing for users with @ in username
  - Additional error handling for emailing of private links
  - Cleanup old session files
  - Fix user space calculation
  - Fix Ampache authentication
  - Remove delete tipsy if file is deleted
  - Dont delete lots of session files during DAV requests
  - Fix error when no adressbook is created
  - Check if php-ldap is installed
  - Security: Check for Admin user in appcinfig.php
  - Security: Several CSRF security fixes
* Thu Jul 19 2012 freitag@owncloud.com
- Release  "4.0.5"
  July 20. 2012
  * Fix remember the username and autologin
  * Offer an option to allow sharing outside the group.
  * Fix for birthday format
  * Fixes for several encoding fixes for unicode characters
  * Fix invalid filesystem cache in the sharing folder
  * Several calendar and contacs fixes
  * Fix sending of emails
  * Several fixes in the system log
  * Several fixes for the external filesystem feature
  * Several CSRF security fixes
* Wed Jun 27 2012 freitag@owncloud.com
- Release  "4.0.4"
  June 28. 2012
  * Fix assigning several groups to a user.
  * Fix LDAP connector with AD servers
  * Conserve some memory in Contacts App
  * Fix a warning in Gallery when deleting files
  * Fix a bug in the music scanner
* Fri Jun 22 2012 freitag@owncloud.com
- update to version ownCloud community server 4.0.3
  June 23. 2012
  * Added a check if the .htaccess file is working and the data directory is protected or not.
  * Added a check if a user is alowed to edit a bookmark or not.
  * Fix the bookmarklet
  * Fix the timezone in the datepicker
  * Fix mimetype detection for cdr files
  * Fix the filecache for the /Shared folder
  * Fix a potential data corruption bug in the encryption app
  * Don't show other users filenames during filesystem cache rebuild
  * Fix several XSS bugs
  * Performance improvements for WebDAV and Desktop Syncing
  * Fix quota calculation
  * Improve the LDAP integration and group management
  * Fix problems with the pdf viewer
  * Fix user account migration
  * Implement several CSRF security checks
  * Fix a gallery bug where first picture is repeated in the last picture.
  * Lot's of calendar fixes
  * Fix problem with "/" in filenames
  * Updated translations
  * Several fixes in Contacts
  * Lot's of fixes in the Tasks App
* Mon Jun 11 2012 freitag@owncloud.com
- update to version ownCloud community server 4.0.2
  * Lot´s of gallery fixes
  * More 3rd party apps visible
  * Fixed update notifications
  * Several calendar fixes
  * Several XSS fixes in calendar
  * Several improvements in contacts
  * Fix infinite redirect during setup for windows hosts
  * Several XSS fixes in contacts
  * New user password salting
  * Several LDAP fixes
  * Fix doublicate emails in sharing
  * Improved compatibility with Android browser
  * Fixed calendar links
  * Fixed logging
  * Allow “/” in filenames
  * Updated translations
  * Fixed reverse proxy and custom hosts configuration
  * Fix contact photo editing
  * Dont allow renaming, deleting and resharing of shared folder
* Mon Jun  4 2012 freitag@owncloud.com
- update to version ownCloud community server 4.0.1
  * Verify if user exists when loggin (oc-863)
  * More efficient log file handling
  * PDO requirement check
  * Check if apps folder is writable
  * prevent division by zero problem during output of free space
  * better mysql error message
  * correctly configure ldap group backend  (oc-887)
  * sort users and groups (oc-779)
  * LDAP. correctly handle group filter (oc-867)
  * try to switch magic quotes of globally
  * fix ategory error reporting (oc-874)
  * correctly handle reverse proxy / load balancer https handling
  * prevent session already started warning
  * fix the files breadcrumb
  * don't try to use smtp auth if config files says no
  * fix versioning path
  * security: fix a XSS problem in calendar
  * make LDAP pqsql compatible
  * fix pqsql database migration
  * fix ldap config interface
  * support for LDAP "member"
  * don't hardcode /tmp
  * fix potential security problem for requested apps parameter
  * fix notes in contacts properly
  * fix timezone detection
  * fix interti_id in calendar
  * set DB prefix for pqsql
  * security: fix a XSS problem in contacts
  * correctly encode caldav link
  * allow longer path in gallery
  * disable not compatible apps during upgrade
  * fix HEAD request for downloads
  * fix private link sharing via email
  * use UTC as default timezone
  * style fixes for tasks app
* Mon May 21 2012 freitag@owncloud.com
- update to version ownCloud community server 4.0.0
  * versioning of files
  * server side encryption
  * drag and drop upload
  * theming
  * ODF file viewer
  * ownCloud Application APIs
  * migration adn backup
  * tasks management
  * application store
  * lots of improvements
* Wed Apr 11 2012 freitag@opensuse.org
- adopted Markus' latest changes for Fedora 16
* Wed Apr 11 2012 freitag@opensuse.org
- created new community version packages from the enterprise branch.
  New upstream version 3.0.2, release april 11, 2012:
  - Drag and Drop fixed
  - Fixed Sharing for LDAP Users
  - Fix loading of LDAP Plugin
  - Security: Make password hashes more random
  - Security: Fix a XXS problem
  - Several small bugfixes
* Wed Apr 11 2012 msrex@owncloud.com
- update to ownCloud 2012.0.1
* Wed Apr 11 2012 msrex@owncloud.com
- update to ownCloud 2012.0.1
* Fri Apr  6 2012 msrex@owncloud.com
- fix fedora permissions
- detect selinux on redhat platforms and add permissions for owncloud
* Thu Apr  5 2012 msrex@owncloud.com
- repair previously messed-up non-suse-platforms dependencies
* Tue Apr  3 2012 msrex@owncloud.com
- change dependencies for some non-suse-platforms
* Sun Apr  1 2012 msrex@owncloud.com
- no more fdupes for now for anybody
* Sun Apr  1 2012 msrex@owncloud.com
- remove fdupes requirement for non-suse packages
* Sun Apr  1 2012 msrex@owncloud.com
- update to final ownCloud 2012 enterprise packaging
- updated descriptions
* Sun Apr  1 2012 msrex@owncloud.com
- make specfile work with both redhat and suse-based systems
- update to current ownCloud stable branch
* Sun Apr  1 2012 freitag@opensuse.org
- autostart ntp at server installation.
* Thu Feb  2 2012 asemen@suse.de
- Fix apache2 start error, missconfig in owncloud.conf
* Thu Feb  2 2012 tom@opensuse.org
- Upstream version 3.0:
  - Cloud Text Editing
  - Application Store
  - Photo Gallery
  - Fixed permissions (bnc#736764)
  - added apache config to prevent php execution in upload dir
* Thu Oct 20 2011 jnelson-suse@jamponi.net
- Upstream version 2.0
* Wed Sep 28 2011 wstephenson@suse.com
- Upstream version 2.0 beta2
  - Fixes to user creation and LDAP integration
  - Reset package version number to 1.9.1 to allow clean upgrades
* Mon Sep 26 2011 asemen@suse.de
- upstream beta 1 Version 2.0
* Mon Sep 19 2011 asemen@suse.de
- update from upstream some fixes in calender
* Fri Sep 16 2011 freitag@suse.com
- added a missing dependency php5-mbstring
  fixed some rpmlint warnings
* Thu Sep 15 2011 asemen@suse.de
- upstream upgrade to version ownCloud 2.0
* Wed Jun  8 2011 asemen@suse.de
- upstream upgrade to version ownCloud 1.2
* Mon Jan 24 2011 asemen@suse.de
- optimizing build spec file
* Wed Jan 19 2011 asemen@suse.de
- initial build for php:applications project
* Tue Nov  2 2010 asemen@suse.de
- upstream upgrade to version ownCloud 1.1
  Changes
  * Plugin system
  * User management
  * ownCloud can now be installed in a DB shared with other applications since ownCloud tables has a prefix (default is "oc_" but can choose it)
  * Experimental PostgreSQL support
  * Text viewer with syntax highlighting
  * Fixes, fixes, fixes...
  * Code cleanup
* Mon Oct 25 2010 asemen@suse.de
- rebuild with ownCloud 1.0 rc1
* Mon Oct 25 2010 asemen@suse.de
- initial build of ownCloud 1.0
