String Comm;

int output = DAC0;
int input;
int val;
String inData;
String tempValue;
String channel;
int sensorPin = A0;    // select the input pin for the potentiometer
int sensorValue;
bool isData = false;
int i = 0;
int ledPin = 53;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  analogWriteResolution(12);
  analogWrite(DAC0, 0);
  analogWrite(DAC1, 0);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  while (Serial.available() > 0 ) {
    char value = Serial.read();
    Comm += value;
    if (value == '\n') {
      isData = true;
    }
  }
  if (isData) {
    isData = false;
    if (Comm.startsWith("IDN")) {
      Serial.print("General DAQ Device built by Uetke. v.1.2019");
      Serial.print("\n");
    }
    else if (Comm.startsWith("OUT")) {
      channel = Comm[6];
      if (channel.toInt() == 1) {
        output = DAC1;
      }
      else if (channel.toInt() == 0) {
        output = DAC0;
      }
      tempValue = "";
      for (i = 8; i < Comm.length(); i++) {
        tempValue += Comm[i];
      }
      val = tempValue.toInt();
      analogWrite(output, val);
      Serial.print(tempValue);
    }
    else if (Comm.startsWith("IN")) {
      channel = Comm[5];
      input = channel.toInt();
      val = analogRead(input);
      Serial.print(val);
      Serial.print("\n");
    }
    else if (Comm.startsWith("DI")){
      Serial.println("Digital");
      channel = Comm[3]+Comm[4];
      tempValue = Comm[6];
      if (tempValue.toInt() == 0){
        digitalWrite(ledPin, LOW);
        Serial.println("OFF");
        Serial.println(ledPin);
        }
        else{
          digitalWrite(ledPin, HIGH);
          Serial.println("ON");
          Serial.println(channel.toInt());
          }
    }
    else {
      Serial.print("Command not known\n");
    }
    Comm = "";
  }
  delay(20);
}
