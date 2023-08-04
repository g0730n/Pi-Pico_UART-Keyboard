# Pi-Pico_UART-Keyboard
A key matrix driven Micropython on a Pi Pico, sends keypress over UART.

<h3>main.py</h3>
Pi-Pico reads matrix on GPIO, example code is a 6x7 matrix. Pin #'s for rows and columns can be adjusted as needed in <b>main.py</b>.
Wiring for UART is on UART0 (GPIO-0 = RX & GPIO-1 = TX)

<h3>kb_handler.py</h3>

Raspberry Pi uses UART0 (BCM-15 = TX & BCM-16 = RX) to receive incoming data from Pico.<br>
<a href="https://github.com/pyserial/pyserial">PySerial</a> library is used to receive serial data.<br>
<a href="https://github.com/boppreh/keyboard">keyboard</a> library is used to translate keypress to system.
