#include <ESP8266WiFi.h>
#include <PubSubClient.h>
const char* ssid = "TP-Link_2AD8";
const char* password = "14730078";
const char* mqtt_server = "192.168.0.119";
const int mqtt_port = 1883;

const int pResistor = A0; // Photoresistor at Arduino analog pin A0
int resistorVal;

WiFiClient vanieriot;
PubSubClient client(vanieriot);

#include <SPI.h>
#include <MFRC522.h>
#define SS_PIN D8
#define RST_PIN D0
MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the class
MFRC522::MIFARE_Key key;
// Init array that will store new NUID
byte nuidPICC[4];
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522
  Serial.println();
  Serial.print(F("Reader :"));
  rfid.PCD_DumpVersionToSerial();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  // Note: To use the RFID RC522 module we use the SPI.h library which will allow us to
  // establish the communication between the ESP8266 card and the module; and the
  // MFRC522.h library which will allow us to dialogue with the module.
  Serial.println();
  Serial.println(F("This code scan the MIFARE Classic NUID."));
  Serial.print(F("Using the following key:"));
  printHex(key.keyByte, MFRC522::MF_KEY_SIZE);

  pinMode(pResistor, INPUT);
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("vanieriot");

  //light sensor
  char str[32] = "";
  resistorVal = analogRead(pResistor);
  if (!isnan(resistorVal))
  {
    dtostrf(resistorVal, 4, 2, str);
    client.publish("IoTlab/light/intensity", str);
  }

  //rfid
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when
  // idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;
  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;
  Serial.print(F("PICC type: "));
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  Serial.println(rfid.PICC_GetTypeName(piccType));
  // Check is the PICC of Classic MIFARE type
  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI && piccType != MFRC522::PICC_TYPE_MIFARE_1K && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    Serial.println(F("Your tag is not of type MIFARE Classic."));
    return;
  }
  if (rfid.uid.uidByte[0] != nuidPICC[0] || rfid.uid.uidByte[1] != nuidPICC[1] || rfid.uid.uidByte[2] != nuidPICC[2] || rfid.uid.uidByte[3] != nuidPICC[3]) {
    Serial.println(F("A new card has been detected."));
    client.publish("IoTlab/rfid/isnew", "true");
    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }
    Serial.println(F("The NUID tag is:"));
    Serial.print(F("In hex: "));
    printHex(rfid.uid.uidByte, rfid.uid.size);
    Serial.println();
    Serial.print(F("In dec: "));
    printDec(rfid.uid.uidByte, rfid.uid.size);
    Serial.println();
  } else 
  {
    client.publish("IoTlab/rfid/isnew", "false");
    Serial.println(F("Card read previously."));
  };
  // Halt PICC
  rfid.PICC_HaltA();
  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
  byteArray2string(rfid.uid.uidByte, rfid.uid.size, str);
  client.publish("IoTlab/rfid/id", str);
}
/**
Helper routine to dump a byte array as hex values to Serial.
*/
void printHex(byte* buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

// https://stackoverflow.com/questions/44748740/convert-byte-array-in-hex-to-char-array-or-string-type-arduino
void byteArray2string(byte* buffer, byte bufferSize, char out[]) {
  for (byte i = 0; i < bufferSize; i++) {
    byte nib1 = (buffer[i] >> 4) & 0x0F;
    byte nib2 = (buffer[i] >> 0) & 0x0F;
    out[i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
    out[i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
  }
  buffer[bufferSize*2] = '\0';
}
/**
Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte* buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 5 seconds before retrying
      delay(3000);
    }
  }
}