import ctypes
import platform
import re
import sys

import requests
import win32com.client
from packaging import version
# import ctypes.wintypes as wintypes
import subprocess

import psutil
import win32gui, win32con, win32api


class JIVLogic:
    def __init__(self):
        self.system_info = None

        self.preparation()



    def preparation(self):
        self.system_info = self.get_system_info()


    def get_system_info(self):
        win_ver = sys.getwindowsversion()
        system_info = {
            "system": platform.system(),  # Windows
            "release": platform.release(),  # Major (e.g. 10, 11)
            "version": platform.version(),  # build version
            "major": win_ver.major,  # major version
            "minor": win_ver.minor,  # minor version
            "build": win_ver.build,  # build version
            "platform": win_ver.platform,  # platform ID
            "service_pack": win_ver.service_pack,
            "architecture": platform.architecture(),  # (64bit, 32bit)
            "hotfixes": self.get_hotfixes_winapi()
        }
        return system_info

    @staticmethod
    def get_hotfixes_winapi():
        update_session = win32com.client.Dispatch("Microsoft.Update.Session")
        update_searcher = update_session.CreateUpdateSearcher()
        history_count = update_searcher.GetTotalHistoryCount()
        history = update_searcher.QueryHistory(0, history_count)

        hotfixes = []
        for entry in history:
            match = re.search(r"(KB\d+)", entry.Title)
            if match:
                hotfixes.append({
                    "kb": match.group(1),
                    "date": entry.Date,
                    "result": entry.ResultCode
                })
        return hotfixes

    @staticmethod
    def get_hotfixes_powershell():
        cmd = 'powershell "Get-HotFix | Select-Object -Property HotFixID, InstalledOn"'
        output = subprocess.check_output(cmd, shell=True).decode(errors="ignore")
        hotfixes = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("kb"):
                parts = line.split(None, 1)
                if len(parts) == 2:
                    hotfixes.append({
                        "KB": parts[0],
                        "InstalledOn": parts[1]
                    })
        return hotfixes

    @staticmethod
    def is_admin():
        """Checking whether programme has administrator privilege"""

        authority = ctypes.windll.shell32.IsUserAnAdmin()
        return bool(authority)

    @staticmethod
    def get_studentmain_state():
        process_name = 'studentmain.exe'
        process_iter = psutil.process_iter()
        for proc in process_iter:
            try:
                if proc.name().lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    @staticmethod
    def set_window_top_most(hwnd):
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                              0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def set_window_display_affinity(self, hwnd):
        if self.system_info["major"] >= 10 and self.system_info["build"] >= 19041:
            ctypes.windll.user32.SetWindowDisplayAffinity(int(hwnd), 0)
        else:
            ctypes.windll.user32.SetWindowDisplayAffinity(int(hwnd), 0x11)

    @staticmethod
    def taskkill(process_name):
        state = subprocess.run(['TASKKILL', '-F', '-IM', process_name, '-T']).returncode

        if state == 0:
            return True
            # self.logger.info(f'The process ({process_name}) has been terminated (Return code {state})')

        elif state == 128:
            return False
            # self.logger.warning(f'The process ({process_name}) not found (Return code {state})')

        elif state == 1:
            return False
            # self.logger.warning(
                # f'The process ({process_name}) could not be terminated (Return code {state})')

        else:
            return False
            # self.logger.warning(f'Unknown Error (Return code {state})')

    @staticmethod
    def get_pid_form_process_name(process_name):
        process_iter = psutil.process_iter()
        for proc in process_iter:
            try:
                if proc.name().lower() == process_name.lower():
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return None

    @staticmethod
    def terminate_process(pid):

        # noinspection PyUnresolvedReferences
        h_process = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
        if not h_process:
            # noinspection PyUnresolvedReferences
            raise Exception(f"OpenProcess failed, error={win32api.GetLastError()}")

        # noinspection PyUnresolvedReferences
        win32api.TerminateProcess(h_process, 1) # return code 1
        # if not success:
            # noinspection PyUnresolvedReferences
            # raise Exception(f"TerminateProcess failed, error={win32api.GetLastError()}")

        # h_process = win32api.OpenProcess(win32con.PROCESS_TERMINATE | win32con.SYNCHRONIZE, False, pid)
        # if not h_process:
        #     raise Exception(f"OpenProcess failed, error={win32api.GetLastError()}")
        #
        # success = win32api.TerminateProcess(h_process, 1)
        # if not success:
        #     raise Exception(f"TerminateProcess failed, error={win32api.GetLastError()}")
        #
        # result = win32event.WaitForSingleObject(h_process, 5000)
        # if result == win32event.WAIT_OBJECT_0:
        #     exit_code = win32process.GetExitCodeProcess(h_process)
        #     print(f"Process terminated with exit code {exit_code}")
        # else:
        #     print("Timeout waiting for process to terminate")


    # # load kernel32.dll
    # kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    #
    # # Define Function Prototype
    # TerminateThread = kernel32.TerminateThread
    # TerminateThread.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    # TerminateThread.restype = wintypes.BOOL
    #
    # TerminateProcess = kernel32.TerminateProcess
    # TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    # TerminateProcess.restype = wintypes.BOOL
    #
    # PROCESS_TERMINATE = 0x0001
    # OpenProcess = kernel32.OpenProcess
    # OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    # OpenProcess.restype = wintypes.HANDLE
    #
    # pid = 1234
    # hProcess = OpenProcess(PROCESS_TERMINATE, False, pid)
    #
    # if hProcess:
    #     result = TerminateProcess(hProcess, 1)  # return code 1
    #     print("TerminateProcess result:", result)
    # else:
    #     print("Failed to open process")

    # # load ntdll.dll
    # ntdll = ctypes.WinDLL("ntdll")
    #
    # # Define NtTerminateProcess function Prototype
    # NtTerminateProcess = ntdll.NtTerminateProcess
    # NtTerminateProcess.argtypes = [wintypes.HANDLE, wintypes.NTSTATUS]
    # NtTerminateProcess.restype = wintypes.NTSTATUS
    #
    # # load kernel32.dll to open process
    # kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    #
    # OpenProcess = kernel32.OpenProcess
    # OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    # OpenProcess.restype = wintypes.HANDLE
    #
    # CloseHandle = kernel32.CloseHandle
    # CloseHandle.argtypes = [wintypes.HANDLE]
    # CloseHandle.restype = wintypes.BOOL
    #
    # # Define constant
    # PROCESS_TERMINATE = 0x0001
    #
    # pid = 1234
    # hProcess = OpenProcess(PROCESS_TERMINATE, False, pid)
    #
    # if hProcess:
    #     status = NtTerminateProcess(hProcess, 1)  # Exit code 1
    #     print(f"NtTerminateProcess returns NTSTATUS: 0x{status:08X}")
    #     CloseHandle(hProcess)
    # else:
    #     print("cannot open process")


