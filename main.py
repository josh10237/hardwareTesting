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


    def toggleServoSwitch(self):
        global servo
        if(servo == False):
            self.ids.toggle_servo_switch.text = "Direction Switch On"
            servo = True
            Thread(target=self.servoThread).start()
            Thread.daemon = True
        else:
            self.ids.toggle_servo_switch.text = "Direction Switch Off"
            servo = False
    def toggleTalonSwitch(self):
        global talon
        if(talon == False):
            self.ids.toggle_talon_switch.text = "Stop Switch On"
            talon = True
            Thread(target=self.talonThread).start()
            Thread.daemon = True
        else:
            self.ids.toggle_talon_switch.text = "Stop Switch Off"
            talon = False

    def toggleProximity(self):
        global cytron
        if cytron == False:
            self.ids.toggle_proximity.text = "Proximity Switch On"
            cytron = True
            Thread(target=self.cytronThread).start()
            Thread.daemon = True
        else:
            self.ids.toggle_proximity.text = "Proximity Switch Off"
            cytron = False


    def servoPressed(self):
        global pos
        cyprus.initialize()  # initialize the RPiMIB and establish communication
        cyprus.setup_servo(2)  # sets up P4 on the RPiMIB as a RC servo style output
        if pos:
            cyprus.set_servo_position(1,0)
            pos = False
        else:
            cyprus.set_servo_position(1,1)
            pos = True

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        global togServo
        if(togServo == 1):
            cyprus.set_servo_position(1, 0)
            togServo = 0
            # 2 specifies port P5, i is a float that specifies speed
        else:
            cyprus.set_servo_position(1, 1)
            togServo = 1


    def cleanup(self):
        cyprus.set_servo_position(1,.5)
        cyprus.close()
        spi.close()
        GPIO.cleanup()
        quit()
    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

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