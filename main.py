##############################
#                            #
#        Josh Benson         #
#           2020             #
#                            #
##############################

import os
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import spidev
import os
from time import sleep
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus

spi = spidev.SpiDev()
from pidev.MixPanel import MixPanel
import datetime
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
cyprus.initialize()
global switchPort
global stepperPort
stepperPort = 0

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    global servoPos
    servoPos = 1

    def talonThread(self):
        global talon
        while talon:
            if (cyprus.read_gpio() & 0b0001):
                sleep(.1)
                if (cyprus.read_gpio() & 0b0001):
                    cyprus.set_pwm_values(1, period_value=100000, compare_value=50000,
                                          compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                    cyprus.set_servo_position(1, 1)
            else:
                cyprus.set_servo_position(1, .5)

    def cytronThread(self):
        global cytron
        while cytron:
            if (cyprus.read_gpio() & 0b0010):
                cyprus.set_pwm_values(1, period_value=100000, compare_value=50000,
                                      compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                sleep(.1)
            else:
                cyprus.set_pwm_values(1, period_value=100000, compare_value=0,
                                      compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                sleep(.1)

    def cyp(self):
        pass
        # cyprus.close()
        # cyprus.initialize()
        # cyprus.setup_servo(2)
        # cyprus.set_servo_position(2, .5)

    def motorpressed(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "motors"

    def driverpressed(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "drivers"

    def switchpressed(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "switches"

    def cleanup(self):
        cyprus.set_servo_position(1, .5)
        cyprus.close()
        spi.close()
        GPIO.cleanup()
        quit()


class SwitchScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def lefty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = 'switchMethods'

    def righty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = 'switchMethods1'


class DriverScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def lefty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "cytronMethods"

    def righty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "talonMethods"


class MotorScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def lefty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "stepperMethods"
        pass

    def righty(self):
        SCREEN_MANAGER.transition.direction = 'left'
        SCREEN_MANAGER.current = "servoMethods"


class SwitchMethodsScreen(Screen):
    def back(self):
        global checking
        checking = False
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'switches'

    def startThread(self):
        global checking
        global switchPort
        switchPort = 6
        checking = True
        Thread(target=self.switchThread).start()
        Thread.daemon = True

    def switchThread(self):
        global switchPort
        global checking
        while checking:
            if switchPort == 6:
                val = 0b0001
            elif switchPort == 7:
                val = 0b0010
            elif switchPort == 8:
                val = 0b0100
            if (cyprus.read_gpio() & val):
                sleep(.1)
                if (cyprus.read_gpio() & val):
                    self.ids.toggle_sensing_label.text = "Not Sensing"
                    self.ids.toggle_sensing_label.color = (1, 0, 0, .8)
            else:
                self.ids.toggle_sensing_label.text = "Sensing"
                self.ids.toggle_sensing_label.color = (0, 1, 0, .8)

    def port(self, port):
        global switchPort
        switchPort = port
        self.ids.port_label.text = "Plug into port P" + str(port)


class SwitchMethods1Screen(Screen):
    def back(self):
        global checking
        checking = False
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'switches'

    def startThread(self):
        global checking
        global switchPort
        switchPort = 6
        checking = True
        Thread(target=self.switchThread).start()
        Thread.daemon = True

    def switchThread(self):
        global switchPort
        global checking
        while checking:
            if switchPort == 6:
                val = 0b0001
            elif switchPort == 7:
                val = 0b0010
            elif switchPort == 8:
                val = 0b0100
            if (cyprus.read_gpio() & val):
                sleep(.1)
                if (cyprus.read_gpio() & val):
                    self.ids.toggle_sensing_label.text = "Not Sensing"
                    self.ids.toggle_sensing_label.color = (1, 0, 0, .8)
            else:
                self.ids.toggle_sensing_label.text = "Sensing"
                self.ids.toggle_sensing_label.color = (0, 1, 0, .8)

    def port(self, port):
        global switchPort
        switchPort = port
        self.ids.port_label.text = "Plug into port P" + str(port)
class ServoMethodsScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = "motors"
        cyprus.set_servo_position(1, .5)
        cyprus.initialize()

    def moveServo(self, param):
        global servoPos
        if param == "move":
            cyprus.setup_servo(1)
            if servoPos == 1:
                cyprus.set_servo_position(1, 0)
                servoPos = 0
            else:
                cyprus.set_servo_position(1, 1)
                servoPos = 1
        else:
            cyprus.set_servo_position(1, .5)
            servoPos = 0

    def updateLabel(self, param):
        global servoPos
        if param == "move":
            if servoPos == 1:
                cyprus.set_servo_position(1, 0)
                self.ids.servo_slider.value = 0
                servoPos = 0
            else:
                cyprus.set_servo_position(1, 1)
                servoPos = 1
                self.ids.servo_slider.value = 100
        elif param == "reset":
            cyprus.set_servo_position(1, .5)
            servoPos = 0
            self.ids.servo_slider.value = 50
        val = self.ids.servo_slider.value
        self.ids.percent_label.text = str(val) + "%"
        cyprus.set_servo_position(1, val/100)
        if val > 50:
            servoPos = 1
        else:
            servoPos = 0



class StepperMethodsScreen(Screen):

    # def setSpeed(self, speed):
    #     s1 = stepper(port=stepperPort, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
    #                  steps_per_unit=200, speed=8)
    #     if speed == "fast":
    #         s1.set_speed(8)
    #         s1.start_relative_move(5)
    #     else:
    #         s1.set_speed(2)
    #         s1.start_relative_move(5)

    def startThread(self):
        global checkingSliders
        checkingSliders = True
        Thread(target=self.sliderThread).start()
        Thread.daemon = True

    def sliderThread(self):
        global checkingSliders
        while checkingSliders:
            self.ids.speed_label.text = "Speed: " + str(self.ids.speed_slider.value)
            self.ids.acell_label.text = "Acceleration: " + str(self.ids.acell_slider.value)
            self.ids.decell_label.text = "Deceleration: " + str(self.ids.decell_slider.value)
            self.ids.microstep_label.text = "Microsteps: " + str(self.ids.microstep_slider.value)
            if self.ids.length_mode_button.text == "Steps":
                self.ids.length_label.text = "Steps: " + str(self.ids.length_slider.value)
            else:
                self.ids.length_label.text = "Rotations: " + str(self.ids.length_slider.value)



    def back(self):
        global checkingSliders
        s1 = stepper(port=stepperPort, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                     steps_per_unit=200, speed=8)
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = "motors"
        checkingSliders = False
        s1.free()


    def runControl(self, param):
        s1 = stepper(port=stepperPort, micro_steps=32, hold_current=20, run_current=20, accel_current=20,
                     deaccel_current=20, steps_per_unit=200, speed=8)
        if param == "stop":
            s1.hard_stop()
            s1.free()
        micro_steps = self.ids.microstep_slider.value
        speed = self.ids.speed_slider.value
        acceleration = self.ids.acell_slider.value
        deceleration = self.ids.decell_slider.value
        if self.ids.dir_button.source == 'cw.png':
            direction = 1
        else:
            direction = -1

        s1.set_accel(acceleration)
        s1.set_deaccel(deceleration)


    def toggleDir(self):
        if self.ids.dir_button.source == 'cw.png':
            self.ids.dir_button.source = 'ccw.png'
        else:
            self.ids.dir_button.source = 'cw.png'


    # def one(self, dir):
    #     s1 = stepper(port=stepperPort, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
    #                  steps_per_unit=200, speed=8)
    #     if dir == "for":
    #         s1.start_relative_move(1)
    #     else:
    #         s1.start_relative_move(-1)

    def port(self, port):
        global stepperPort
        stepperPort = port
        self.ids.port_label.text = "Plug into port " + str(port)

    def toggleLegnthMode(self):
        if self.ids.length_mode_button.text == "Steps":
            self.ids.length_mode_button.text = "Rotations"
            self.ids.length_slider.max = 10
        else:
            self.ids.length_mode_button.text = "Steps"
            self.ids.length_slider.max = 1000



class TalonMethodsScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'drivers'
        cyprus.set_servo_position(1, 0.5)

    def updateLabel(self):
        cyprus.initialize()
        cyprus.setup_servo(2)
        spd = self.ids.PWM_slider.value / 100
        if (self.ids.PWM_slider.value > 45) and (self.ids.PWM_slider.value < 55):
            self.ids.talon_label.text = "Neutral"
            self.ids.talon_label.color = (1, .65, 0, .8)
            spd = .5
        elif self.ids.PWM_slider.value > 54:
            s = "Forward " + str(self.ids.PWM_slider.value - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (0, 1, 0, .8)
            spd = spd - .03
        else:
            s = "Backward " + str(self.ids.PWM_slider.value - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (1, 0, 0, .8)
            spd = spd + .03

        cyprus.set_servo_position(2, spd)

    def buttonControl(self, cmd):
        if cmd == "forward":
            self.ids.talon_label.text = "Forward 50.0"
            self.ids.PWM_slider.value = 100
            self.ids.talon_label.color = (0, 1, 0, .8)
            cyprus.set_servo_position(2, 1)

        elif cmd == "back":
            self.ids.talon_label.text = "Backward 50.0"
            self.ids.PWM_slider.value = 0
            self.ids.talon_label.color = (1, 0, 0, .8)
            cyprus.set_servo_position(2, 0)

        else:
            self.ids.talon_label.text = "Neutral"
            self.ids.PWM_slider.value = 50
            self.ids.talon_label.color = (1, .65, 0, .8)
            cyprus.set_servo_position(2, .5)

    def tickArrows(self, way):
        cyprus.initialize()
        cyprus.setup_servo(2)
        num = self.ids.PWM_slider.value
        if way == "up":
            if self.ids.talon_label.text == "Neutral":
                num = 55
            elif num == 45:
                num = 50
            elif num == 100:
                num = 100
            else:
                num += 1
        elif way == "down":
            if self.ids.talon_label.text == "Neutral":
                num = 45
            elif num == 55:
                num = 50
            elif num == 0:
                num = 0
            else:
                num -= 1
        spd = num / 100
        if (num > 45) and (num < 55):
            self.ids.talon_label.text = "Neutral"
            self.ids.talon_label.color = (1, .65, 0, .8)
            self.ids.PWM_slider.value = 50
            spd = .5
        elif num > 54:
            s = "Forward " + str(num - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (0, 1, 0, .8)
            self.ids.PWM_slider.value = num
            spd = spd - .03
        else:
            s = "Backward " + str(num - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (1, 0, 0, .8)
            self.ids.PWM_slider.value = num
            spd = spd + .03

        cyprus.set_servo_position(2, spd)


class CytronMethodsScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'drivers'

    def updateLabel(self):
        cyprus.initialize()
        if (self.ids.PWM_slider.value < 55) and (self.ids.PWM_slider.value > 45):
            self.ids.cytron_label.text = "Neutral"
            self.ids.cytron_label.color = (1, .65, 0, .8)
            val = 0
        elif self.ids.PWM_slider.value > 54:
            s = "Forward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.cytron_label.text = s
            self.ids.cytron_label.color = (0, 1, 0, .8)
            val = (self.ids.PWM_slider.value - 50) * 2000
            direction = 1
        else:
            s = "Backward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.cytron_label.text = s
            self.ids.cytron_label.color = (1, 0, 0, .8)
            val = (50 - self.ids.PWM_slider.value) * 2000
            direction = 0
        cyprus.set_pwm_values(2, period_value=100000, compare_value=val,
                              compare_mode=cyprus.LESS_THAN_OR_EQUAL)

    def buttonControl(self, cmd):
        if cmd == "forward":
            self.ids.cytron_label.text = "Forward 50.0"
            self.ids.PWM_slider.value = 100
            self.ids.cytron_label.color = (0, 1, 0, .8)
            cyprus.set_pwm_values(2, period_value=10000, compare_value=10000,
                                  compare_mode=cyprus.LESS_THAN_OR_EQUAL)

        elif cmd == "back":
            self.ids.cytron_label.text = "Backward 50.0"
            self.ids.PWM_slider.value = 0
            self.ids.cytron_label.color = (1, 0, 0, .8)
            cyprus.set_pwm_values(2, period_value=10000, compare_value=10000,
                                  compare_mode=cyprus.LESS_THAN_OR_EQUAL)

        else:
            self.ids.cytron_label.text = "Neutral"
            self.ids.PWM_slider.value = 50
            self.ids.cytron_label.color = (1, .65, 0, .8)
            cyprus.set_pwm_values(2, period_value=10000, compare_value=0,
                                  compare_mode=cyprus.LESS_THAN_OR_EQUAL)

    def tickArrows(self, way):
        cyprus.initialize()
        cyprus.setup_servo(2)
        num = self.ids.PWM_slider.value
        if way == "up":
            if self.ids.cytron_label.text == "Neutral":
                num = 55
            elif num == 45:
                num = 50
            elif num == 100:
                num = 100
            else:
                num += 1
        elif way == "down":
            if self.ids.cytron_label.text == "Neutral":
                num = 45
            elif num == 55:
                num = 50
            elif num == 0:
                num = 0
            else:
                num -= 1
        if (num > 45) and (num < 55):
            self.ids.cytron_label.text = "Neutral"
            self.ids.cytron_label.color = (1, .65, 0, .8)
            self.ids.PWM_slider.value = 50
            val = 0
        elif num > 54:
            s = "Forward " + str(num - 50)
            self.ids.cytron_label.text = s
            self.ids.cytron_label.color = (0, 1, 0, .8)
            self.ids.PWM_slider.value = num
            val = (self.ids.PWM_slider.value - 50) * 200
            direction = 1
        else:
            s = "Backward " + str(num - 50)
            self.ids.cytron_label.text = s
            self.ids.cytron_label.color = (1, 0, 0, .8)
            self.ids.PWM_slider.value = num
            val = (50 - self.ids.PWM_slider.value) * 200
            direction = 0


        cyprus.set_pwm_values(2, period_value=10000, compare_value=val,
                              compare_mode=cyprus.LESS_THAN_OR_EQUAL)



Builder.load_file('main.kv')
Builder.load_file('switches.kv')
Builder.load_file('drivers.kv')
Builder.load_file('motors.kv')
Builder.load_file('switchMethods.kv')
Builder.load_file('switchMethods1.kv')
Builder.load_file('servoMethods.kv')
Builder.load_file('stepperMethods.kv')
Builder.load_file('talonMethods.kv')
Builder.load_file('cytronMethods.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(SwitchScreen(name="switches"))
SCREEN_MANAGER.add_widget(DriverScreen(name="drivers"))
SCREEN_MANAGER.add_widget(MotorScreen(name="motors"))
SCREEN_MANAGER.add_widget(SwitchMethodsScreen(name="switchMethods"))
SCREEN_MANAGER.add_widget(SwitchMethods1Screen(name="switchMethods1"))
SCREEN_MANAGER.add_widget(ServoMethodsScreen(name="servoMethods"))
SCREEN_MANAGER.add_widget(StepperMethodsScreen(name="stepperMethods"))
SCREEN_MANAGER.add_widget(TalonMethodsScreen(name="talonMethods"))

SCREEN_MANAGER.add_widget(CytronMethodsScreen(name="cytronMethods"))


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()
