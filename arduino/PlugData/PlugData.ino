/*
  Plug_Data

  This code runs on an Arduino connected directly to the smartplug. 
  It measures the current drawn through the plug and sends it to SerialToServer.py via serial port, 
  where it is further processed and sent to a server. 

  Collects data every 8 miliseconds, sends  aggregated data to serial port every second. 

  This code listens for a binary on/off signal from ListenSend, and toggles the plug on/off accordingly. 

  Currently unclear whether signal will be sent via XBee Net BluTooth antennas and a second Arduino, 
  or directly to a computer with a WiFi antenna. 
  
*/

#include <stdlib.h>  
#include "EmonLib.h"                   // Include Emon Library
EnergyMonitor emon1;                   // Create an instance

int sensor_pin = A0;    // analogo input pin for the current sensor
int plug_pin = 8;           // PWM pin the plug switch is attached to

float i_measured = 42.43; //sqrt(2) * i_rms, in ohms
float i_sensor = 0.02121; //
float R_burden = 250;

int plug_state = LOW;    // on/off state of plug. Default is off. 

int interval = 0;
int switch_state = 0;
int read_value = 0;

// the setup routine runs once when you press reset:
void setup() {
  // declare sensor pin to be an input:
  pinMode(sensor_pin, INPUT);

  //Initialize serial port
  Serial.begin(9600);
  Serial.println(switch_state);
  
  //Initialize digital pins as output
  pinMode(plug_pin, OUTPUT);  

  float calibration_value = ( i_measured / i_sensor ) / R_burden;
  emon1.current(sensor_pin, calibration_value);             // Current: input pin, calibration.
}

// the loop routine runs over and over again forever:
void loop() {

  float Irms = emon1.calcIrms(1480);  // Calculate Irms only    
  Serial.println(Irms);

  while (Serial.available() > 0) {
    switch_state = Serial.read() - '0';
  }
      
  //Samples 200 times a second, more than double the AC frequency to capture the current. 
  delay (1000);
}



