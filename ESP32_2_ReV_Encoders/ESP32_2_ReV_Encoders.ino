#include "ESP32Encoder.h"

// --- Pin Definitions (Ensure these go through your level shifters!) ---
// Encoder 1 (Front)
const int FRONT_A = 17; 
const int FRONT_B = 16; 
// Encoder 2 (Rear)
const int REAR_A = 18; 
const int REAR_B = 19; 

const long PPR = 8192; 
const long INTERVAL = 100; // 100ms

ESP32Encoder frontEncoder;
ESP32Encoder rearEncoder;

long prevCountFront = 0;
long prevCountRear = 0;
unsigned long prevTime = 0;

void setup() {
  Serial.begin(115200);
  
  // Initialize Front Encoder
  frontEncoder.attachFullQuad(FRONT_A, FRONT_B);
  frontEncoder.setFilter(0); // Set to 0 for 6000 RPM
  frontEncoder.setCount(0);

  // Initialize Rear Encoder
  rearEncoder.attachFullQuad(REAR_A, REAR_B);
  rearEncoder.setFilter(0); 
  rearEncoder.setCount(0);

  prevTime = millis();
  Serial.println("Dual Encoder Monitor Initialized");
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - prevTime >= INTERVAL) {
    // Read hardware registers
    long countF = frontEncoder.getCount();
    long countR = rearEncoder.getCount();
    
    float deltaT = (currentTime - prevTime) / 1000.0; // Seconds

    // RPM Calculation: (DeltaCounts / PPR) / (DeltaT / 60)
    float rpmF = ((float)(countF - prevCountFront) / PPR) / (deltaT / 60.0);
    float rpmR = ((float)(countR - prevCountRear) / PPR) / (deltaT / 60.0);

    // CSV format for the laptop to read: Time, FrontRPM, RearRPM
    Serial.print("DATA,");
    Serial.print(currentTime);
    Serial.print(",");
    Serial.print(rpmF, 2);
    Serial.print(",");
    Serial.println(-rpmR, 2);

    prevCountFront = countF;
    prevCountRear = countR;
    prevTime = currentTime;
  }
}