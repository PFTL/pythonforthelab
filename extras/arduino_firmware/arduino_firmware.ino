#include <Regexp.h>

#define IDN_STRING "PFTL DAQ device. Rev 02.2024"
#define INVALID_CHANNEL_MSG "ERROR: Invalid channel number"
#define ERROR_COMMAND "ERROR: UNKNOWN COMMAND"
#define OUT_OF_RANGE_MSG "ERROR: Out of range"

#define DAC_BITS 12
#define ADC_BITS 10

#define COM_IDN "*IDN?"                                  // *IDN?
#define COM_WRITE_DAC "^OUT:CH(%d) (%d+)$"               // e.g. OUT:CH0 1023
#define COM_READ_DAC "^OUT:CH(%d)%?$"                    // e.g. OUT:CH0?
#define COM_READ_ADC "^MEAS:CH(%d)%?$"                   // e.g. MEAS:CH1?

#define BUFFER_LENGTH 100

int DACchannel[] = { DAC0, DAC1 };
int ADCchannel[] = { A0, A1, A2, A3, A4, A5, A6, A7 };

#define MAX_DAC_CHANNEL sizeof(DACchannel) / sizeof(int)
#define MAX_ADC_CHANNEL sizeof(ADCchannel) / sizeof(int)

int DACvalues[MAX_DAC_CHANNEL];


void setup() {
  int i;
  Serial.begin(9600);
  while (!Serial) ;
  Serial.setTimeout(-1);
  Serial.flush();
  analogWriteResolution(DAC_BITS);
  analogReadResolution(ADC_BITS);
  for (i = 0; i < MAX_DAC_CHANNEL; i++) {
    analogWrite(DACchannel[i], 0);
    DACvalues[i] = 0;
  }
}

void loop() {
  String msg;
  MatchState ms;
  char buffer[BUFFER_LENGTH];
  int channel, value;
  float volt;

  msg = Serial.readStringUntil('\n');
  msg.toCharArray(buffer, BUFFER_LENGTH);
  ms.Target(buffer);

  if (msg == COM_IDN) {
    Serial.println(IDN_STRING);
  }

  // write DAC value
  else if (ms.Match(COM_WRITE_DAC) == 1) {
    channel = atoi(ms.GetCapture(buffer, 0));
    if (channel >= 0 && channel < MAX_DAC_CHANNEL) {
      value = atoi(ms.GetCapture(buffer, 1));
      if (value >= pow(2, DAC_BITS)) {
        Serial.println(OUT_OF_RANGE_MSG);
      } else {
        analogWrite(DACchannel[channel], value);
        DACvalues[channel] = value;
        Serial.println(value);
      }
    } else Serial.println(INVALID_CHANNEL_MSG);
  }

  // request current DAC value in volts
  else if (ms.Match(COM_READ_DAC) == 1) {
    channel = atoi(ms.GetCapture(buffer, 0));
    if (channel >= 0 && channel < MAX_DAC_CHANNEL) {
      Serial.println(DACvalues[channel]);
    } else Serial.println(INVALID_CHANNEL_MSG);
  }

  // request ADC measurement value
  else if (ms.Match(COM_READ_ADC) == 1) {
    channel = atoi(ms.GetCapture(buffer, 0));
    if (channel >= 0 && channel < MAX_ADC_CHANNEL) {
      Serial.println(analogRead(ADCchannel[channel]));
    } else Serial.println(INVALID_CHANNEL_MSG);
  }

  else {
    Serial.print(ERROR_COMMAND);
    Serial.println(msg);
  }
  delay(20);
}
