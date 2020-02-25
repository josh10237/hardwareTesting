import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import spidev
import os
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from Slush.Devices import L6470Registers
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
spi = spidev.SpiDev()
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
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
    pos = False
    servo = False
    talon = False
    cytron = False
    global togServo
    togServo = 1

    def servoThread(self):
        global servo
        while servo:
            if(cyprus.read_gpio() & 0b0001):
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


    def switches(self):
        SCREEN_MANAGER.current =

    def drivers(self):

    def motors(self):





    def cleanup(self):
        cyprus.set_servo_position(1,.5)
        cyprus.close()
        spi.close()
        GPIO.cleanup()
        quit()



    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()
"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(MainScreen(name="Switches"))
SCREEN_MANAGER.add_widget(MainScreen(name="Drivers"))
SCREEN_MANAGER.add_widget(MainScreen(name="Motors"))



"""
MixPanel
"""


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