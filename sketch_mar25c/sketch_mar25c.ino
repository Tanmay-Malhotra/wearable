int ledb = 9;
int ledr = 8;
int battery = 7;

void setup() {
  pinMode(ledb,OUTPUT);
  pinMode(ledr,OUTPUT);
  pinMode(battery,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  
  

  while (Serial.available() == 0) {

  }
  

  int userChoice = Serial.parseInt();
  

  while (Serial.available() > 0) {
    Serial.read();
  }
  

  if (userChoice == 0) {
    Serial.println("Optimal weather conditions predicted for tommorrow");
    Serial.println("Charging paused till tommorrow");
    digitalWrite(ledb,HIGH);
    
  } 
  else if (userChoice == 1) {
    Serial.println("Bad Weather Conditions detected");
    Serial.println("Charging Battery via Grid");
    digitalWrite(ledr,HIGH);
    digitalWrite(battery,HIGH);
    delay(10000);
    digitalWrite(ledr,LOW);
    delay(10000);
    digitalWrite(battery,LOW);
       
  }
  else {
    Serial.println("Invalid input! Please enter only 0 or 1.");
  }
  
  Serial.println();
  delay(10000);
}
