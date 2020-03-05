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
                print("yeepie")
            else:
                cyprus.set_pwm_values(1, period_value=100000, compare_value=0,
                                      compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                sleep(.1)
                print("yeepie 1")

    def cyp(self):
        # cyprus.close()
        # cyprus.initialize()
        # cyprus.setup_servo(2)
        # cyprus.set_servo_position(2, .5)
        print("on enter")

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
        print("recived on enter")
        global checking
        checking = True
        Thread(target=self.switchThread).start()
        Thread.daemon = True

    def switchThread(self):
        global checking
        while checking:
            if (cyprus.read_gpio() & 0b0001):
                sleep(.1)
                if (cyprus.read_gpio() & 0b0001):
                    self.ids.toggle_sensing_label.text = "Not Sensing"
                    self.ids.toggle_sensing_label.color = (1, 0, 0, .8)
            else:
                self.ids.toggle_sensing_label.text = "Sensing"
                self.ids.toggle_sensing_label.color = (0, 1, 0, .8)


class SwitchMethods1Screen(Screen):
    def back(self):
        global checking
        checking = False

        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'switches'

    def startThread(self):
        global checking
        checking = True
        Thread(target=self.switchThread).start()
        Thread.daemon = True

    def switchThread(self):
        global checking
        while checking:
            if (cyprus.read_gpio() & 0b0001):
                sleep(.1)
                if (cyprus.read_gpio() & 0b0001):
                    self.ids.toggle_sensing_label.text = "Not Sensing"
                    self.ids.toggle_sensing_label.color = (1, 0, 0, .8)
            else:
                self.ids.toggle_sensing_label.text = "Sensing"
                self.ids.toggle_sensing_label.color = (0, 1, 0, .8)


class ServoMethodsScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = "motors"
        cyprus.set_servo_position(1, .5)
        cyprus.initialize()

    def moveServo(self):
        global servoPos
        cyprus.setup_servo(1)
        if servoPos == 1:
            cyprus.set_servo_position(1, 0)
            servoPos = 0
        else:
            cyprus.set_servo_position(1, 1)
            servoPos = 1


class StepperMethodsScreen(Screen):

    def setSpeed(self, speed):
        s1 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                     steps_per_unit=200, speed=8)
        if speed == "fast":
            s1.set_speed(8)
            s1.start_relative_move(5)
        else:
            s1.set_speed(2)
            s1.start_relative_move(5)

    def back(self):
        s1 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                     steps_per_unit=200, speed=8)
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = "motors"
        s1.free()

    def one(self, dir):
        s1 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                     steps_per_unit=200, speed=8)
        if dir == "for":
            s1.start_relative_move(1)
        else:
            s1.start_relative_move(-1)


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
            s = "Forward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (0, 1, 0, .8)
            spd = spd - .03
        else:
            s = "Backward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (1, 0, 0, .8)
            spd = spd + .03

        cyprus.set_servo_position(2, spd)

    def buttonControl(self, cmd):
        if cmd == "forward":
            self.ids.talon_label.text = "Forward 50.0"
            self.ids.talon_label.color = (0, 1, 0, .8)
            cyprus.set_servo_position(2, 1)

        elif cmd == "back":
            self.ids.talon_label.text = "Backward 50.0"
            self.ids.talon_label.color = (1, 0, 0, .8)
            cyprus.set_servo_position(2, 0)

        else:
            self.ids.talon_label.text = "Neutral"
            self.ids.talon_label.color = (1, .65, 0, .8)
            cyprus.set_servo_position(2, .5)

    def tickArrows(self, way):
        pass

class CytronMethodsScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = 'drivers'

    def updateLabel(self):
        cyprus.initialize()
        if (self.ids.PWM_slider.value < 55) and (self.ids.PWM_slider.value > 45):
            self.ids.talon_label.text = "Neutral"
            self.ids.talon_label.color = (1, .65, 0, .8)
            val = 0
        elif self.ids.PWM_slider.value > 54:
            s = "Forward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (0, 1, 0, .8)
            val = (self.ids.PWM_slider.value - 50) * 2000
            direction = 1
        else:
            s = "Backward " + str(abs(self.ids.PWM_slider.value) - 50)
            self.ids.talon_label.text = s
            self.ids.talon_label.color = (1, 0, 0, .8)
            val = (50 - (self.ids.PWM_slider.value)) * 2000
            direction = 0
        cyprus.set_pwm_values(2, period_value=100000, compare_value=val,
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
