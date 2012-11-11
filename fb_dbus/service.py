from sparts.vservice import VService
from sparts.tasks.twisted import TwistedReactorTask
from sparts.tasks.dbus import DBusMainLoopTask
from fb_dbus.tasks import FBDBusServiceTask

class FBDBusService(VService):
    TASKS=[DBusMainLoopTask, FBDBusServiceTask, TwistedReactorTask]
    REQUIRE_TWISTED = True

if __name__ == '__main__':
    FBDBusService.initFromCLI()
