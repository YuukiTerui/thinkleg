#define LED_PIN 13
unsigned long time_ = 0;
unsigned long start_time = 0;
unsigned long read_time = 0;
int interval = 20;
int v = 0;
int data = 512;
boolean send_flag = false;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
  Serial.print("arduino is avairable\n");
}

void(* resetFunc) (void) = 0;

void read_v() {
  v = analogRead(A0);
}

int LPF(int y0, int raw) {
  float alpha = 0.7;
  float y;
  y = alpha * y0+ (1-alpha) * raw;
  return int(y);
}

void send_to_RPi() {
  time_ = millis() - start_time;
  data = LPF(data, v);
  String s = String(time_);
  s += ",";
  s += String(raw);
  s += ",";
  s += String(data);
  s += '\n';
  Serial.print(s);
}

void loop() {
  serialEvent();
  read_v();
  int tmp_time = millis()-time_read;
  if (tmp_time >= interval) {
    time_ = tmp_time;
    if (send_flag) {
      send_to_RPi();
    }
    time_read = millis();
  }
}

void serialEvent() {
  if(Serial.available() > 0) { // 内部でloop毎にSerial.available()>0の時呼ばれる関数なはずだから要らないのかもしれない．
    char c = Serial.read();
    switch (c) {
      case byte('0'):
        send_flag = false;
        digitalWrite(LED_PIN, LOW);
        break;
      case byte('1'):
        send_flag = true;
        start_time = millis();
        digitalWrite(LED_PIN, HIGH);
        break;
      // default:
      case byte('9'):
        resetFunc();
        break;
    }
  }
}
