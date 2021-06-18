 ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Alarm and Shutdown",
    "author": "Sergey Metelskiy, Anton Nikitin",
    "version": (1, 2, 1),
    "blender": (2, 80, 0),
    "location": "Output > Alarm and Shutdown tab",
    "description": "Sounds alarm and shutting down computer at render completion",
    "warning": "This version is in Beta",
    "wiki_url": "",
    "category": "Render"}

import bpy
import aud, platform, subprocess, os, threading, smtplib, datetime, traceback
from bpy.props import *
from bpy.app.handlers import persistent
from bpy.types import Operator, Panel, PropertyGroup, AddonPreferences
from email.mime.text import MIMEText

OS = 'WIN' if platform.system().startswith('Win') else 'LIN' #Determine platform prefix
d = '/' if OS == 'WIN' else '-'                              #platform dependent flag
sound_path = os.path.normpath(os.path.dirname(__file__)+'/sounds/')
poweroff_list = [("NONE", "Do Not Shut Down", ""),
                ("POWER_OFF", "Power Off", ""),
                ("RESTART", "Restart", "")]
if OS == 'WIN': poweroff_list.append(("SLEEP", "Sleep", ""))


@persistent
def playSoundAndStartTimer(scene): #Function hooked at render completion event
    global timer
    props = scene.alarm_and_shutdown
    if props.use_alarm_and_shutdown:
        playSound(props.sound_type)
        if props.shutdown_type != 'NONE': #Start a shut-down timer if shut-down type set to enything but NONE
            props.remaining_time = props.timeout_time+3
            timer = threading.Timer(1, countDown)
            timer.start()
        if props.use_send_email:
            sendMail()

def handlerBind(self, context): #callback function bind to use_alarm_and_shutdown checkbox
	H = bpy.app.handlers.render_complete
	if playSoundAndStartTimer not in H: H.append(playSoundAndStartTimer) #it binds playSoundAndStartTimer to handler

def playSound(type='NONE'): #Function that plays selected sound
    soundList = {'SONIC':'Sonic.mp3','MARIO':'Mario.mp3','LODERUNNER':'Lode Runner.mp3','RADIO':'Lighthouse.mp3', 'CUSTOM':''}
    if type != 'NONE':
        Device = aud.Device()
        if type != 'CUSTOM': Sound = aud.Sound(os.path.normpath(sound_path+'/'+soundList[type]))
        else: Sound = aud.Sound(os.path.normpath(bpy.context.preferences.addons[__name__].preferences.filepath))
        try:
            Device.play(Sound.volume(bpy.context.scene.alarm_and_shutdown.alarm_volume/100))
        except:
            print("\a")

def countDown(): #Counting down till shut-down, then compiling os dependent shut-down command, then sending it to os
    global timer, OS
    props = bpy.context.scene.alarm_and_shutdown
    if props.remaining_time > 0:
        print(str(props.remaining_time)+' seconds remaining untill shutdown!')
        props.remaining_time -= 1
        timer = threading.Timer(1, countDown)
        timer.start()
    else:
        #if props.shutdown_type != 'NONE':
        flags = {'RESTART':'r /f' if OS == 'WIN' else 'r now', 'POWER_OFF':'s /f' if OS=='WIN' else 'h now', 'SLEEP':'h'}
        command = 'shutdown {}{}'.format(d, flags[props.shutdown_type])
        if OS == 'LIN': os.system(command)
        subprocess.call(command)

def sendMail():
    prefs = bpy.context.preferences.addons[__name__].preferences
    msgBody = '''
    This is an automatic message, sent by Alarm and Shutdown addon.
    Render of the scene "{0}" in file "{1}" has been completed at {2}
    '''.format(bpy.context.scene.name, bpy.path.basename(bpy.data.filepath), datetime.datetime.now().strftime('%H:%M'))
    msg = MIMEText(msgBody)
    msg["Subject"] = "Your render is completed!"
    msg["From"] = prefs.emailfrom
    msg["To"] = prefs.emailto

    port = ':'+str(prefs.emailport) if prefs.emailport else ''
    s = smtplib.SMTP_SSL(prefs.emailhost+port) if prefs.use_SSL else smtplib.SMTP(prefs.emailhost+port)
    s.connect(prefs.emailhost+port)
    s.ehlo()
    if prefs.use_SSL != True:
        s.starttls()
        s.ehlo()
    s.login(prefs.emailuser, prefs.emailpass)
    try:
        s.sendmail(prefs.emailfrom, prefs.emailto, msg.as_string())
    except Exception as e:
        print('Alarm and Shutdown: email notifications failed. Something went wrong :( \n'+Exception)
    s.quit()
    
class playAlarmSound(bpy.types.Operator): #operator that plays de sound
    bl_description = 'Tests alarm sound'
    bl_idname = 'sound.play_alarm'
    bl_label = 'Play Alarm Sound'
    
    @classmethod
    def poll(cls, context):
        if context.scene.alarm_and_shutdown.sound_type != 'NONE': return True
        return False

    def execute(self, context):
        playSound(bpy.context.scene.alarm_and_shutdown.sound_type)
        return {'FINISHED'}

class abortShutDown(bpy.types.Operator):
    bl_description = 'Abort shutdown timer'
    bl_idname = 'render.abort_shutdown'
    bl_label = 'Abort'
    
    @classmethod
    def poll(cls, context):
        if context.scene.alarm_and_shutdown.remaining_time > 0:
            return True
        return False

    def execute(self, context):
        global timer
        timer.cancel()
        context.scene.alarm_and_shutdown.remaining_time = 0
        return {'FINISHED'}

class alarmAndShutdownPROPS(bpy.types.PropertyGroup): #All the properties utilized by addon
    use_alarm_and_shutdown : BoolProperty(name='Enable', description='Enable shutdown timer',default=False, options={'SKIP_SAVE'}, update=handlerBind)
    timeout_time : IntProperty(name='Timeout/sec', description='Timeout untill shutdown action', min=0, step=1, subtype='TIME')
    sound_type : EnumProperty(items=[
                                ("NONE", "No sound", "No sound plays at render completion", 1),
                                ("SONIC", "Sonic", "", 2),
                                ("MARIO", "Mario", "", 3),
                                ("LODERUNNER", "Lode Runner", "", 4),
                                ("RADIO", "Radio", "", 5),
                                ("CUSTOM", "Custom", "", 6),
                                ], description='Sound type', name='Sound type')
    shutdown_type : EnumProperty(items=poweroff_list,  description='Shutdown type', name='Shutdown type')
    remaining_time : IntProperty()
    alarm_volume : IntProperty(name='Volume', description='Alarm volume level', default=100, min=1, max=100, step=1, subtype='PERCENTAGE')
    use_send_email : BoolProperty(name='Send Email Notification', description='Sends an email with notification on render completion', default=False)
    

bpy.utils.register_class(alarmAndShutdownPROPS)
bpy.types.Scene.alarm_and_shutdown = PointerProperty(type=alarmAndShutdownPROPS)
    

class alarmAndShutdownPANEL(bpy.types.Panel):
    bl_description = 'Sounds alarm and shutting down computer at render completion'
    bl_idname = 'RENDER_PT_alarm'
    bl_label = 'Alarm and Shutdown'
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_context = 'output'
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        props = context.scene.alarm_and_shutdown
        l = self.layout
        m = l.column()
        m.active = props.use_alarm_and_shutdown #Check whether addon function is enabled
        c = m.column(align=True)
        c.prop(props, 'sound_type', text='', icon='SOUND')
        r = c.row(align=True)
        r.prop(props, 'alarm_volume')
        r.operator('sound.play_alarm', text='', icon='OUTLINER_DATA_SPEAKER')
        c = m.column(align=True)
        c.prop(props, 'shutdown_type', text='', icon='QUIT')
        c.prop(props, 'timeout_time')
        c.prop(props, 'use_send_email')
        c = m.column()
        c.scale_y = 3
        if props.remaining_time > 0:
            c.operator('render.abort_shutdown', text='Shut-down timer in progress. Abort.', icon='CANCEL')
        
    def draw_header(self, context):
        l = self.layout
        l.prop(context.scene.alarm_and_shutdown, 'use_alarm_and_shutdown', text='')
    
class AlarmAndShutdownPREF(AddonPreferences):
    bl_idname = __name__

    filepath: StringProperty(name="Custom Audio File", description="Specify location of a custom audio file", subtype="FILE_PATH")
    emailfrom: StringProperty(name="From*", description="Set a correct address FROM where an email will be sent", default="yoursmtp@provider.com")
    emailto: StringProperty(name="To*", description="Set a correct address TO where an email will be sent", default="notification@reciever.com")
    emailhost: StringProperty(name="Host*", description="SMTP server hostname or IP adress")
    emailport: StringProperty(name="Port (optional)", description="SMTP server port")
    use_SSL: BoolProperty(name='Use SSL', description="Whether to use an SSL enctyption (some servers require it)", default=False)
    emailuser: StringProperty(name="User*", description="User login for your SMTP server")
    emailpass: StringProperty(name="Password*", description="User password for your SMTP server")

    def draw(self, context):
        l = self.layout
        r = l.row(align=True)
        r.label(text="Custom Sound File Path:")
        r.prop(self, "filepath", text="")
        l.label(text='Email notification settings', icon='URL')
        r = l.row()
        c = r.column(align=True)
        c.prop(self, 'emailhost')
        c.prop(self, 'emailport')
        c.prop(self, 'use_SSL')
        c1 = r.column()
        c2 = c1.column(align=True)
        c2.prop(self, 'emailuser')
        c2.prop(self, 'emailpass')
        c3 = c1.column(align=True)
        c3.prop(self, 'emailfrom')
        c3.prop(self, 'emailto')
        
toRegister = (alarmAndShutdownPANEL, AlarmAndShutdownPREF, playAlarmSound, abortShutDown)
    
def register():
    for cls in toRegister:
        bpy.utils.register_class(cls)
    handlerBind(None, bpy.context)

def unregister():
    H = bpy.app.handlers.render_complete
    if playSoundAndStartTimer in H:
        bpy.app.handlers.render_complete.remove(playSoundAndStartTimer)
    #bpy.context.scene.alarm_and_shutdown.use_alarm_and_shutdown = False
    for cls in toRegister:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
