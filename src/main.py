from qt import *
from main_window import MainWindow
from codex import DeviceManager
# import qtawesome as qta
# from appdirs import AppDirs
from pathlib import Path


class Application(BaseApplication):
    def __init__(self) -> None:
        super().__init__()
        self.init_app_info()
        
        # self.setQuitOnLastWindowClosed(False)

        # icon = QIcon(qta.icon('fa.circle','fa5s.video', options=[{'color':'gray'}, {'scale_factor':0.5, 'color':'white'}]))
        # self.setWindowIcon(icon)

        self.device_manager = DeviceManager(self)

        # create window
        self.window = MainWindow()
        self.window.show()

    def closeEvent(self, event):
        self.device_manager.close()
        return super().closeEvent(event)

    def init_app_info(self):
        self.setOrganizationName("DaelonCo")
        self.setOrganizationDomain("DaelonCo")
        self.setApplicationName("CodexTester")
        self.setApplicationVersion("v0.1")

        # self.dirs = AppDirs('CodexTester', 'DaelonCo')
        # self.config_dir = self.dirs.user_config_dir

        # # make sure config dir exists
        # Path(self.config_dir).mkdir(parents=True, exist_ok=True)


def run():    
    # Create the Qt Application
    app = Application()

    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    run()