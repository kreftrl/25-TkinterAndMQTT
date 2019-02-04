"""
Using a Brickman (robot) as the receiver of messages.
"""

# Same as m2_fake_robot_as_mqtt_sender,
# but have the robot really do the action.
# Implement just FORWARD at speeds X and Y is enough.

import mqtt_remote_method_calls as com
import time
import math
import ev3dev.ev3 as ev3

class DelegateThatReceives(object):

    def __init__(self):
        self.robot=SimpleRoseBot()

    def forward(self, speed1, speed2):
        self.robot.go(speed1,speed2)

class SimpleRoseBot(object):

    def __init__(self):

        self.left_wheel_motor = Motor('B')
        self.right_wheel_motor = Motor('C')
        self.color_sensor = ColorSensor(3)

    def go(self,left_wheel_speed,right_wheel_speed):

        Motor('B').turn_on(left_wheel_speed)
        Motor('C').turn_on(right_wheel_speed)

    def stop(self):

        Motor('B').turn_off()
        Motor('C').turn_off()

    def go_straight_for_seconds(self,seconds,speed):

        SimpleRoseBot().go(speed,speed)
        start = time.time()
        while True:
            current = time.time()
            if current - start >= seconds:
                break
        SimpleRoseBot().stop()

    def go_straight_for_inches(self,inches,speed):

        Motor('B').reset_position()
        SimpleRoseBot().go(speed,speed)
        while True:
            position = Motor('B').get_position() * 1.3 * math.pi / 360
            if position >= inches:
                break
        SimpleRoseBot().stop()

    def go_straight_until_black(self,speed):

        SimpleRoseBot().go(speed,speed)
        while True:
            if SimpleRoseBot().color_sensor.get_reflected_light_intensity() <= 5:
                break
        SimpleRoseBot().stop()

class Motor(object):
    WheelCircumference = 1.3 * math.pi

    def __init__(self, port):  # port must be 'B' or 'C' for left/right wheels
        self._motor = ev3.LargeMotor('out' + port)

    def turn_on(self, speed):  # speed must be -100 to 100
        self._motor.run_direct(duty_cycle_sp=speed)

    def turn_off(self):
        self._motor.stop(stop_action="brake")

    def get_position(self):  # Units are degrees (that the motor has rotated).
        return self._motor.position

    def reset_position(self):
        self._motor.position = 0

class ColorSensor(object):
    def __init__(self, port):  # port must be 3
        self._color_sensor = ev3.ColorSensor('in' + str(port))

    def get_reflected_light_intensity(self):
        # Returned value is from 0 to 100,
        # but in practice more like 3 to 90+ in our classroom lighting.
        return self._color_sensor.reflected_light_intensity

def main():
    robot=SimpleRoseBot()
    name1 = 'lego28'
    name2 = 'qwertyuiopasdfghjklzxcvbnm'

    my_delegate = DelegateThatReceives()
    mqtt_client = com.MqttClient(my_delegate)
    mqtt_client.connect(name1, name2)
    time.sleep(1)  # Time to allow the MQTT setup.

    while True:
        time.sleep(0.01)  # Time to allow message processing

main()