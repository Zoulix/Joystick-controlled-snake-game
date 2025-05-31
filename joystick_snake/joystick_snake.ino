const int xPin = A0;
const int yPin = A1;


void setup() {
  Serial.begin(9600);
}

void loop() {
  int xVal = analogRead(xPin);
  int yVal = analogRead(yPin);


  // Envoie au format : x,y
  Serial.print(xVal);
  Serial.print(",");
  Serial.println(yVal);



  delay(100); // ajustable
}
