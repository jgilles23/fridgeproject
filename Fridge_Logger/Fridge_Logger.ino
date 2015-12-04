//NetFridge Arduino Code
//Written by Jordan Gilles

//libraries to include
#include <SD.h>
#include <Wire.h>
#include "RTClib.h"
#include <SPI.h>
#include <OneWire.h>

//Tempature definitions
// DS18B20 signal pin on digital pin 2
int const DS18B20_Pin = 2;
// Number of DS18B20 sensors
int const DS18B20_Num = 2;
// Array for storing temperature readings
float temperatures[DS18B20_Num];
// Temperature chip i/o
OneWire ds(DS18B20_Pin);

//Set times between data events
#define OPEN_SYNC_INTERVAL 15000 //time between serial writes when door open
#define CLOSED_SYNC_INTERVAL 60000 //time between serial writes when door closed
#define COLLECTION_INTERVAL 2000 //time between collections
#define READ_INTERVAL 1000 //time between reads of the serial port
#define COMPRESSOR_INTERVAL 300000 //time between compressor acuations = 5min

uint32_t previousPrint = 0; //millis time of the previos print
uint32_t previousCollect = 0; //millis time of previous collection of data
uint32_t previousRead = 0; //millis time of previous read of serial port
uint32_t previousCompressor = 0; //millis time of previous set of compressor
int previousDoorPos = 2; //Previous door position, 2 indicates just turned on
int previousCompressorState = 2; //PRevious compressor state, 2 indicates just turned on

//Set how data is displayed
#define ECHO_TO_LOG      1 //echo data to the SD card
#define ECHO_TO_SERIAL   0 // echo data to serial port
#define ECHO_TO_STRING   1 // echo data to string to be checked for print
#define WAIT_TO_START    0 // Wait for serial input in setup()

// the digital pins that connect to the LEDs
#define redLEDpin 13 //2
#define greenLEDpin 12 //3
#define printLEDpin 9
#define pythonLEDpin 8
#define compressorLEDpin 7

// The analog pins that connect to the sensors
#define doorPin 6           // analog 0
#define tempPin 1                // analog 1

#define aref_voltage 3.3         // we tie 3.3V to ARef and measure it with a multimeter!

//Time definitions
#define timeZoneCorrection -8 //time zone correction in hours
RTC_DS1307 RTC; // define the Real Time Clock object

// for the data logging shield, we use digital pin 10 for the SD cs line
const int chipSelect = 10;

// the logging file
File logfile;

//-------------------------
//ERROR FUNCTION
void error(char *str)
{
  Serial.print("error: ");
  Serial.println(str);

  // red LED indicates error
  digitalWrite(redLEDpin, HIGH);

  while (1);
}

//----------------------------------------
//----------------------------------------
//SETUP FUNCTION
void setup(void)
{  
  Serial.begin(9600);
  Serial.println();
  
  // use debugging LEDs
  pinMode(redLEDpin, OUTPUT);
  pinMode(greenLEDpin, OUTPUT);
  pinMode(printLEDpin, OUTPUT);
  pinMode(pythonLEDpin, OUTPUT);
  pinMode(compressorLEDpin, OUTPUT);
  digitalWrite(printLEDpin, LOW);
  digitalWrite(pythonLEDpin, LOW);
  // use the door logger
  pinMode(doorPin, INPUT);

#if WAIT_TO_START
  Serial.println("Type any character to start");
  while (!Serial.available());
#endif //WAIT_TO_START

  // initialize the SD card
  Serial.print("Initializing SD card...");
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    error("Card failed, or not present");
  }
  Serial.println("card initialized.");

  // create a new file
  char filename[] = "LOGGER00.CSV";
  for (uint8_t i = 0; i < 100; i++) {
    filename[6] = i / 10 + '0';
    filename[7] = i % 10 + '0';
    if (! SD.exists(filename)) {
      // only open a new file if it doesn't exist
      logfile = SD.open(filename, FILE_WRITE);
      break;  // leave the loop!
    }
  }

  if (! logfile) {
    error("couldnt create file");
  }

  Serial.print("Logging to: ");
  Serial.println(filename);

  // connect to RTC
  Wire.begin();
  RTC.begin();
  if (!RTC.begin()) {
    logfile.println("RTC failed");
#if ECHO_TO_SERIAL
    Serial.println("RTC failed");
#endif  //ECHO_TO_SERIAL
  }


  logfile.println("millis,unix,datetime,insideTemp,outsideTemp,doorPos");
#if ECHO_TO_SERIAL
  Serial.println("millis,unix,datetime,insideTemp,outsideTemp,doorPos");
#endif //ECHO_TO_SERIAL

  // If you want to set the aref to something other than 5v
  analogReference(EXTERNAL);
}

//-------------------------------------------
//--------------------------------------------
//MAIN FUNCTION
void loop(void){
  if (previousCollect + COLLECTION_INTERVAL <= millis()) {
    collect();
    previousCollect = millis();
  }
  if (previousRead + READ_INTERVAL <= millis()) {
    readData();
    previousRead = millis();
  }
  delay(1);
}

//-------------------------------------------
//-------------------------------------------
//RECERIVE DATA FROM SERIAL PORT
void readData() {
  if (Serial.available() > 0) {
    //read the incoming value
    int serialIn = Serial.parseInt();
    //Serial.print("User Input: ");
    //Serial.println(serialIn);
    //------------------
    //DATA SENT TO SERVER
    if (serialIn == 3) {
      //Raspberry Pi sent data to Server
      digitalWrite(pythonLEDpin,HIGH);
      delay(100);
      digitalWrite(pythonLEDpin,LOW);
    }
    //-------------------
    //CONNECTED TO RASPBERRY PI
    if (serialIn == 2) {
      //Welcome from Raspberry Pi
      for (int i = 0; i<5; i++) {
        delay(200);
        digitalWrite(pythonLEDpin,HIGH);
        delay(200);
        digitalWrite(pythonLEDpin,LOW);
      }
    }
    //---------------------
    //ACTUATE COMPRESSOR
    if (serialIn == 10 || serialIn == 11) {
      //Actuate the compressor if it has been long enough
      //Serial.print("Input Value: ");
      //Serial.print(serialIn);
      //Serial.print(" Previous State: ");
      //Serial.println(previousCompressorState);
      if ((serialIn==10 && previousCompressorState==11) || \
      (serialIn==11 && previousCompressorState==10)) {
        //Serial.println("Type 1");
        if (previousCompressor + COMPRESSOR_INTERVAL <= millis()) {
          //Serial.println("Blink LED");
          digitalWrite(compressorLEDpin, serialIn-10);
          //delay(100);
          //digitalWrite(compressorLEDpin, LOW);
          previousCompressor = millis();
          previousCompressorState = serialIn;
        }
      }
      else if ((previousCompressorState==2)) {
        //Serial.println("Type 2");
        digitalWrite(compressorLEDpin, serialIn-10);
        //delay(100);
        //digitalWrite(compressorLEDpin, LOW);
        previousCompressor = millis();
        previousCompressorState = serialIn;
      }
    }
  }
}

//--------------------------------------------
//--------------------------------------------
//COLLECT AND SEND DATA
void collect(void) {
  //Serial.println("Collecting");
//setup the echo to string
#if ECHO_TO_STRING
  String str1 = ""; //String to which serial output will be displayed until ready to print
#endif

  // delay for the amount of time we want between readings
  //delay(COLLECTION_INTERVAL); //((LOG_INTERVAL - 1) - (millis() % LOG_INTERVAL));

  //Set green LED to green
  digitalWrite(greenLEDpin, HIGH);
  
//------------------------------
//PULL CURRENT TIME
//run startup code
  //Pull the time in GMT
  DateTime now;
  now = RTC.now();
  //Set the pacific time to be displayed
  DateTime pacific (now.unixtime() timeZoneCorrection * 3600L);

//---------------------------------
//LOG MILISECONDS SINCE STARTING
  // log milliseconds since starting
  uint32_t m = millis();
  logfile.print(m);           // milliseconds since start
  logfile.print(", ");
#if ECHO_TO_SERIAL
  Serial.print(m);         // milliseconds since start
  Serial.print(", ");
#endif
#if ECHO_TO_STRING
  str1 = str1 + m + ", ";
#endif

//------------------------------------
//LOG CURRENT TIME
  // fetch the time
  //now = RTC.now();
  // log time
  logfile.print(now.unixtime()); // seconds since 1/1/1970
  logfile.print(", ");
  logfile.print('"');
  logfile.print(pacific.year(), DEC);
  logfile.print("/");
  logfile.print(pacific.month(), DEC);
  logfile.print("/");
  logfile.print(pacific.day(), DEC);
  logfile.print(" ");
  logfile.print(pacific.hour(), DEC);
  logfile.print(":");
  logfile.print(pacific.minute(), DEC);
  logfile.print(":");
  logfile.print(pacific.second(), DEC);
  logfile.print('"');
#if ECHO_TO_SERIAL
  Serial.print(now.unixtime()); // seconds since 1/1/1970
  Serial.print(", ");
  Serial.print('"');
  Serial.print(pacific.year(), DEC);
  Serial.print("/");
  Serial.print(pacific.month(), DEC);
  Serial.print("/");
  Serial.print(pacific.day(), DEC);
  Serial.print(" ");
  Serial.print(pacific.hour(), DEC);
  Serial.print(":");
  Serial.print(pacific.minute(), DEC);
  Serial.print(":");
  Serial.print(pacific.second(), DEC);
  Serial.print('"');
#endif //ECHO_TO_SERIAL
#if ECHO_TO_STRING
  str1 = str1 + now.unixtime() + ", ";
  str1 = str1 + '"' + pacific.year()+"/"+pacific.month()+"/"+pacific.day()+" ";
  str1 = str1 + pacific.hour()+":"+pacific.minute()+":"+pacific.second() + '"';
#endif

//--------------------------
//GET THE TEMPERATURES
  updateTemperaturesF();
  logfile.print(", ");
  logfile.print(temperatures[0]);
  logfile.print(", ");
  logfile.print(temperatures[1]);
#if ECHO_TO_SERIAL
  Serial.print(", ");
  Serial.print(temperatures[0]);
  Serial.print(", ");
  Serial.print(temperatures[1]);
#endif //ECHO_TO_SERIAL
#if ECHO_TO_STRING
  str1 = str1 + ", ";
  str1 = str1 + temperatures[0];
  str1 = str1 + ", ";
  str1 = str1 + temperatures[1];
#endif

//---------------------------
//WRITE ERROR IF BAD TEMPERATURE
  if (temperatures[0] == -1000) {
    digitalWrite(printLEDpin, HIGH);
    delay(2000);
  }
  else {
    digitalWrite(printLEDpin, LOW);
  }

//----------------------------
//GET DOOR STATE
  int doorPos = digitalRead(doorPin);
  logfile.print(", ");
  logfile.print(doorPos);
#if ECHO_TO_SERIAL
  Serial.print(", ");
  Serial.print(doorPos);
#endif
#if ECHO_TO_STRING
  str1 = str1 + ", " + doorPos;
#endif

//----------------------------
//PRINT NEW LINES
  logfile.println();
#if ECHO_TO_SERIAL
  Serial.println();
#endif // ECHO_TO_SERIAL

//----------------------------
//WRITE DATA TO THE DISK
  digitalWrite(greenLEDpin, LOW);
  // Now we write data to disk! Don't sync too often - requires 2048 bytes of I/O to SD card
  // which uses a bunch of power and takes time
  // blink LED to show we are syncing data to the card & updating FAT!
  digitalWrite(redLEDpin, HIGH);
  logfile.flush();
  digitalWrite(redLEDpin, LOW);

//-----------------------------
//DECIDE TO WRITE STRING TO SERIAL PORT\
#if ECHO_TO_STRING
  //run as data is collected every Z seconds
  //Serial.println(previousPrint);
  //previousPrint = millis();
  if ((doorPos == 0 && previousDoorPos == 1) || \
  (doorPos == 1 && previousDoorPos == 0) || (previousDoorPos == 2)) {
    Serial.println(str1);
    previousPrint = millis();
    digitalWrite(printLEDpin, HIGH);
    delay(100);
    digitalWrite(printLEDpin, LOW);
  }
  else if (doorPos == 0 && previousDoorPos == 0) {
    //Serial.println("Open");
    //if the door is open print every X seconds
    if (previousPrint + OPEN_SYNC_INTERVAL <= millis()){
      Serial.println(str1);
      previousPrint = millis();
      digitalWrite(printLEDpin, HIGH);
      delay(100);
      digitalWrite(printLEDpin, LOW);
    }
  }
  else {
    //Serial.println("Closed");
    //if the door is closed print every Y seconds
    if (previousPrint + CLOSED_SYNC_INTERVAL <= millis()){
      Serial.println(str1);
      previousPrint = millis();
      digitalWrite(printLEDpin, HIGH);
      delay(100);
      digitalWrite(printLEDpin, LOW);
    }
  }
  previousDoorPos = doorPos;
#endif

}

//--------------------------------------------
//--------------------------------------------
//GET TEMPERATURE UPDATES
// Get the temperature from multiple DS18B20 sensors
//In degrees Farenheight
void updateTemperaturesF() {
  updateTemperatures();
  for (int i = 0; i < DS18B20_Num; i++) {
    if ( temperatures[i] != -1000) {
      temperatures[i] = temperatures[i] * 9 / 5 + 32;
    }
  }
}
//For degress Celcius
void updateTemperatures() {

  byte data[9];
  byte addr[8];
  ds.reset_search();

  // Loop through the number of sensors
  for (int k = 0; k < DS18B20_Num; k++) {

    if (!ds.search(addr)) {
      temperatures[k] = -1000;
      continue;
    }
    if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      temperatures[k] = -1000;
      continue;
    }
    if (addr[0] != 0x28) {
      Serial.print("Device family is not recognized");
      temperatures[k] = -1000;
      continue;
    }

    //Serial.print("Addr: ");
    for (int i = 0; i < 8; i++ ) {
      //Serial.print(addr[i], HEX);
      if ( i < 7) {
        //Serial.print(".");
      }
    }
    //Serial.println();

    ds.reset();
    ds.select(addr);
    ds.write(0x44);
    delay(1);

    byte present = ds.reset();
    if ( present ) {
      ds.select(addr);
      ds.write(0xBE);

      for (int i = 0; i < 9; i++) {
        data[i] = ds.read();
      }
      byte temperature_LSB = data[0];
      byte temperature_MSB = data[1];

      int rawTemperature = (int(temperature_MSB << 8) + temperature_LSB);
      //Serial.print("Raw: ");
      //Serial.println(rawTemperature);

      float finalTemperature = 0.0625 * rawTemperature;
      temperatures[k] = finalTemperature;
    }
    else {
      temperatures[k] = -1000;
      continue;
    }
  }
}
