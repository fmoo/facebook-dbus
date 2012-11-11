facebook-dbus is a reference implementation of a [sparts](http://github.com/fmoo/sparts)
service that exports Facebook's graph API over dbus.

Dependencies
============
facebook-dbus depends on a smattering of unusually diverse python libraries:

 * keyring
 * sparts (which depends on crazy stuff, like thrift)
 * dbus-python (which depends on python-gobject)
 * Twisted-web
