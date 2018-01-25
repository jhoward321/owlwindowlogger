
"""
Originally from https://github.com/seanbuscay
"""

import wx, wx.adv
import psutil #http://code.google.com/p/psutil/wiki/Documentation#Classes
import win32api
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
import datetime
import jsonlogwrite as logwrite

def get_threadname(HWND):
    "Return process info about a window handle id"
    pprocess = GetWindowThreadProcessId(HWND)
    p = psutil.Process(pprocess[1])
    return p

class TaskBarApp(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title, size=(1, 1), style=wx.FRAME_NO_TASKBAR | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.ICON_STATE = 1
        self.ID_ICON_TIMER = wx.NewId()
        self.tbicon = wx.adv.TaskBarIcon()
        icon = wx.Icon('logon.ico', wx.BITMAP_TYPE_ICO)
        self.tbicon.SetIcon(icon, 'Logging')
        self.tbicon.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.tbicon.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)
        self.Bind(wx.EVT_TIMER, self.on_timer, id=self.ID_ICON_TIMER)
        self.SetIconTimer()
        self.Show(True)
        self.last_input = 0
        self.is_idle = False
        self.logfile = "logs/" + datetime.datetime.now().strftime('%Y%m%d.log')
        self.logger_check = 0

        # Startup logging
        logwrite.write(dict(log_message="Startup"), self.logfile)
        self.new_active_window()
        
    def OnTaskBarLeftDClick(self, evt):
        if self.ICON_STATE == 0:
            self.StartIconTimer()
            icon = wx.Icon('logon.ico', wx.BITMAP_TYPE_ICO)
            self.tbicon.SetIcon(icon, 'Logging')
            self.ICON_STATE = 1
        else:
            self.StopIconTimer()
            icon = wx.Icon('logoff.ico', wx.BITMAP_TYPE_ICO)
            self.tbicon.SetIcon(icon, 'Not Logging')
            self.ICON_STATE = 0
 
    def OnTaskBarRightClick(self, evt):
        # @todo: Find better way to make sure all threads close.
        logwrite.write(dict(log_message="user shutdown, right clicked"), self.logfile)
        self.StopIconTimer()
        self.tbicon.Destroy()
        self.Close(True)
        wx.GetApp().ProcessIdle()
        wx.GetApp().Exit()
        wx.Exit()
       
    def SetIconTimer(self):
        self.icontimer = wx.Timer(self, self.ID_ICON_TIMER)
        self.icontimer.Start(1000)
 
    def StartIconTimer(self):
        try:
            self.icontimer.Start(1000)
            logwrite.write(dict(log_message="Starting timer"), self.logfile)
            self.new_active_window()
        except:
            pass
 
    def StopIconTimer(self):
        try:
            self.icontimer.Stop()
            logwrite.write(self.data, self.logfile)
            logwrite.write(dict(log_message="Timer stopped"), self.logfile)
            self.new_active_window()
        except:
            pass
 
    def on_timer(self, evt):
        last_input = win32api.GetLastInputInfo()
        if self.last_input == last_input:
            self.is_idle = True
        elif last_input > self.last_input and self.is_idle:
            idle_secs = (last_input - self.last_input) / 1000.0
            if idle_secs > 5:
                self.data['idle_seconds'] = self.data['idle_seconds'] + idle_secs
            self.is_idle = False
        self.last_input = last_input

        # If current window is different from the last time we checked, log the info about
        # the previous one and start tracking the current one
        active_hwnd = GetForegroundWindow()
        window_title = GetWindowText(active_hwnd)
        if self.data['hwnd'] != active_hwnd or self.data['window_title'] != window_title:
            self.data['end_timestamp'] = str(datetime.datetime.now())
            logwrite.write(self.data, self.logfile)
            self.new_active_window()

        # update the log filename every 120s
        self.logger_check += 1
        if self.logger_check % 120 == 0:
            self.logfile = "logs/" + datetime.datetime.now().strftime('%Y%m%d.log')
            self.logger_check = 0

    def new_active_window(self):
        self.data = {}

        active_hwnd = GetForegroundWindow()
        self.data['hwnd'] = active_hwnd
        self.data['window_title'] = GetWindowText(active_hwnd)

        procinfo = get_threadname(active_hwnd)
        self.data['process_name'] = procinfo.name()
        self.data['pid'] = procinfo.pid
        self.data['idle_seconds'] = 0.0
        self.data['start_timestamp'] = str(datetime.datetime.now())
    
 
class MyApp(wx.App):
    def OnInit(self):
        frame = TaskBarApp(None, -1, ' ')
        frame.Center(wx.BOTH)
        frame.Show(True)
        return True
 
def main():
    app = MyApp(0)
    app.MainLoop()
 
if __name__ == '__main__':
    main()
