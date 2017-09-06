# vim:sw=4:et
#############################################################################
# File          : CheckFilelist.py
# Package       : rpmlint
# Author        : Ludwig Nussel
# Modified      : Anas Nashif
# Purpose       : Check for wrongly packaged files and FHS violations
#############################################################################

from Filter import *
import AbstractCheck
import re
import os
import string
import fnmatch
from rpm import RPMTAG_VENDOR

_defaulterror = 'meego-filelist-forbidden'
_defaultmsg = '%(file)s is not allowed in MeeGo'

def notnoarch(pkg):
    return pkg.arch != 'noarch'

def isfilesystem(pkg):
    return pkg.name == 'filesystem'

def isdebuginfo(pkg):
    if pkg.name.endswith('-debuginfo') \
    or pkg.name.endswith('-debuginfo-32bit') \
    or pkg.name.endswith('-debuginfo-64bit') \
    or pkg.name.endswith('-debugsource') \
    or pkg.name.endswith('-debug'):
        return True

def notsymlink(pkg, f):
    mode = pkg.files()[f].mode
    type = (mode>>12)&017
    return type != 012

def ghostfile(pkg, f):
    ghosts = pkg.ghostFiles()
    return f in ghosts

_goodprefixes = (
        '/bin/',
        '/boot/',
        '/etc/',
        '/lib/',
        '/lib64/',
        '/media/',
        # MeeGo policy handled in separate check
        '/opt/',
        '/sbin/',
        '/srv/',
        # MeeGo policy handled in separate check
        '/usr/X11R6/',
        '/usr/bin/',
        '/usr/games/',
        '/usr/include/',
        '/usr/lib/',
        '/usr/lib64/',
        '/usr/sbin/',
        # MeeGo Exception
        '/usr/libexec/',
        '/usr/share/',
        # actually only linux is allowed by fhs
        '/usr/src/linux',
        '/usr/src/debug/',
        '/usr/src/packages/',
        '/var/account/',
        '/var/cache/',
        '/var/crash/',
        '/var/games/',
        '/var/lib/',
        '/var/lock/',
        '/var/log/',
        '/var/mail/',
        '/var/opt/',
        '/var/run/',
        '/var/spool/',
        '/var/yp/',
        # those are not in FHS!
        '/var/adm/',
        '/var/nis/',
        '/emul/',
        )

# computed from goodprefixes.
# Directories that are only allowed to have defined subdirs (such as /usr)
_restricteddirs = set()

_checks = [
        {
            'bad': [
                '*/.xvpics',
                '*.orig',
                '*.orig.gz',
                '/usr/share/*/.libs*',
                '/usr/share/*/.deps*',
                '/var/adm/setup',
                '/etc/httpd/*',
                '/etc/init.d/*/*',
                '/usr/share/locale/LC_MESSAGES',
                ],
            },
        {
            'error': 'meego-filelist-forbidden-perl-dir',
            'details': '''perl files installed a non-vendor installed path, 
                          which is not allowed in MeeGo.''',
            'bad': [
                '/usr/lib/perl5/site_perl/*',
                ],
        },
        {
            'error': 'meego-filelist-forbidden-backup-file',
            'details': 'backup files (e.g. files ending in ~ or .bak) are not allowed',
            'bad': [
                '*~',
                '*.bak',
                ],
            'ignorefileif': ghostfile,
            },
        {
            'error': 'meego-filelist-forbidden-devel-in-lib',
            'details': 'please move la files, static libs and .so symlinks to /usr/lib(64)',
            'bad': [
                "/lib/*.la",
                "/lib/*.a",
                "/lib64/*.la",
                "/lib64/*.a",
                ]
            },
        {
            'error': 'meego-filelist-forbidden-devel-in-lib',
            'details': 'please move la files, static libs and .so symlinks to /usr/lib(64)',
            'good': [
                # exception for pam
                "/lib/security/*.so",
                "/lib64/security/*.so",
                ],
            'bad': [
                "/lib/*.so",
                "/lib64/*.so",
                ],
            # some libs without proper soname are packaged directly
            'ignorefileif': notsymlink,
            },
        {
            'error': 'meego-filelist-forbidden-fhs23',
            'msg': '%(file)s is not allowed in FHS 2.3',
            'details': 'see http://www.pathname.com/fhs/ to find a better location',
            'bad': [
                "/etc/X11/app-defaults/*",
                "/usr/local/man/*/*",
                "/var/lib/games",
                "/var/lib/games/*",
                "/usr/sbin/*/*",
                "/sbin/init.d",
                "/sbin/init.d/*",
                "/bin/*/*",
                ]
            },
        {
                'error': 'meego-filelist-forbidden-srv',
                'details': """Please use /srv for ftp and http data""",
                'bad': [
                    '/usr/local/ftp',
                    '/usr/local/http',
                    ],
                },
        {
                'error': 'meego-filelist-forbidden-games',
                'details': """static data has to be in /usr/share/games, variable in /var/games""",
                'bad': [
                    '/usr/games/bin',
                    '/usr/games/lib',
                    '/usr/games/*/*',
                    ],
                },
        {
                'error': 'meego-filelist-forbidden-noarch',
                'msg': '%(file)s is not allowed in a noarch package',
                'bad': [
                    '/lib64',
                    '/lib64/*',
                    '/usr/lib64',
                    '/usr/lib64/*',
                    '/usr/X11R6/lib64',
                    '/usr/X11R6/lib64/*',
                    '/opt/gnome/lib64',
                    '/opt/gnome/lib64/*',
                    '/opt/kde3/lib64',
                    '/opt/kde3/lib64/*',
                    '/usr/lib/pkgconfig/*',
                    '/usr/lib/perl5/vendor_perl/5.*/*-linux-*/*',
                    ],
                'ignorepkgif': notnoarch,
                },
        {
                'error': 'meego-filelist-forbidden-debuginfo',
                'msg': '%(file)s may only be packaged in the -debuginfo subpackage',
                'bad': [
                    '/usr/lib/debug/*',
                    ],
                'ignorepkgif': isdebuginfo,
                },
        {
                'error': 'meego-filelist-forbidden-locale',
                'details': """Please use nb or nb_NO (and nn for nynorsk)"""
                """see https://bugzilla.novell.com/show_bug.cgi?id=42748""",
                'bad': [
                    '/opt/gnome/share/locale/no',
                    '/opt/gnome/share/locale/no/*',
                    '/opt/kde3/share/locale/no',
                    '/opt/kde3/share/locale/no/*',
                    '/usr/share/locale/no',
                    '/usr/share/locale/no/*',
                    '/usr/share/vim/*/lang/no',
                    '/usr/share/vim/*/lang/no/*',
                    ],
                },
        {
                'error': 'meego-filelist-forbidden-xorg',
                'details': """Please use the updated paths for Xorg 7.1 and above""",
                'bad': [
                    '/usr/X11R6/*',
                    ],
                'ignorepkgif': isfilesystem,
                },
        {
                'error': 'meego-filelist-forbidden-opt',
                'details': """/opt may not be used by a distribution. It is reserved for 3rd party packagers""",
                },
        ]

class FilelistCheck(AbstractCheck.AbstractCheck):
    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, "CheckFilelist")
        import re

        _restricteddirs.add('/')
        for d in _goodprefixes:
            if d.count('/') > 2:
                _restricteddirs.add(d[0:-1].rpartition('/')[0])

        for check in _checks:
            if 'good' in check:
                for i in range(len(check['good'])):
                    pattern = check['good'][i]
                    if '*' in pattern:
                        r = fnmatch.translate(pattern)
                        check['good'][i] = re.compile(r)

            if 'bad' in check:
                for i in range(len(check['bad'])):
                    pattern = check['bad'][i]
                    if '*' in pattern:
                        r = fnmatch.translate(pattern)
                        check['bad'][i] = re.compile(r)

    def check(self, pkg):
        global _checks
        global _defaultmsg
        global _defaulterror
        global _goodprefixes
        global _restricteddirs

        if pkg.isSource():
            return

        files = pkg.files()

        if not files:
            printError(pkg, 'meego-filelist-empty', 'packages without any files are not allowed in MeeGo')
            return

        for check in _checks:

            if 'ignorepkgif' in check:
                if check['ignorepkgif'](pkg):
                    continue

            if 'msg' in check:
                msg = check['msg']
            else:
                msg = _defaultmsg

            if 'error' in check:
                error = check['error']
            else:
                error = _defaulterror

            if 'good' in check or 'bad' in check:
                for f in files.keys():
                    ok = False
                    if 'good' in check:
                        for g in check['good']:
                            if (not isinstance(g, str) and  g.match(f)) or g == f:
                                ok = True
                                break
                    if ok:
                        continue

                    if 'bad' in check:
                        for b in check['bad']:
                            if 'ignorefileif' in check:
                                if check['ignorefileif'](pkg, f):
                                    continue
                            if (not isinstance(b, str) and  b.match(f)) or b == f:
                                m = msg % { 'file':f }
                                printError(pkg, error, m)

        invalidfhs = set()
        invalidopt = set()

        if pkg.header[RPMTAG_VENDOR] and pkg.header[RPMTAG_VENDOR].find('MeeGo') != -1:
            isMeeGo = True
        else:
            isMeeGo = False

        # the checks here only warn about a directory once rather
        # than reporting potentially hundreds of files individually
        for f, pkgfile in files.items():
            type = (pkgfile.mode>>12)&017

            # append / to directories
            if type == 04:
                f +=  '/'

            if not f.startswith(_goodprefixes):
                base = f.rpartition('/')
                pfx = None
                # find the first invalid path component (/usr/foo/bar/baz -> /usr)
                while base[0] and not base[0].startswith(_goodprefixes) and not base[0] in _restricteddirs:
                    pfx = base[0]
                    base = base[0].rpartition('/')

                if not pfx:
                    invalidfhs.add(f)
                else:
                    invalidfhs.add(pfx)

            if f.startswith('/opt'):
                try:
                    provider = f.split('/')[2]
                except:
                    continue

                d = '/opt/'+provider
                invalidopt.add(d)

        for f in invalidfhs:
            printError(pkg, 'meego-filelist-forbidden-fhs23', "%(file)s is not allowed in FHS 2.3" % { 'file': f })

        for f in invalidopt:
            printError(pkg, 'meego-filelist-forbidden-opt', '%(file)s is not allowed for official MeeGo packages' % { 'file': f })

check=FilelistCheck()

if Config.info:
    for check in _checks:

        if not 'details' in check:
            continue

        if not 'error' in check:
            continue

        addDetails('meego-filelist-forbidden', """
Your package installs files or directories in a location that have
previously been blacklisted. Please have a look at the particular
file and see if the MeeGo Packaging Guidelines propose a better place
on where to install the file or not install it at all.""")

        addDetails(check['error'], check['details'])