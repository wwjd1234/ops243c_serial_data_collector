#!/usr/bin/env python3

# https://github.com/makerportal/pylive
# https://github.com/pratikguru/Instructables/blob/master/uart_visualizer.py

import tkinter as tk
import threading
import numpy as np
import pandas as pd
import csv
from tkinter.ttk import Progressbar
import os

from optparse import OptionParser
import time
import json

import serial
import serial.tools.list_ports
from serial.serialutil import SerialException

import sys
import select
from platform import system
if system() == "Linux":
    import tty
    import termios
elif system() == "Windows":
    from msvcrt import kbhit, getche # or getch() for echo-less getch

serial_data = ''
filter_data = ''
update_period = 5
serial_object = None
gui = tk.Tk()
gui.title("UART Interface OPS243C")
start_flag = 1

#i_data = np.array([])
#q_data = np.array([])

#range_data = np.array([])
#range_magnitude = np.array([])
range_time = np.array([])

#speed_data = np.array([])
#magnitude_data = np.array([])
speed_time = np.array([])

fft_data = np.array([])

range_data_list = [np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([])]
range_magnitude_list = [np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([])]
speed_data_list = [np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([]),
                   np.array([])]
speed_magnitude_list = [np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([]),
                        np.array([])]

def set_args():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-p", "--port", dest="port_name",
                      help="read data from PORTNAME")
    parser.add_option("-b", "--baud", dest="baudrate",
                      default="57600",
                      help="baud rate on serial port")
    parser.add_option("-t", "--timeToLive",
                      default=0,
                      dest="time_to_live")
    return parser

def get_args_options(parser):
    return parser.parse_args()

def set_time_to_live(options):
    return float(options.time_to_live)
#
# def set_baudrate(options):
#     baudrate_int = int(options.baudrate)
#     if baudrate_int <= 0:
#         baudrate_int = 57600
#     return baudrate_int
#
# def set_serial_port(options, serial_port):
#     if options.port_name is None or len(options.port_name) < 1:
#         if len(serial.tools.list_ports.comports()):
#             serial_port.port = serial.tools.list_ports.comports()[0].device
#         elif system() == "Linux":
#             serial_port.port = "/dev/ttyACM0"  # good for linux
#         else:
#             serial_port.port = "COM4"  # maybe we'll luck out on windows
#     else:
#         serial_port.port = options.port_name
#
def check_serial_port(serial_port):
     if not serial_port.is_open:
         print("Exiting.  Could not open serial port:", serial_port.port)
         raise SerialException
         #sys.exit(1)
#
# def key_available():
#     if system() == "Linux":
#         return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
#     elif system() == "Windows":
#         return kbhit()
#
# def start_callback(event):
#     print("start")
#
# def stop_callback(event):
#     print("stop")
#
# def main():
#     parser = set_args()
#     (options, args) = get_args_options(parser)
#
#     time_to_live_val = set_time_to_live(options)
#     baudrate_int = set_baudrate(options)
#
#     serial_port = serial.Serial(
#         timeout=0.1,
#         writeTimeout=0.2,
#         baudrate=baudrate_int
#     )
#     set_serial_port(options,serial_port)
#     serial_port.open()
#     check_serial_port(serial_port)
#
#     if system() == "Linux":
#         # suppress echo on terminal.
#         old_tty_settings = termios.tcgetattr(sys.stdin)
#         old_port_attr = termios.tcgetattr(serial_port.fileno())
#         new_port_attr = termios.tcgetattr(serial_port.fileno())
#         new_port_attr[3] = new_port_attr[3] & ~termios.ECHO
#         termios.tcdrain(serial_port.fileno())
#         termios.tcsetattr(serial_port.fileno(), termios.TCSADRAIN, new_port_attr)
#     start_time = time()
#
#     #serial_port.write(b'??')
#     #serial_port.write(b'S?')
#     serial_port.write(b'OJ')   # JSON
#     serial_port.write(b'OR')   # Raw I/Q
#     serial_port.write(b'OM')   # Magnitude I/Q
#     serial_port.write(b'OF')   # Post FFT
#     serial_port.write(b'OT')   # Time Report
#     #serial_port.write(b'os')  # Speed Report (Default Active)
#     #serial_port.write(b'od')  # Range Report (Default Active)
#
#     try:
#         if system() == "Linux":
#             tty.setcbreak(sys.stdin.fileno())
#
#         serial_port.flushInput()
#         serial_port.flushOutput()
#         while serial_port.is_open:
#             data_rx_bytes = serial_port.readline()
#             #print(data_rx_bytes)
#             data_rx_length = len(data_rx_bytes)
#             if data_rx_length != 0:
#                 data_rx_str = str.rstrip(str(data_rx_bytes.decode('utf-8', 'ignore'))) # strict ignore replace
#                 print(data_rx_str)
#             #while key_available():
#             #    if system() == "Linux":
#             #        c = sys.stdin.read(1)
#             #        serial_port.write(c.encode('utf-8'))
#             #        sys.stdout.write(c)
#             #    elif system() == "Windows":
#             #        c = getche()   # change to getch() to remove echo
#             #        print(c)
#             #        serial_port.write(c)
#             if time_to_live_val > 0:
#                 if (time() - start_time) > time_to_live_val:
#                     print("Exiting.  Time to live elapsed")
#                     sys.exit(0)
#
#     except SerialException:
#         print("Serial Port closed. terminate.")
#     except KeyboardInterrupt:
#         print("Break received,  Serial Port closing.")
#     finally:
#         if system() == "Linux":
#             # reinstate original condition (reinstate echo if it was there)
#             termios.tcsetattr(serial_port.fileno(), termios.TCSADRAIN, old_port_attr)
#             termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty_settings)


def connect():
    """The function initiates the Connection to the UART device with the Port and Buad fed through the Entry
    boxes in the application.
    The radio button selects the platform, as the serial object has different key phrases
    for Linux and Windows. Some Exceptions have been made to prevent the app from crashing,
    such as blank entry fields and value errors, this is due to the state-less-ness of the
    UART device, the device sends data at regular intervals irrespective of the master's state.
    The other Parts are self explanatory.
    """

    version_ = button_var.get()
    print("Version: " + str(version_))
    global serial_object
    port = port_entry.get()
    baud = baud_entry.get()

    try:
        if version_ == 2:
            try:
                serial_object = serial.Serial('/dev/tty' + str(port), baud)

            except:
                print("Cant Open Specified Port")
        elif version_ == 1:
            parser = set_args()
            (options, args) = get_args_options(parser)
            time_to_live_val = set_time_to_live(options)
            serial_object = serial.Serial(port='COM' + str(port), baudrate=baud, timeout=0.1, writeTimeout=0.2)
            check_serial_port(serial_object)

    except ValueError:
        print("ValueError Enter Baud and Port")
        return
    except SerialException:
        print("SerialException: Device not connected or wrong serial port defined")
        return

    t1 = threading.Thread(target=get_data)
    t1.daemon = True
    t1.start()


def get_data():
    """This function serves the purpose of collecting data from the serial object and storing
    the filtered data into a global variable.
    The function has been put into a thread since the serial event is a blocking function.
    """
    global serial_object
    global filter_data
    global start_flag
    global speed_time, fft_data, range_time #range_data, range_magnitude, speed_data, magnitude_data,
    global range_data_list, range_magnitude_list, speed_data_list, speed_magnitude_list

    serial_object.write(b'OJ')   # JSON
    #serial_object.write(b'OP')  # Doppler Phase
    #serial_object.write(b'oP')  # Doppler Phase
    #serial_object.write(b'O1')  # Number of reports
    #serial_object.write(b'o1')  # Number of reports
    serial_object.write(b'UC')   # Doppler {"Units":"cm-per-sec"}
    serial_object.write(b'uC')   # Range {"Units":"Value", "RangeUnit":"cm"}
    serial_object.write(b'OT')   # Time Report
    ####serial_object.write(b'oT')   # Time Report
    serial_object.write(b'OM')   # Doppler Magnitude
    serial_object.write(b'oM')   # FMCW Magnitude
    ####serial_object.write(b'oS')   # Range Speed
    ####serial_object.write(b'oD')   # Range Distance
    serial_object.write(b'OS')   # Doppler Speed
    serial_object.write(b'OD')   # FMCW Distance
    #serial_object.write(b'oF')  # Range Post FFT
    #serial_object.write(b'OF')  # Doppler Post FFT
    serial_object.write(b'm>5') #range magnitude
    serial_object.write(b'M>5') #speed magnitude
    #serial_object.write(b'??')  # Module Information


    serial_object.flushInput()
    serial_object.flushOutput()

    while (start_flag):
        try:
            serial_data = serial_object.readline()
            data_rx_length = len(serial_data)
            if data_rx_length != 0:
                filter_data = str.rstrip(str(serial_data.decode('utf-8', 'ignore'))) # strict ignore replace
                dict_fd = json.loads(filter_data)
                if "range" in dict_fd:
                    r_time = dict_fd["time"]
                    range_time = np.concatenate((range_time, [r_time]))

                    range_df = dict_fd["range"]
                    append_data(range_df, range_data_list)

                    mag = dict_fd["magnitude"]
                    append_data(mag, range_magnitude_list)

                elif "speed" in dict_fd:
                    s_time = dict_fd["time"]
                    speed_time = np.concatenate((speed_time, [s_time]))

                    speed = dict_fd["speed"]
                    append_data(speed, speed_data_list)

                    mag = dict_fd["magnitude"]
                    append_data(mag, speed_magnitude_list)

                elif "FFT" in dict_fd:
                    fft = dict_fd["FFT"]
                    fft_data = np.concatenate((fft_data, fft))
                #if "I" in dict_fd:
                #    i_data = np.concatenate((i_data, dict_fd["I"]))
                    #print(i_data)
                #if "Q" in dict_fd:
                #    q_data = np.concatenate((q_data, dict_fd["Q"]))
                print(filter_data)

        except TypeError:
            pass
        except ValueError:
            print("JSON ERROR")

def append_data(jsn, lst):
    if isinstance(jsn, str):
        jsn = np.array([jsn])

    for i, value in enumerate(jsn):
        lst[i] = np.concatenate((lst[i], [value]))

    if len(jsn) < len(lst):
        for i in range(len(jsn), len(lst)):
            lst[i] = np.concatenate((lst[i], np.zeros(1)))
# def update_gui():
#     """" This function is an update function which is also threaded. The function assimilates the data
#     and applies it to it corresponding progress bar. The text box is also updated every couple of seconds.
#     A simple auto refresh function .after() could have been used, this has been avoid purposely due to
#     various performance issues.
#     """
    # global filter_data
    # global update_period
    #
    # text.place(x=15, y=10)
    # progress_1.place(x=60, y=100)
    # progress_2.place(x=60, y=130)
    # progress_3.place(x=60, y=160)
    # progress_4.place(x=60, y=190)
    # progress_5.place(x=60, y=220)
    # new = time.time()

    # while (1):
    #     if filter_data:
    #
    #         text.insert(tk.END, filter_data)
    #         text.insert(tk.END, "\n")
            # try:
            #     progress_1["value"] = filter_data[0]
            #     progress_2["value"] = filter_data[1]
            #     progress_3["value"] = filter_data[2]
            #     progress_4["value"] = filter_data[3]
            #     progress_5["value"] = filter_data[4]
            #
            #
            # except:
            #     pass
            #
            # if time.time() - new >= update_period:
            #     text.delete("1.0", tk.END)
            #     progress_1["value"] = 0
            #     progress_2["value"] = 0
            #     progress_3["value"] = 0
            #     progress_4["value"] = 0
            #     progress_5["value"] = 0
            #     new = time.time()


def send():
    """This function is for sending data from the computer to the host controller.

        The value entered in the the entry box is pushed to the UART. The data can be of any format, since
        the data is always converted into ASCII, the receiving device has to convert the data into the required f
        format.
    """
    send_data = data_entry.get()

    if not send_data:
        print("Sent Nothing")

    serial_object.write(send_data.encode())


def disconnect():
    """
    This function is for disconnecting and quitting the application.
    Sometimes the application throws a couple of errors while it is being shut down, the fix isn't out yet
    but will be pushed to the repo once done.
    simple GUI.quit() calls.
    """
    global start_flag
    try:
        start_flag = 0
        serial_object.close()

    except AttributeError:
        print("Closed without Using it -_-")

    gui.quit()

def save_data():
    print("saving")

    global start_flag
    global range_time, speed_time, fft_data
    global range_data_list, range_magnitude_list, speed_data_list, speed_magnitude_list

    #stop the get_data thread
    start_flag = 0

    df = pd.DataFrame({"Time": range_time,
                       "Range0": range_data_list[0], "Range1": range_data_list[1], "Range2": range_data_list[2],
                       "Range3": range_data_list[3], "Range4": range_data_list[4], "Range5": range_data_list[5],
                       "Magnitude0": range_magnitude_list[0], "Magnitude1": range_magnitude_list[1], "Magnitude2": range_magnitude_list[2],
                       "Magnitude3": range_magnitude_list[3], "Magnitude4": range_magnitude_list[4], "Magnitude5": range_magnitude_list[5]})
    df.to_csv("range_and_magnitude.csv", index=False)

    df = pd.DataFrame({"Time": speed_time,
                       "Speed0": speed_data_list[0], "Speed1": speed_data_list[1], "Speed2": speed_data_list[2],
                       "Speed3": speed_data_list[3], "Speed4": speed_data_list[4], "Speed5": speed_data_list[5],
                       "Magnitude0": speed_magnitude_list[0], "Magnitude1": speed_magnitude_list[1], "Magnitude2": speed_magnitude_list[2],
                       "Magnitude3": speed_magnitude_list[3], "Magnitude4": speed_magnitude_list[4], "Magnitude5": speed_magnitude_list[5]})
    df.to_csv("speed_and_magnitude.csv", index=False)

if __name__ == "__main__":
    """
    The main loop consists of all the GUI objects and its placement.
    The Main loop handles all the widget placements.
    """
    # frames
    #frame_1 = tk.Frame(height=285, width=480, bd=3, relief='groove').place(x=7, y=5)
    frame_2 = tk.Frame(height=150, width=340, bd=3, relief='groove').place(x=7, y=5)
    text = tk.Text(width=65, height=5)

    # threads
    # t2 = threading.Thread(target=update_gui)
    # t2.daemon = True
    # t2.start()

    # Labels
    # data1_ = tk.Label(text="Data1:").place(x=15, y=100)
    # data2_ = tk.Label(text="Data2:").place(x=15, y=130)
    # data3_ = tk.Label(text="Data3:").place(x=15, y=160)
    # data4_ = tk.Label(text="Data4:").place(x=15, y=190)
    # data5_ = tk.Label(text="Data5:").place(x=15, y=220)

    baud = tk.Label(text="Baud").place(x=10, y=68)
    port = tk.Label(text="Port").place(x=110, y=68)
    #contact = tk.Label(text="ops243c").place(x=250, y=437)

    # # progress_bars
    # progress_1 = Progressbar(orient="horizontal", mode='determinate', length=200, max=255)
    # progress_2 = Progressbar(orient="horizontal", mode='determinate', length=200, max=255)
    # progress_3 = Progressbar(orient="horizontal", mode='determinate', length=200, max=255)
    # progress_4 = Progressbar(orient="horizontal", mode='determinate', length=200, max=255)
    # progress_5 = Progressbar(orient="horizontal", mode='determinate', length=200, max=255)

    # Entry
    data_entry = tk.Entry(gui)
    #data_entry.insert(0, "OR")
    data_entry.place(x=80, y=15)

    baud_entry = tk.Entry(gui, width=7)
    baud_entry.insert(0, "57600")
    baud_entry.place(x=10, y=85)

    port_entry = tk.Entry(gui, width=7)
    port_entry.insert(0, "5")
    port_entry.place(x=110, y=85)

    # radio button
    button_var = tk.IntVar()
    radio_1 = tk.Radiobutton(text="Windows", variable=button_var, value=1)
    radio_1.select()
    radio_1.place(x=10, y=45)
    radio_2 = tk.Radiobutton(text="Linux", variable=button_var, value=2).place(x=110, y=45)

    # button
    button1 = tk.Button(text="Send", command=send, width=6).place(x=15, y=10)
    connect = tk.Button(text="Connect", command=connect).place(x=15, y=120)
    disconnect = tk.Button(text="Disconnect", command=disconnect).place(x=95, y=120)
    save_data = tk.Button(text="Save Data", command=save_data).place(x=200, y=120)

    # mainloop
    gui.geometry('350x160')
    gui.mainloop()