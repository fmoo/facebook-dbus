from sparts.tasks.dbus import DBusServiceTask
from fb_dbus.dbus import FBAccessDBusObject

class FBDBusServiceTask(DBusServiceTask):
    BUS_NAME = 'org.sparts.FBDbus'

    def addHandlers(self):
        super(FBDBusServiceTask, self).addHandlers()
        self.access = FBAccessDBusObject(self.bus)
