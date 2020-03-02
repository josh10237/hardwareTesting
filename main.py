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
    """
    Class to handle the main screen and its associated touch events
    """
    global pos
    global cytron
    global servo
    global talon
    global checking
    pos = False
    servo = False
    talon = False
    cytron = False
    global togServo
    togServo = 1

    def servoThread(self):
        global servo
        while servo:
            if (cyprus.read_gpio() & 0b0001):
                sleep(.1)
                if (cyprus.read_gpio() & 0b0001):
                    cyprus.set_servo_position(1, 0)
            else:
                cyprus.set_servo_position(1, 1)

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
        # SCREEN_MANAGER.current =
        pass

    def righty(self):
        # SCREEN_MANAGER.current =
        pass


class MotorScreen(Screen):
    def back(self):
        SCREEN_MANAGER.transition.direction = 'right'
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def lefty(self):
        # SCREEN_MANAGER.current = ''
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


Builder.load_file('main.kv')
Builder.load_file('switches.kv')
Builder.load_file('drivers.kv')
Builder.load_file('motors.kv')
Builder.load_file('switchMethods.kv')
Builder.load_file('switchMethods1.kv')
Builder.load_file('servoMethods.kv')
# Builder.load_file('stepperMethods.kv')
# Builder.load_file('talonMethods.kv')
# Builder.load_file('cytronMethods.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(SwitchScreen(name="switches"))
SCREEN_MANAGER.add_widget(DriverScreen(name="drivers"))
SCREEN_MANAGER.add_widget(MotorScreen(name="motors"))
SCREEN_MANAGER.add_widget(SwitchMethodsScreen(name="switchMethods"))
SCREEN_MANAGER.add_widget(SwitchMethods1Screen(name="switchMethods1"))
SCREEN_MANAGER.add_widget(ServoMethodsScreen(name="servoMethods"))


# SCREEN_MANAGER.add_widget(StepperMethodsScreen(name="stepperMethods"))
# SCREEN_MANAGER.add_widget(TalonMethodsScreen(name="talonMethods"))
# SCREEN_MANAGER.add_widget(CytronMethodsScreen(name="cytronMethods"))


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
