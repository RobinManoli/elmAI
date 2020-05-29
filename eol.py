import psutil
import win32api, win32process, win32gui
import re, time
import ctypes

# ----------------------
# from old elma-ai ps.py
# ----------------------
def get_pid(name="eol"):
    "Return pid (process id) for the first process which contains the string name"
    pids = psutil.pids()

    result = None
    for pid in pids:
        try:
            ps = psutil.Process(pid)
        except psutil._exceptions.NoSuchProcess:
            # perhaps it tried to load a process which has been killed?
            pass
        if name in ps.name():
            result = ps.pid
            print( "%s running with pid: %d" % (ps.name(), ps.pid) )
            break

    if not result:
        print("*%s*.exe not running." % (name))
    return result

def get_base_addr(pid):
    # https://stackoverflow.com/q/19822852
    PROCESS_ALL_ACCESS = 0x1F0FFF
    #hwnd = win32ui.FindWindow(None, processName).GetSafeHwnd()
    #pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    processHandle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    modules = win32process.EnumProcessModules(processHandle)
    processHandle.close()
    result = modules[0]
    return result


# https://stackoverflow.com/a/2091530
class WindowMgr:
    """
    Encapsulates some calls to the winapi for window management
    Finds a window and activates (or alt-tabs to) it, using ps.w.set_foreground()
    """

    def __init__ (self):
        """Constructor"""
        self._handle = None
        #self.base_address = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd
            #self.base_address = win32gui.GetModuleHandle(local.elmaexec) # not working
            #pid = win32process.GetWindowThreadProcessId(hwnd) # works
            #print("hwnd:", hwnd, self.base_address)

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_as_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)

# ---------------------------
# from old elma-ai readmem.py
# ---------------------------
def read_process_memory(pid, address, size=0, ctype='str', allow_partial=False):
    if ctype == 'str':
        buf = (ctypes.c_char * size)()
        #c_char = ctypes.c_char()
    elif ctype == 'double':
        #buf = (ctypes.c_byte * 8)() # works but creates byte array
        buf = (ctypes.c_double * 1)()
        size = 8
        #nread = ctypes.c_ulong(0) # works but returns an array
        #nread = ctypes.c_double(0)
        #ptr = ctypes.cast(nread, ctypes.POINTER(ctypes.c_ulong)) # https://stackoverflow.com/a/1363344
    hProcess = kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
    nread = SIZE_T()
    ptr = ctypes.byref(nread)
    try:
        #print('Reading %d bytes from %4x...' % (size, address))
        kernel32.ReadProcessMemory(hProcess, address, buf, size, ptr)
        #print('success:', buf)
        #address = ctypes.c_void_p(address) # if looking for int?
        #ctypes.memmove(ctypes.byref(c_char), buf, ctypes.sizeof(c_char)*size)
    except WindowsError as e:
        if not allow_partial or e.winerror != ERROR_PARTIAL_COPY:
            raise
        print(e)
    finally:
        kernel32.CloseHandle(hProcess)
    return buf[:nread.value]

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
PROCESS_VM_READ = 0x0010
SIZE_T = ctypes.c_size_t
def process_position(pid, base_addr):
    try:
        # retrieved from level
        #self.start_x = read_process_memory(pid, base_addr+0x000538D0, ctype='double', allow_partial=True)[0]
        #self.start_y = read_process_memory(pid, base_addr+0x000538D8, ctype='double', allow_partial=True)[0]
        #self.x = read_process_memory(pid, base_addr+0x53A20, ctype='double', allow_partial=True)[0] # torso or general x
        #self.y = read_process_memory(pid, base_addr+0x53A28, ctype='double', allow_partial=True)[0]
        head_x = read_process_memory(pid, base_addr+0x53B30, ctype='double', allow_partial=True)[0] # head 0x453B30
        print( head_x )
        """
        self.x = read_process_memory(pid, base_addr+0x53B30, ctype='double', allow_partial=True)[0] # head 0x453B30
        self.y = read_process_memory(pid, base_addr+0x53B38, ctype='double', allow_partial=True)[0] # 0x453B18?
        self.lwx = read_process_memory(pid, base_addr+0x53A88, ctype='double')[0] # first (left?) wheel x value
        self.lwy = read_process_memory(pid, base_addr+0x53A90, ctype='double')[0] # first wheel y value
        self.rwx = read_process_memory(pid, base_addr+0x53AF0, ctype='double')[0] # second (right?) wheel x value
        self.rwy = read_process_memory(pid, base_addr+0x53AF8, ctype='double')[0] # second wheel y value
        self.vx = read_process_memory(pid, base_addr+0x53A30, ctype='double')[0] # x speed
        self.vy = read_process_memory(pid, base_addr+0x53A38, ctype='double')[0] # y speed
        self.turn = read_process_memory(pid, base_addr+0x53B20, size=2)[0] # turn
        self.distance = self._distance()"""
        #self.time = read_process_memory(pid, base_addr+0x9D2AB4, size=2)[0] #
        #print( self.distance )
        #self.rotation = self._rotation()
    except IndexError:
        raise


# ---------------------------
# from old elma-ai keyinput.py
# ---------------------------
SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def Key(hexKeyCode, sleepTime=0.02):
    """
    Seems to take at least 2 hundreds of a second to make sure the keypress is actually registered into eol
    """
    #print("Pressing %04x for %.03f" % (hexKeyCode, sleepTime))
    PressKey(hexKeyCode)
    time.sleep(sleepTime)
    ReleaseKey(hexKeyCode)
    time.sleep(sleepTime)


# ---------------------------
# from old elma-ai ai.py
# ---------------------------
# directx scan codes http://www.gamespp.com/directx/directInputKeyboardScanCodes.html
DIK_ESCAPE = 0x01
DIK_RETURN = 0x1C 
DIK_LSHIFT = 0x2A
DIK_LCONTROL = 0x1D
DIK_SPACE = 0x39
DIK_W = 0x11
DIK_A = 0x1E
DIK_S = 0x1F
DIK_D = 0x20


if __name__ == "__main__":
    # print eol pid and base addr
    eol_pid = get_pid("eol")
    base_addr = get_base_addr( eol_pid )
    #print( eol_pid, base_addr )
    # init handling Elasto Mania window
    windowMgr = WindowMgr()
    windowMgr.find_window_wildcard("Elasto Mania")

    windowMgr.set_as_foreground() # alt tab to "Elasto Mania"
    time.sleep(0.1) # wait before done
    Key(DIK_RETURN) # start level
    process_position(eol_pid, base_addr) # get observation
    Key(DIK_ESCAPE) # exit level

