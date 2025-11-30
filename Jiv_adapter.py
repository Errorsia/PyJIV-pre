# adapter.py
# from threading import Thread

# from typing import Protocol

from PySide6.QtCore import QObject, Signal, QTimer, QThread


class AdapterManager(QObject):
    signal = Signal(str, object)

    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.workers = []
        # self.workers: list[BaseWorkerProtocol] = []
        # self.threads: dict[BaseWorkerProtocol, QThread] = {}

        self.threads = {}

        self.init_workers()
        self.start_all()

    def init_workers(self):
        self.workers.append(MonitorWorker(self.logic, 1000))
        # self.workers.append(DatabaseWorker(logic, 2000))
        # self.workers.append(NetworkWorker(logic, 5000))

    # def start_workers(self):
    #
    #     for worker in self.workers:
    #         thread = QThread()
    #
    #         worker.moveToThread(thread)
    #
    #         thread.started.connect(worker.start)
    #         worker.stateReady.connect(self.signal)
    #
    #         self.threads.append(thread)
    #
    #         thread.start()
    #         worker.start()

    def start_all(self):
        for worker in self.workers:
            thread = QThread()
            worker.moveToThread(thread)

            thread.started.connect(worker.start)
            # 用 lambda 包装，把 worker 类名和结果一起发出去
            worker.value.connect(lambda result, w=worker:
                                      self.signal.emit(type(w).__name__, result))

            self.threads[worker] = thread
            thread.start()

    def stop_all(self):
        """停止所有 worker 并安全退出线程"""
        for worker, thread in self.threads.items():
            worker.stop()
            thread.quit()
            thread.wait()


class BaseWorkerInterface:
    def start(self):
        raise NotImplementedError("Subclasses must implement start()")

    def stop(self):
        raise NotImplementedError("Subclasses must implement stop()")

    def run_task(self):
        raise NotImplementedError("Subclasses must implement run_task()")


# class BaseWorkerProtocol(Protocol):
#     def start(self) -> None: ...
#
#     def stop(self) -> None: ...
#
#     def run_task(self) -> None: ...


# class BaseWorkerInterface(ABC):
#     @abstractmethod
#     def start(self):
#         raise NotImplementedError("Subclasses must implement start()")
#
#     @abstractmethod
#     def stop(self):
#         raise NotImplementedError("Subclasses must implement stop()")
#
#     @abstractmethod
#     def run_task(self):
#         raise NotImplementedError("Subclasses must implement run_task()")


# class MonitorAdapter(QObject):
#     stateReady = Signal(bool)
#
#     def __init__(self, logic):
#         super().__init__()
#         self.thread = QThread()
#         self.worker = MonitorWorker(logic, 1000)
#         self.worker.moveToThread(self.thread)
#
#         self.thread.started.connect(self.worker.start)
#         self.worker.stateReady.connect(self.stateReady)
#
#         self.thread.start()
#
#     def stop(self):
#         self.worker.stop()
#         self.thread.quit()
#         self.thread.wait()


class MonitorWorker(QObject, BaseWorkerInterface):
    value = Signal(bool)

    def __init__(self, logic, interval=1000):
        super().__init__()
        self.logic = logic
        self.timer = QTimer(self)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.run_task)
        self.last_result = None

    def start(self):
        self.timer.start()
        # QTimer.singleShot(0, self.check_state)

    def stop(self):
        self.timer.stop()

    def run_task(self):
        state = self.check_state()
        if state is not self.last_result:
            self.last_result = state
            self.value.emit(state)

    def check_state(self):
        return self.logic.get_studentmain_state()
