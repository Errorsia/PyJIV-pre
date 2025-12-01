import threading
import time
from abc import ABC, abstractmethod


class WorkerManager:
    def __init__(self, logic, gui):
        super().__init__()
        self.logic = logic
        self.gui = gui
        self.workers = []

        self.threads = {}

        self.init_workers()
        self.start_all()

    def init_workers(self):
        self.workers.append(TopMostWorker(50, self.logic, self.gui))

    def start_all(self):
        for worker in self.workers:
            thread = threading.Thread(target=worker.start, daemon=True)
            self.threads[worker] = thread
            thread.start()

    def stop_all(self):
        """停止所有 worker 并安全退出线程"""
        for worker, thread in self.threads.items():
            worker.stop()
            # 如果不是 daemon，可以 join 等待线程结束
            if thread.is_alive():
                thread.join()


class BaseWorkerInterface(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError("Subclasses must implement start()")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("Subclasses must implement stop()")

    @abstractmethod
    def run_task(self):
        raise NotImplementedError("Subclasses must implement run_task()")


class TopMostWorker(BaseWorkerInterface):
    def __init__(self, interval, logic, gui):
        """
        :param interval: millisecond
        :param logic:
        :param gui:
        """
        super().__init__()

        self.interval = interval / 1000
        self.logic = logic
        self.gui = gui

        self.run = True
        self.hwnd = None

    def start(self):
        self.init_hwnd()
        self.run_task()

    def stop(self):
        self.run = False

    def run_task(self):
        # Set top most
        while self.run:
            self.logic.set_window_top_most(self.hwnd)
            time.sleep(self.interval)

    def init_hwnd(self):
        self.hwnd = int(self.gui.winId())
        print(f'Hwnd: {self.hwnd}')
