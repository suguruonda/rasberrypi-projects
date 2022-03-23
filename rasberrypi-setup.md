## This is memo for initial rasberry pi setup (raspbian 11.2).
### change root password
'''
sudo passwd root
'''

### add user
'''
sudo adduser [new user name]
'''

### copy pi user group to new user

#### comfirm pi user group
'''
groups pi
'''

'''
sudo usermod -G adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,render,netdev,pi,spi,i2c,gpio,lpadmin [new user]
'''

#### confirm new user group
'''
groups [new user]
'''

### copy pi user folder to new user
'''
sudo cp -r /home/pi/* /home/[new user]
'''

### turn off auto login
'''
sudo raspi-config
'''

#### select 1 System Options -> S5 Boot / Auto Login -> B1 Console

'''
reboot
'''

### delete pi user
#### login as new user
'''
sudo userdel -r pi
'''
#### check pi user is deleted
'''
id -a pi
'''
### change default user
'''
sudo nano /etc/systemd/system/autologin@.service
'''
'''
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
->ExecStart=-/sbin/agetty --autologin [new user] --noclear %I $TERM
'''
### change desktop login
'''
sudo raspi-config
'''

#### select 1 System Options -> S5 Boot / Auto Login -> B3 Desktop
'''
reboot
'''

### Wifi setting(eduroam)
'''
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
'''
#### add this
'''
network={
	ssid="eduroam"
	proto=RSN
	key_mgmt=WPA-EAP
	pairwise=CCMP
	auth_alg=OPEN
	eap=PEAP
	identity="university email address(example:***@byu.edu)"
	password=hash:****
	phase1="peaplabel=0"
	phase2="auth=MSCHAPV2"
	priority=1
}
'''
#### convert your password to hash (****)
##### open terminal
'''
echo -n type_your_eduroam_password | iconv -t utf16le | openssl md4
'''
##### copy output and paste to ****
##### delete your password from commandline history
'''
nano ~/.bash_history
...

#### stop and restart wifi
'''
sudo ifconfig wlan0 down
sudo ifconfig wlan0 up
'''

### fix IP address
#### get router IP address
'''
route -n
'''

#### set fixed IP address
'''
sudo nano /etc/dhcpcd.conf
'''
#### add this
'''
interface wlan0
static ip_address=[your desired IP address]
static routers=[router IP address]
static domain_name_servers=[router IP address] 8.8.8.8 8.8.4.4
'''
### change hostname
'''
sudo nano /etc/hosts
'''
'''
sudo nano /etc/hostname
'''

### SSH setting
#### SSH enable at "rasberry pi"
'''
cd /boot
sudo touch ssh 
reboot
'''
#### make .ssh folder
'''
mkdir ~/.ssh
cmod 700 ~/.ssh
'''

#### make ssh key at "client PC"
'''
ssh-keygen -t rsa
scp -P [port number] nameofyoursshkey.pub username@hostname:/home/username/.ssh
'''
#### copy sshkey at "rasberry pi"
'''
cat nameofyoursshkey.pub >> authorized_keys
chmod 600 authorized_keys
rm ~/.ssh/nameofyoursshkey.pub
'''

#### confirm ssh connection from "client PC"
'''
ssh username@hostname -i sshkey_path
'''

#### change ssh setting at "rasberry pi"
'''
sudo cp sshd_config sshd_config.old
'''
'''
sudo nano sshd_config
'''
#Port 22 -> Port your_desired_port_number

#PermitRootLogin prohibit-password -> PermitRootLogin no

#PasswordAuthentication yes -> PasswordAuthentication no

#PermitEmptyPasswords no -> PermitEmptyPasswords no
'''

'''
sudo /etc/init.d/ssh restart
'''

### set ssh config at "client PC"
'''
cd ~/.ssh
nano config
'''
#### add this
'''
Host hostnameofrasberrypi
  HostName hostnameofrasberrypi
  IdentityFile ~/.ssh/your_sshkey_filename
  User username
  Port portnumber
'''
'''
chmod 600 config
...


