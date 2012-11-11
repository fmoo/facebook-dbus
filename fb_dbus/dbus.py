from __future__ import absolute_import
import dbus.service
import keyring
import logging
import urllib
import urlparse
from functools import partial
from twisted.web.client import getPage
from twisted.internet import reactor


class _TwistedHelper(object):
    def getPage(self, url, success_cb, error_cb):
        reactor.callFromThread(self.doGetPage, url, success_cb, error_cb)

    def doGetPage(self, url, success_cb, error_cb):
        d = getPage(str(url), timeout=5.0)
        d.addCallback(success_cb)
        d.addErrback(self.logError)
        d.addErrback(error_cb)
        return d

    def makeURL(self, endpoint, **query):
        access_token = getattr(self, 'access_token', None)
        if access_token is not None:
            query['access_token'] = access_token

        url = 'https://graph.facebook.com' + endpoint
        if query:
            url += '?' + urllib.urlencode(query)

        return url

    def logError(self, reason):
        self.logger.error(reason)
        return reason
        

class FBAccessDBusObject(dbus.service.Object, _TwistedHelper):
    def __init__(self, bus):
        dbus.service.Object.__init__(self, bus, '/')
        self.bus = bus
        self.app_services = {}
        self.user_services = {}
        self.anonymous = FBAnonymousAPIDBusObject(self.bus)
        self.logger = logging.getLogger('sparts.fb_dbus.access')

    def makeAppAccessTokenURL(self, application_id, application_secret):
        return self.makeURL('/oauth/access_token', client_id=application_id,
                            client_secret=application_secret,
                            grant_type='client_credentials')

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.AuthService',
                         in_signature='ss', out_signature='s',
                         async_callbacks=('success_cb', 'error_cb'),)
    def setAppSecret(self, application_id, application_secret,
                     success_cb=None, error_cb=None):
        """Register an application + secret.

        Allows you to make graph API calls as the application."""
        keyring.set_password('sparts.fb_dbus.app_secret', str(application_id),
                             str(application_secret))

        # Verify Application - return app_token
        url = self.makeAppAccessTokenURL(application_id, application_secret)
        self.getPage(url, 
            partial(self.onAppAccessToken, application_id,
                    application_secret, success_cb, error_cb), error_cb)

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.AuthService',
                         in_signature='ss', out_signature='')
    def setAppAccessToken(self, application_id, access_token):
        keyring.set_password('sparts.fb_dbus.app_token',
                             str(application_id), str(access_token))
        self.registerAppService(application_id, access_token)

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.AuthService',
                         in_signature='s', out_signature='s',
                         async_callbacks=('success_cb', 'error_cb'),)
    def getAppAccessToken(self, application_id, success_cb=None, error_cb=None):
        access_token = keyring.get_password('sparts.fb_dbus.app_token',
                                            str(application_id))
        if access_token is not None:
            self.registerAppService(application_id, access_token)
            success_cb(access_token)
            return

        secret = keyring.get_password('sparts.fb_dbus.app_secret',
                                      str(application_id))
        assert secret is not None, "Please call setAppSecret first"

        # Verify Application - return app_token
        url = self.makeAppAccessTokenURL(application_id, secret)
        self.getPage(url, 
            partial(self.onAppAccessToken, application_id,
                    secret, success_cb, error_cb), error_cb)

    def onAppAccessToken(self, application_id, application_secret, success_cb,
                         error_cb, page_content):
        d = urlparse.parse_qs(page_content)
        self.logger.debug("response=%s", d)
        access_token = d['access_token'][0]
        keyring.set_password('sparts.fb_dbus.app_token', str(application_id),
                             str(access_token))
        self.registerAppService(application_id, access_token)
        success_cb(access_token)

    def registerAppService(self, application_id, access_token):
        if application_id not in self.app_services:
            self.app_services[application_id] = \
                FBAppAPIDBusObject(self.bus, application_id, access_token)

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.AuthService',
                         in_signature='ss', out_signature='s',
                         async_callbacks=('success_cb', 'error_cb'),)
    def accessApp(self, app_id, user, success_cb=None, error_cb=None):
        access_token = keyring.get_password(
            'sparts.fb_dbus.user_token.' + app_id, user)
        if access_token is None:
            self.logger.error('No Access Token for %s for app %s.', user, app_id)
            # TODO - attempt login with app secret
            #access_token = self.loginWithAppSecret(app_id, user)

        if access_token is None:
            error_cb()
            return

        self.user_services[(app_id, user)] = \
            FBUserAPIDBusObject(self.bus, app_id, user, access_token)
        success_cb(access_token)


class FBAPIDBusObject(dbus.service.Object, _TwistedHelper):
    def __init__(self, bus, app_id=None, user=None, access_token=None):
        self.app_id = app_id
        self.user = user
        self.access_token = access_token

        if access_token:
            assert app_id
            if user:
                name = app_id + '/' + user
            else:
                name = app_id
        else:
            name = 'anonymous'

        self.path = '/facebook/' + name
        self.logger = logging.getLogger('sparts.fb_dbus.%s' %
                                        self.path.replace('/', '.'))
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.APIService',
                         in_signature='sa{ss}', out_signature='v',
                         async_callbacks=('success_cb', 'error_cb'),)
    def get(self, endpoint, params, success_cb=None, error_cb=None):
        url = self.makeURL(endpoint, **params)
        self.getPage(url, success_cb, error_cb)

    @dbus.service.method(dbus_interface='org.sparts.fb_dbus.APIService',
                         in_signature='s', out_signature='v',
                         async_callbacks=('success_cb', 'error_cb'),)
    def fql(self, query, success_cb=None, error_cb=None):
        return self.get('/fql', {'q': query}, success_cb, error_cb)


class FBAnonymousAPIDBusObject(FBAPIDBusObject):
    def __init__(self, bus):
        FBAPIDBusObject.__init__(self, bus)


class FBAppAPIDBusObject(FBAPIDBusObject):
    def __init__(self, bus, app_id, access_token):
        FBAPIDBusObject.__init__(self, bus, app_id, access_token=access_token)

class FBUserAPIDBusObject(FBAPIDBusObject):
    pass
