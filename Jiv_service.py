import threading
from abc import ABC, abstractmethod

import pywintypes


class ServiceManager:
    def __init__(self, logic, gui):
        super().__init__()
        self.logic = logic
        self.gui = gui
        self.services = []

        self.threads = {}

        self.init_services()
        self.start_all()

    def init_services(self):
        self.services.append(TopMostService(50, self.logic, self.gui))

    def start_all(self):
        for service in self.services:
            thread = threading.Thread(target=service.start, daemon=True)
            self.threads[service] = thread
            thread.start()

    def stop_all(self):
        """Stop services and quit"""
        for service, thread in self.threads.items():
            print(service, thread)
            service.stop()

            # May cause deadlock
            # If not daemon, wait until lifelong_threads end
            # if thread.is_alive():
            #     thread.join()


class BaseServiceInterface(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError("Subclasses must implement start()")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Subclasses must implement stop()")

    @abstractmethod
    def run_task(self):
        raise NotImplementedError("Subclasses must implement run_task()")


class TopMostService(BaseServiceInterface):
    def __init__(self, interval, logic, gui):
        """
        :param interval: millisecond
        :param logic:
        :param gui:
        """
        super().__init__()

        self.stop_flag = threading.Event()
        self.interval = interval / 1000
        self.logic = logic
        self.gui = gui

        self.run = True
        self.hwnd = None

    def start(self):
        self.init_hwnd()
        self.run_task()

    def stop(self):
        self.stop_flag.set()

    def run_task(self):
        while not self.stop_flag.is_set():
            try:
                self.logic.set_window_top_most(self.hwnd)
            except pywintypes.error as err:  # type: ignore
                print('pywintypes.error')
                print(err)
            except Exception as err:
                print(err)
            if self.stop_flag.wait(self.interval):
                break

    # def stop(self):
    #     self.run = False
    #     print('get stop signal')
    #
    # def run_task(self):
    #     # Set top most
    #     while self.run:
    #         print(self.run)
    #         self.logic.set_window_top_most(self.hwnd)
    #         time.sleep(self.interval)

    def init_hwnd(self):
        self.hwnd = int(self.gui.winId())
        print(f'Hwnd: {self.hwnd}')
