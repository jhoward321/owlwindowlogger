
"""
Originally from https://github.com/seanbuscay
"""

import wx
import psutil #http://code.google.com/p/psutil/wiki/Documentation#Classes
import win32api
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
from time import strftime, localtime, time
import jsonlogwrite as logwrite

def get_idle_duration():
    "Returns idle time in seconds"
    millis = win32api.GetTickCount() - win32api.GetLastInputInfo()
    return millis / 1000.0
 
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
        self.tbicon = wx.TaskBarIcon()
        icon = wx.Icon('logon.ico', wx.BITMAP_TYPE_ICO)
        self.tbicon.SetIcon(icon, 'Logging')
        self.tbicon.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.tbicon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)
        self.Bind(wx.EVT_TIMER, self.Log, id=self.ID_ICON_TIMER)
        self.SetIconTimer()
        self.Show(True)
        # setup logging
        self.LogFile            = 'logs/' + strftime("%Y%m%d", localtime())
        # begin the data dictionary to be written as json entries in log
        self.Data               = {}
        # call SetFreshData() to get time and any other available data
        self.SetFreshData()
        self.Data['Message'] = 'Starting a new logging session.'
        # write a session startup entry
        logwrite.Write(self.Data,self.LogFile)
        # most always set fresh data after logging
        self.SetFreshData()
        
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
        self.StopIconTimer()
        self.tbicon.Destroy()
        self.Close(True)
        self.Data['Message'] = 'Owl Timer Shutting Down.'
        logwrite.Write(self.Data,self.LogFile)
        wx.GetApp().ProcessIdle()
        wx.GetApp().Exit()
        wx.Exit()
       
    def SetIconTimer(self):
        self.icontimer = wx.Timer(self, self.ID_ICON_TIMER)
        self.icontimer.Start(1000)

 
    def StartIconTimer(self):
        try:
            self.icontimer.Start(1000)
            self.Data['Message'] = 'Starting timer.'
            logwrite.Write(self.Data,self.LogFile)
            self.SetFreshData()
        except:
            pass
 
    def StopIconTimer(self):
        try:
            self.icontimer.Stop()
            self.Data['Message'] = 'Stopping timer.'
            logwrite.Write(self.Data,self.LogFile)
            self.SetFreshData()
        except:
            pass
 
    def Log(self, evt):
        idle_duration = get_idle_duration()
        if self.Data['Idle'] < idle_duration:
            self.Data['Idle'] = idle_duration
      
        if self.Data['Idle'] > idle_duration:
            # Lets log the idle time if we've been idle for more than 5 minutes
            if self.Data['Idle'] > 5*60:
                self.Data['Message'] = "idle_log"
                logwrite.Write(self.Data, self.LogFile)
                del self.Data['Message']

            self.Data['TotalIdle'] = self.Data['TotalIdle'] + self.Data['Idle']
            self.Data['Idle'] = 0

        # If current window is different from the last time we checked, log the info about
        # the previous one and start tracking the current one
        if self.Data['Active'] != GetForegroundWindow():
            try:
                p = get_threadname(self.Data['Active'])
                self.Data['AppThread']   = p.name()
                self.Data['AppThreadID'] = p.pid
            except:
                self.Data['AppThread'] = "Unknown"
                self.Data['AppThreadID'] = -1
            self.Data['WinEnd'] = self.Now()
            self.Data['date_end_time']   = strftime("%d %b %Y - %H:%M:%S")
            logwrite.Write(self.Data,self.LogFile)
            # reset data after log is written.
            self.SetFreshData()

    def SetFreshData(self):
        self.Data.clear()
        foreground_pid = GetForegroundWindow()
        self.Data['Active'] = foreground_pid
        self.Data['ActiveText'] = GetWindowText(foreground_pid)
        self.Data['Idle']       = 0
        self.Data['TotalIdle']  = 0
        self.Data['WinStart']   = self.Now()
        self.Data['date_start_time'] = strftime("%d %b %Y - %H:%M:%S")
    
    def Now(self):
        localtime = int(time()) 
        return localtime

 
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
