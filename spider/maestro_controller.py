"""maestro_controller.py
Classes and functions necessary to drive two daisy chained Maestro servo controllers,
including the ability to define poses and animate between them.
"""

import serial
import time
from itertools import izip

#http://www.pololu.com/docs/0J40/5.e
class MaestroController(object):
    """MaestroController gives access to two Maestro's connected via UART, as well as
    the ability to run animations based on pre defined positions.
    """
    def __init__(self):
        self.serial = get_serial('/dev/ttyMFD1', 9600)
        self.positions = {}
        self.animations = {}

        self.setup_positions()
        self.setup_animations()
        self.current_position = "park"
        self.animating = False
        self.move_to(self.positions[self.current_position], [(10, 10)]*24)

    def setup_positions(self):
        """Setup predefined positions and their safe routes.
        """
        park = ServoPositions([
            [1370, 1750, 1560, 2230], [1030, 1980, 1500, 1500], [1580, 1780, 880, 736],
            [1450, 1100, 1330, 780], [1770, 890, 1500, 1500], [1340, 1970, 1870, 1990]])

        extend = ServoPositions([
            [1370, 1750, 1020, 1570], [1710, 1500, 1500, 1500], [1580, 1780, 1420, 1410],
            [1460, 980, 1890, 1360], [1130, 1410, 1500, 1500], [1360, 1890, 1210, 1210]])

        extend_half = ServoPositions([
            [1370, 1760, 1330, 1790], [1210, 1760, 1500, 1500], [1580, 1810, 1020, 1210],
            [1450, 1080, 1560, 1200], [1610, 1100, 1500, 1500], [1340, 1970, 1700, 1610]])

        jugendstil = ServoPositions([
            [1510, 1990, 1270, 1590], [1250, 1480, 1500, 1500], [1640, 1900, 1020, 1590],
            [1250, 900, 1530, 1270], [1560, 1460, 1500, 1500], [1350, 1920, 1630, 1090]])

        jugendstil_half = ServoPositions([
            [1370, 1750, 1560, 2230], [1250, 1480, 1500, 1500], [1640, 1900, 1020, 1590],
            [1450, 1100, 1330, 780], [1560, 1460, 1500, 1500], [1350, 1920, 1630, 1090]])

        challenge = ServoPositions([
            [1500, 1860, 1410, 1910], [1130, 1610, 1500, 1500], [1640, 1900, 1020, 1600],
            [1340, 970, 1450, 1020], [1610, 1300, 1500, 1500], [1350, 1910, 1650, 1100]])

        point = ServoPositions([
            [1240, 1590, 1020, 770], [1190, 1180, 1500, 1500], [1640, 1900, 910, 1700],
            [1530, 1190, 1810, 2040], [1580, 1730, 1500, 1500], [1350, 1860, 1710, 1020]])

        knife = ServoPositions([
            [1370, 1750, 1560, 2230], [1650, 1400, 1500, 1500], [1580, 1780, 880, 736],
            [1450, 1100, 1330, 780], [1150, 1500, 1500, 1500], [1340, 1970, 1870, 1990]])

        push_away = ServoPositions([
            [1210, 1970, 1240, 1580], [1030, 1980, 1500, 1500], [1580, 1780, 880, 736],
            [1640, 910, 1670, 1360], [1820, 880, 1500, 1500], [1340, 1970, 1870, 1990]])

        wiggle_up = ServoPositions([
            [1370, 1750, 1400, 1520], [1270, 1430, 1500, 1500], [1580, 1780, 1070, 1640],
            [1450, 1050, 1500, 1470], [1500, 1510, 1500, 1500], [1340, 1970, 1590, 1100]])

        wiggle_down = ServoPositions([
            [1370, 1750, 1400, 1610], [1270, 1340, 1500, 1500], [1580, 1780, 1070, 1560],
            [1450, 1050, 1500, 1390], [1500, 1600, 1500, 1500], [1340, 1970, 1590, 1190]])

        self.positions["park"] = park
        self.positions["extend"] = extend
        self.positions["extend_half"] = extend_half
        self.positions["jugendstil"] = jugendstil
        self.positions["jugendstil_half"] = jugendstil_half
        self.positions["challenge"] = challenge
        self.positions["point"] = point
        self.positions["knife"] = knife
        self.positions["push_away"] = push_away
        self.positions["wiggle_up"] = wiggle_up
        self.positions["wiggle_down"] = wiggle_down

    def setup_animations(self):
        """Setup predefined animations (tuple of a list of positions, and times).
        """
        park = [("park", [1500]*6)]
        extend = [("extend", [1500]*6)]
        breathe = [
            ("extend", [1500]*6),
            ("park", [1500]*6),
            ("extend_half", [1500]*6),
            ("park", [1500]*6)]
        knife = [
            ("knife", [600]*6),
            ("pause", 500),
            ("park", [1000]*6)]
        attack = [
            ("extend", [750]*6),
            ("park", [1500]*6)]
        point = [ #note, don't use point as much
            ("point", [1500]*6),
            ("park", [1500]*6)]
        jugendstil = [ #note, pause around 0.5 between position
            ("jugendstil_half", [1500]*6),
            ("pause", 750),
            ("jugendstil", [1500]*6),
            ("pause", 900),
            ("park", [1500]*6)]
        challenge = [
            ("challenge", [1500]*6),
            ("pause", 1000),
            ("park", [1500]*6)]
        wiggle = [ 
            ("wiggle_up", [750]*6),
            ("wiggle_down", [100]*6),
            ("wiggle_up", [100]*6),
            ("wiggle_down", [100]*6),
            ("wiggle_up", [100]*6),
            ("park", [750]*6)]
        dance = [
            ]

        self.animations["park"] = park
        self.animations["extend"] = extend
        self.animations["breathe"] = breathe
        self.animations["knife"] = knife
        self.animations["attack"] = attack
        self.animations["point"] = point
        self.animations["jugendstil"] = jugendstil
        self.animations["challenge"] = challenge
        self.animations["wiggle"] = wiggle
        self.animations["dance"] = dance

    def prox_sensor_listener(self, space, distance):
        """Based on data from the proximity sensor, drive the legs to position.
        """
        print "MaestroController listener called with space=", space, " distance=", distance

    def animation(self, animation_name):
        """Run through animation found with animation_name.
        """
        if self.animating:
            return

        anim = self.animations[animation_name]
        anim_length = len(anim)

        self.animating = True
        i = 0
        while i < anim_length:
            self.animate(anim[i][0], anim[i][1])
            i += 1
        self.animating = False

    def animate(self, script_name, animation_times):
        """Run through script. Animate will take animation_time_safe to reach safe route
        position, and animation_time_final to reach final destination. Times should
        be a list of 6 values for each leg.
        """
        print script_name
        if script_name == "pause":
            time.sleep((animation_times+100)/1000)
            return

        #Determine the difference between the common route and our final position so we can
        #calculate the speed and acceleration necessary to get there.
        difference_final = self.positions[self.current_position] - self.positions[script_name]
        max_value, max_index = difference_final.legs[0][0], (0, 0)
        speed_accel = []
        for leg, animation_time in izip(difference_final.legs, animation_times):
            for servo in leg:
                speed_accel.append(time_to_speed_accel(animation_time, servo, 0))
        for i in range(3):
            for j in range(4):
                if max_value < difference_final.legs[i][j]:
                    max_value = difference_final.legs[i][j]
                    max_index = (i, j)
        index = max_index[0]*4+max_index[1]

        #Animate to common route.
        self.move_to(self.positions[script_name], speed_accel)
        time.sleep(0.1)

        are_servos_moving = True
        max_value = self.positions[script_name].legs[max_index[0]][max_index[1]]
        while are_servos_moving:
            current_position = self.get_position(index)
            if current_position is None or abs(current_position - max_value) <= 20:
                are_servos_moving = False

        self.current_position = script_name

    def move_to(self, position, speed_accel):
        """Send speed, acceleration and position data to the Maestro.
        """
        pulse_widths = []

        # Immediately set the speed and accel values through maestro,
        # but not position. This is done so that all servos can
        # move in a syncronized way.
        i = 0
        while i < 24:
            self.set_speed(i, speed_accel[i][0])
            self.set_accel(i, speed_accel[i][1])
            pulse_widths.append(position.legs[i/4][i%4])
            i += 1

        self.set_position_multiple(0, *pulse_widths)

    def go_home(self):
        """Return all servos to "home" position.
        """
        cmd = chr(0xaa) + chr(0x0c) + chr(0x22)
        self.serial.write(cmd)

    def set_position_multiple(self, first_servo, *pulse_widths):
        """Set position of multiple servos, starting at first servo, going to
        pulse_widths.length servos. Uses raw pulse width.
        """
        num_targets = len(pulse_widths)
        if first_servo+num_targets > 24:
            print "Too many servo targets."
            return

        #We must determine if the servo range straddles both of the chained Maestro's.
        #If so, we have to fiddle a bit to make sure we send the correct commands to
        #each one.
        if first_servo < 12:
            device = 12
        else:
            device = 13
            first_servo = first_servo - 12

        both_devices = False
        targets1 = num_targets
        if device == 12 and first_servo+num_targets > 11:
            both_devices = True
            targets1 = 12 - first_servo
            targets2 = num_targets - targets1

        target_bits = []
        channel = int(first_servo) & 0x7f
        for pulse_width in pulse_widths[:12-first_servo]:
            if pulse_width < 736 or pulse_width > 2272:
                print "Pulse width outside of range [736, 2272]"
                return

            pulse_width = int(pulse_width) * 4

            low_bits = pulse_width & 0x7f
            high_bits = (pulse_width >> 7) & 0x7f
            target_bits.append(low_bits)
            target_bits.append(high_bits)

        cmd = chr(0xaa) + chr(device&0xff) + chr(0x1f) + chr((targets1)&0xff) + chr(channel)
        for byte in target_bits:
            cmd += chr(byte)

        if both_devices is True:
            target_bits2 = []
            channel2 = 0
            for pulse_width in pulse_widths[12-first_servo:]:
                if pulse_width < 736 or pulse_width > 2272:
                    print "Pulse width outside of range [736, 2272]"
                    return

                pulse_width = int(pulse_width) * 4

                low_bits = pulse_width & 0x7f
                high_bits = (pulse_width >> 7) & 0x7f
                target_bits2.append(low_bits)
                target_bits2.append(high_bits)

            cmd2 = chr(0xaa) + chr(0x0d) + chr(0x1f) + chr((targets2)&0xff) + chr(channel2)
            for byte in target_bits2:
                cmd2 += chr(byte)
            self.serial.write(cmd2)

        self.serial.write(cmd)

    def get_position(self, servo):
        """Return two hex bytes, representing the position of servo as
        pulse width * 4 per maestro protocol.
        """
        if servo < 12:
            device = 12
        else:
            device = 13
            servo = servo - 12
        channel = servo &0x7F
        cmd = chr(0xaa) + chr(device) + chr(0x10) + chr(channel)
        self.serial.write(cmd)
        byte1 = self.serial.read()
        byte2 = self.serial.read()

        if len(byte1) < 1 or len(byte2) < 1:
            self.serial.flushInput()
            return None

        return int(int(ord(byte1) | (ord(byte2) << 8)) / 4)

    def get_servos_moving(self):
        """Returns true if any servos are moving, false otherwise.
        """
        cmd1 = chr(0xaa) + chr(0x0c) + chr(0x13)
        self.serial.write(cmd1)
        byte = self.serial.read()
        if len(byte) > 0 and ord(byte) == 1:
            return True

        # cmd2 = chr(0xaa) + chr(0x0d) + chr(0x13)
        # self.serial.write(cmd2)
        # byte = self.serial.read()
        # if len(byte) > 0 and ord(byte) == 1:
        #     return True

        return False

    def set_speed(self, servo, speed):
        """Set the maximum speed of servo.
        """
        device = 12
        if servo > 11:
            servo = servo - 12
            device = 13
        channel = servo & 0x7f
        low_bits = speed & 0xff
        high_bits = (speed >> 8) & 0xff
        cmd = chr(0xaa) + chr(device&0xff) + chr(0x07) + chr(channel)
        cmd = cmd + chr(low_bits) + chr(high_bits)

        self.serial.write(cmd)

    def set_accel(self, servo, accel):
        """Set the acceleration of servo. Will accelerate up to max speed,
        then as the servo approaches position, will decelerate smoothly.
        """
        device = 12
        if servo > 11:
            servo = servo - 12
            device = 13
        channel = servo & 0x7f
        low_bits = accel & 0xff
        high_bits = (accel >> 8) & 0xff
        cmd = chr(0xaa) + chr(device&0xff) + chr(0x09) + chr(channel) + \
            chr(low_bits) + chr(high_bits)

        self.serial.write(cmd)

    def test_get_position(self):
        """Test get_position on chained maestro.
        """
        i = 0
        timeout_count = 0

        while i < 100:
            position = self.get_position(13)
            if position is None:
                timeout_count += 1

            i += 1

        print "Num failures: ", timeout_count

class ServoPositions(object):
    """Holds the positions for 24 legs, and the safe routes required to
    navigate there.
    """
    def __init__(self, legs):
        self.legs = legs
        self.safe_routes = set()

    def __sub__(self, other):
        #We want the absolute value of the difference of each matched servo. This
        #is essentially the distance each servo is traveling. We use this to determine
        #speed and acceleration values later on.
        abs0 = [abs(a - b) for a, b in zip(self.legs[0], other.legs[0])]
        abs1 = [abs(a - b) for a, b in zip(self.legs[1], other.legs[1])]
        abs2 = [abs(a - b) for a, b in zip(self.legs[2], other.legs[2])]
        abs3 = [abs(a - b) for a, b in zip(self.legs[3], other.legs[3])]
        abs4 = [abs(a - b) for a, b in zip(self.legs[4], other.legs[4])]
        abs5 = [abs(a - b) for a, b in zip(self.legs[5], other.legs[5])]

        return ServoPositions([abs0, abs1, abs2, abs3, abs4, abs5])

    def __str__(self):
        return str(self.legs)

def get_serial(tty, baud):
    """Retrieve and open UART connection to maestro controllers.
    """
    ser = serial.Serial()
    ser.port = tty
    ser.baudrate = baud
    ser.timeout = 0.5
    ser.open()
    return ser

def time_to_speed_accel(anim_time, distance, initial_velocity):
    """Convert an animation time over a certain distance with an initial velocity
    to a speed and acceleration based on the Maestro protocol.
    """
    half_time = float(anim_time)/2
    half_distance = distance/2.0

    accel = (2.0*(half_distance-(initial_velocity*half_time))) / (half_time**2)
    max_speed = initial_velocity + (accel * half_time)

    accel = accel * 10 * 80 / 0.25 + 0.5
    max_speed = max_speed * 10 / 0.25 + 0.5

    #Since a speed and acceleration of 0 is basically uncapped according to the
    #Maestro protocol, we set the minimum to be one.
    return int(max(max_speed, 1)), int(max(accel, 1))

def find_common_route(routes1, routes2):
    """Given two sets of safe routes, return an arbitrary safe route in common.
    """
    common_routes = routes1 & routes2

    if len(common_routes) > 0:
        return common_routes.pop()

    return "park"

if __name__ == "__main__":
    MAESTRO = MaestroController()

    print "Animate EXTEND"
    MAESTRO.animate("extend", [1500]*6)

    while MAESTRO.get_servos_moving() is True:
        time.sleep(0.01)

    print "Animate PARK"
    MAESTRO.animate("park", [1500]*6)
