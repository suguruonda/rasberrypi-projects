import http.client
import select
import socket
import time

class PyFZ1000:
    """ Class for interfacing with Panasonic DMC-FZ1000 """
    def __init__(self):
        
        #self.wifi_ssid = 'FZ1000-0CE9E0'
        #self.wifi_password = 'a90b6860ce9e0'
        self.wifi_ssid = 'FZ1000-944147'
        self.wifi_password = 'afcdbb3944147'
        self.cam_ip = '192.168.54.1'
        self.local_preview_port = 52700
        self.single_frame = ''

    def enter_control(self):
        self.issue_command_string('mode=camcmd&value=recmode')

    def exit_control(self):
        self.issue_command_string('mode=camcmd&value=playmode')

    def snap_photo(self):
        self.issue_command_string('mode=camcmd&value=capture')

    def get_state(self):
        self.issue_command_string('mode=getstate')

    def get_capability_info(self):
        self.issue_command_string('mode=getinfo&type=capability')

    def get_curmenu_info(self):
        self.issue_command_string('mode=getinfo&type=curmenu')

    def get_lens_info(self):
        self.issue_command_string('mode=getinfo&type=lens')

    def get_setting_exteleconv(self):
        self.issue_command_string('mode=getsetting&type=ex_tele_conv')

    def get_setting_touchtype(self):
        self.issue_command_string('mode=getsetting&type=touch_type')
    
    def zoom_in(self):
        self.issue_command_string('mode=camcmd&value=tele-normal')
    
    def zoom_out(self):
        self.issue_command_string('mode=camcmd&value=wide-normal')

    def zoom_stop(self):
        self.issue_command_string('mode=camcmd&value=zoomstop')

    def issue_command_string(self,command):
        CON = http.client.HTTPConnection(self.cam_ip)
        CON.request('get','/cam.cgi?%s'%command)
        RESP = CON.getresponse()
        print('RESPONSE: %s' % RESP.read())

        # Get frames as streamed in live preview
    def start_preview(self):
        print('foo 0')
        udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        #udp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)

        self.issue_command_string('mode=startstream&value=%s'%self.local_preview_port)
        #s1.bind(('127.0.0.1', self.local_preview_port))
        #s1.bind(('0.0.0.0', self.local_preview_port))
        udp.bind(('', self.local_preview_port))
            #s1.bind(('192.168.54.10', self.local_preview_port))
        print('foo 1')
        receiving = True
        while receiving:
            inputready,outputready,exceptready = select.select([udp],[],[])
            for s in inputready:
                print('have input waiting on %s' % s)
                try:
                    while True:
                        data,addr = s.recvfrom(64000)
                        print('RECEIVED UDP')
            #print data 
            #print addr
            #print x
                except:
                    print('error')
                    receiving = False
                    
    def one_frame(self):
        udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.issue_command_string('mode=startstream&value=%s'%self.local_preview_port)
        udp.bind(('', self.local_preview_port))
        inputready,outputready,exceptready = select.select([udp],[],[])
        for s in inputready:
            print('have input waiting on %s' % s)
            count = 0
            while count < 17:
                data,addr = s.recvfrom(64000)
                print('RECEIVED UDP from %s: type is %s' % (addr, type(data)))
                self.single_frame += data
                count += 1
                

if __name__ == "__main__":
    p = PyFZ1000()
    p.enter_control()
    p.zoom_in()
    time.sleep(2.4)
    p.zoom_stop()
    p.snap_photo()
