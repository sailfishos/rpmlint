# vim:sw=4:et
#############################################################################
# File          : CheckGNOMEMacros.py
# Package       : rpmlint
# Author        : Vincent Untz
# Purpose       : Check for GNOME related packaging errors
#############################################################################

import re
import string

import rpm

from Filter import *
import AbstractCheck
import Config

## FIXME
# Maybe detect packages installing icons in other themes than hicolor and not
# updating the icon cache for those themes?

_gnome_post_postun_checks = [
  ('glib2-gsettings-schema',
   re.compile('^/usr/share/glib-2.0/schemas/.+\.gschema.xml$'),
   'glib2-tools',
   re.compile('^[^#]*glib-compile-schemas', re.MULTILINE),
   True),

  ('glib2-gio-module',
   re.compile('^/usr/lib(?:64)?/gio/modules/'),
   'glib2-tools',
   re.compile('^[^#]*gio-querymodules', re.MULTILINE),
   True),

  ('gdk-pixbuf-loader',
   re.compile('^/usr/lib(?:64)?/gdk-pixbuf-2.0/[^/]+/loaders/'),
   'gdk-pixbuf-query-loaders',
   re.compile('^[^#]*gdk-pixbuf-query-loaders', re.MULTILINE),
   True),

  ('gtk2-immodule',
   re.compile('^/usr/lib(?:64)?/gtk-2.0/[^/]+/immodules/'),
   'gtk2',
   re.compile('^[^#]*gtk-query-immodules-2.0', re.MULTILINE),
   True),

  ('gtk3-immodule',
   re.compile('^/usr/lib(?:64)?/gtk-3.0/[^/]+/immodules/'),
   'gtk3-tools',
   re.compile('^[^#]*gtk-query-immodules-3.0', re.MULTILINE),
   True),

  # Not fatal since it would make too many things fail
  ('hicolor-icon-cache',
   re.compile('^/usr/share/icons/hicolor/'),
   None,
   re.compile('^[^#]*gtk-update-icon-cache', re.MULTILINE),
   False),

  ('mime-database',
   re.compile('^/usr/share/mime/packages/.+\.xml$'),
   None,
   re.compile('^[^#]*update-mime-database', re.MULTILINE),
   True),

  # Not fatal since it would make too many things fail
  ('desktop-database',
   re.compile('^/usr/share/applications/.+\.desktop$'),
   None,
   re.compile('^[^#]*update-desktop-database', re.MULTILINE),
   False)
]

_gnome_gconf_filename_re = re.compile('^/usr/share/GConf/schemas/.+\.schemas$')
_gnome_gconf_sciptlet_re = re.compile('^[^#]*gconftool-2', re.MULTILINE)

class GNOMECheck(AbstractCheck.AbstractCheck):

    def __init__(self):
        AbstractCheck.AbstractCheck.__init__(self, "CheckGNOMEMacros")

    def check(self, pkg):

        if pkg.isSource():
            return

        ghosts = pkg.ghostFiles()

        pkg_requires = set(map(lambda x: string.split(x[0],'(')[0], pkg.requires()))
        postin = pkg[rpm.RPMTAG_POSTIN] or pkg[rpm.RPMTAG_POSTINPROG]
        postun = pkg[rpm.RPMTAG_POSTUN] or pkg[rpm.RPMTAG_POSTUNPROG]
        posttrans = pkg[rpm.RPMTAG_POSTTRANS] or pkg[rpm.RPMTAG_POSTTRANSPROG]

        for filename in (x for x in pkg.files() if x not in ghosts):
            for (name, file_re, required, post_re, fatal) in _gnome_post_postun_checks:
                if fatal:
                    gnomePrint = printError
                else:
                    gnomePrint = printWarning

                if file_re.search(filename):
                    if required and required not in pkg_requires:
                        gnomePrint(pkg, 'meego-' + name + '-missing-requires', filename)
                    if not postin or not post_re.search(postin):
                        gnomePrint(pkg, 'meego-' + name + '-missing-postin', filename)
                    if not postun or not post_re.search(postun):
                        gnomePrint(pkg, 'meego-' + name + '-missing-postun', filename)

            if _gnome_gconf_filename_re.search(filename):
                if not ((postin and _gnome_gconf_sciptlet_re.search(postin)) or
                        (posttrans and _gnome_gconf_sciptlet_re.search(posttrans))):
                    printError(pkg, 'meego-gconf-schema-missing-scriptlets', filename)


check=GNOMECheck()

if Config.info:
    addDetails(
'meego-glib2-gsettings-schema-missing-requires',
'''A GSettings schema is in your package, but there is no dependency for the tool to recompile the schema database. Use %glib2_gsettings_schema_requires.''',

'meego-glib2-gsettings-schema-missing-postin',
'''A GSettings schema is in your package, but the schema database is not recompiled in the %post scriptlet. Use %glib2_gsettings_schema_post.''',

'meego-glib2-gsettings-schema-missing-postun',
'''A GSettings schema is in your package, but the schema database is not recompiled in the %postun scriptlet. Use %glib2_gsettings_schema_postun.''',

'meego-glib2-gio-module-missing-requires',
'''A GIO module is in your package, but there is no dependency for the tool to rebuild the GIO module cache. Use %glib2_gio_module_requires.''',

'meego-glib2-gio-module-missing-postin',
'''A GIO module is in your package, but the GIO module cache is not rebuilt in the %post scriptlet. Use %glib2_gio_module_post.''',

'meego-glib2-gio-module-missing-postun',
'''A GIO module is in your package, but the GIO module cache is not rebuilt in the %postun scriptlet. Use %glib2_gio_module_postun.''',

'meego-gdk-pixbuf-loader-missing-requires',
'''A gdk-pixbuf loader is in your package, but there is no dependency for the tool to rebuild the gdk-pixbuf loader cache. Use %gdk_pixbuf_loader_requires.''',

'meego-gdk-pixbuf-loader-missing-postin',
'''A gdk-pixbuf loader is in your package, but the gdk-pixbuf loader cache is not rebuilt in the %post scriptlet. Use %gdk_pixbuf_loader_post.''',

'meego-gdk-pixbuf-loader-missing-postun',
'''A gdk-pixbuf loader is in your package, but the gdk-pixbuf loader cache is not rebuilt in the %postun scriptlet. Use %gdk_pixbuf_loader_postun.''',

'meego-gtk2-immodule-missing-requires',
'''A GTK+ 2 IM module is in your package, but there is no dependency for the tool to rebuild the GTK+ 2 IM module cache. Use %gtk2_immodule_requires.''',

'meego-gtk2-immodule-missing-postin',
'''A GTK+ 2 IM module is in your package, but the GTK+ 2 IM module cache is not rebuilt in the %post scriptlet. Use %gtk2_immodule_post.''',

'meego-gtk2-immodule-missing-postun',
'''A GTK+ 2 IM module is in your package, but the GTK+ 2 IM module cache is not rebuilt in the %postun scriptlet. Use %gtk2_immodule_postun.''',

'meego-gtk3-immodule-missing-requires',
'''A GTK+ 3 IM module is in your package, but there is no dependency for the tool to rebuild the GTK+ 3 IM module cache. Use %gtk3_immodule_requires.''',

'meego-gtk3-immodule-missing-postin',
'''A GTK+ 3 IM module is in your package, but the GTK+ 3 IM module cache is not rebuilt in the %post scriptlet. Use %gtk3_immodule_post.''',

'meego-gtk3-immodule-missing-postun',
'''A GTK+ 3 IM module is in your package, but the GTK+ 3 IM module cache is not rebuilt in the %postun scriptlet. Use %gtk3_immodule_postun.''',

'meego-hicolor-icon-cache-missing-postin',
'''An icon for the hicolor theme is in your package, but the hicolor icon cache is not rebuilt in the %post scriptlet. Use %icon_theme_cache_post.''',

'meego-hicolor-icon-cache-missing-postun',
'''An icon for the hicolor theme is in your package, but the hicolor icon cache is not rebuilt in the %postun scriptlet. Use %icon_theme_cache_postun.''',

'meego-mime-database-missing-postin',
'''A MIME definition is in your package, but the MIME database is not rebuilt in the %post scriptlet. Use %mime_database_post.''',

'meego-mime-database-missing-postun',
'''A MIME definition is in your package, but the MIME database is not rebuilt in the %postun scriptlet. Use %mime_database_postun.''',

'meego-desktop-database-missing-postin',
'''A desktop file is in your package, but the desktop database is not rebuilt in the %post scriptlet. Use %desktop_database_post.''',

'meego-desktop-database-missing-postun',
'''A desktop file is in your package, but the desktop database is not rebuilt in the %postun scriptlet. Use %desktop_database_postun.''',

'meego-gconf-schema-missing-scriptlets',
'''A GConf schema is in your package, but the GConf configuration is not updated by scriptlets. Please use the gconf RPM macros.'''

)
