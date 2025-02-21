#include <Stepper.h>
#include <DHT.h>  // Include the DHT library

#define STEPS_PER_REV 2048
#define DEFAULT_SPEED 10
#define LED_PIN 13
#define CCD_LED_PIN 12
#define DHTPIN 2       // Pin where the DHT11 is connected
#define DHTTYPE DHT11  // DHT 11 sensor type

Stepper azimuthMotor(STEPS_PER_REV, 8, 10, 9, 11);
Stepper altitudeMotor(STEPS_PER_REV, 4, 6, 5, 7);

float targetAz = 0, targetAlt = 0;
float currentAz = 0, currentAlt = 0;
bool abortSlew = false;
bool blinkLed = false;
unsigned long lastBlinkTime = 0;
bool blinkState = false;
int motorSpeed = DEFAULT_SPEED;

DHT dht(DHTPIN, DHTTYPE);  // Initialize DHT sensor

void setup() {
  Serial.begin(9600);
  azimuthMotor.setSpeed(motorSpeed);
  altitudeMotor.setSpeed(motorSpeed);

  pinMode(LED_PIN, OUTPUT);
  pinMode(CCD_LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  digitalWrite(CCD_LED_PIN, LOW);

  dht.begin();  // Start the DHT sensor
  Serial.println("microMONET is ready for some stargazing!");
}

void moveBothSteppersInterruptible(int stepsAz, int stepsAlt) {
  int stepsMovedAz = 0, stepsMovedAlt = 0;
  int maxSteps = max(abs(stepsAz), abs(stepsAlt));
  for (int i = 0; i < maxSteps; i++) {
    if (Serial.available()) {
      String input = Serial.readStringUntil('\n');
      input.trim();
      if (input == "ABORT") {
        abortSlew = true;
        Serial.println("Slew aborted!");
        break;
      }
      processCommand(input);
    }
    if (abortSlew) break;

    // Move azimuth motor
    if (i < abs(stepsAz)) {
      azimuthMotor.step(stepsAz > 0 ? 1 : -1);
      stepsMovedAz += (stepsAz > 0 ? 1 : -1);
      currentAz += (stepsAz > 0 ? 1 : -1) / (STEPS_PER_REV / 360.0); // Update currentAz in real-time
    }

    // Move altitude motor
    if (i < abs(stepsAlt)) {
      altitudeMotor.step(stepsAlt > 0 ? 1 : -1);
      stepsMovedAlt += (stepsAlt > 0 ? 1 : -1);
      currentAlt += (stepsAlt > 0 ? 1 : -1) / (STEPS_PER_REV / 360.0); // Update currentAlt in real-time
    }
  }

  // Final position update in case of abort
  if (abortSlew) {
    Serial.print("Aborted at ALT: ");
    Serial.print(currentAlt);
    Serial.print(" AZ: ");
    Serial.println(currentAz);
  }
}

void processCommand(String input) {
  if (input == "GET_POS") {
    Serial.print("ALT: ");
    Serial.print(currentAlt);
    Serial.print(" AZ: ");
    Serial.println(currentAz);
  } else if (input == "LED_ON") {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED ON");
  } else if (input == "HI_MIMO") {
    Serial.println("HELLO!");
  } else if (input == "LED_OFF") {
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED OFF");
  } else if (input == "CCD_ON") {
    digitalWrite(CCD_LED_PIN, HIGH);
    Serial.println("CCD LED ON");
  } else if (input == "CCD_OFF") {
    digitalWrite(CCD_LED_PIN, LOW);
    Serial.println("CCD LED OFF");
  } else if (input.startsWith("SET_SPEED ")) {
    int newSpeed = input.substring(10).toInt();
    if (newSpeed >= 1 && newSpeed <= 15) {
      motorSpeed = newSpeed;
      azimuthMotor.setSpeed(motorSpeed);
      altitudeMotor.setSpeed(motorSpeed);
      Serial.print("Speed set to ");
      Serial.print(motorSpeed);
      Serial.println(" RPM");
    } else {
      Serial.println("Invalid speed! Use 1-15 RPM.");
    }
  } else if (input.startsWith("ALT:") && input.indexOf("AZ:") > 0) {
    int altIndex = input.indexOf("ALT:") + 4;
    int azIndex = input.indexOf("AZ:") + 3;
    targetAlt = input.substring(altIndex, input.indexOf(" ", altIndex)).toFloat();
    targetAz = input.substring(azIndex).toFloat();

    Serial.print("Slewing to ALT: ");
    Serial.print(targetAlt);
    Serial.print(" AZ: ");
    Serial.println(targetAz);

    int stepsAlt = (targetAlt - currentAlt) * (STEPS_PER_REV / 360.0);
    int stepsAz = (targetAz - currentAz) * (STEPS_PER_REV / 360.0);
    abortSlew = false;
    moveBothSteppersInterruptible(stepsAz, stepsAlt);
    if (!abortSlew) {
      currentAlt = targetAlt;
      currentAz = targetAz;
    }
  } else if (input == "GET_TEMP") {
    // Read temperature from DHT11
    float temperature = dht.readTemperature();

    // Check if readings are valid
    if (isnan(temperature)) {
      Serial.println("Failed to read from DHT sensor!");
    } else {
      Serial.print("Temperature: ");
      Serial.print(temperature);
      Serial.println(" °C");
    }
  } else if (input == "GET_HUMI") {
    // Read humidity from DHT11
    float humidity = dht.readHumidity();

    // Check if readings are valid
    if (isnan(humidity)) {
      Serial.println("Failed to read from DHT sensor!");
    } else {
      Serial.print("Humidity: ");
      Serial.print(humidity);
      Serial.println(" %");
    }
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    processCommand(input);
  }
}