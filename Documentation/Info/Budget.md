<div align="center">

# AIris Project Budget

**Hardware components for the AIris vision assistant**

---

## Budget Overview

**Target Total**: ৳8,000 - ৳12,000 BDT (~$70-110 USD)  
**Architecture**: ESP32-CAM (WiFi) + Arduino (Bluetooth Audio) + Server

---

</div>

## Hardware Components

### ESP32-CAM Module (Video Capture)

| Component | Specification | Est. Price (BDT) | Notes |
|:----------|:--------------|:-----------------|:------|
| ESP32-CAM | With OV2640 camera | ৳800 - ৳1,200 | WiFi streaming |
| USB Programmer | FTDI or CH340 | ৳200 - ৳400 | For flashing firmware |
| Camera mount | Clip or 3D printed | ৳100 - ৳300 | Spectacle attachment |

**Subtotal: ৳1,100 - ৳1,900**

---

### Arduino Audio Module (Bluetooth I/O)

| Component | Specification | Est. Price (BDT) | Notes |
|:----------|:--------------|:-----------------|:------|
| Arduino Nano | ATmega328P | ৳300 - ৳500 | Compact controller |
| HC-05/HC-06 | Bluetooth module | ৳400 - ৳600 | Audio communication |
| Microphone | Electret or MEMS | ৳100 - ৳250 | Voice input |
| Speaker | 2W mini speaker | ৳100 - ৳200 | Audio output |
| Amplifier | PAM8403 or similar | ৳80 - ৳150 | Audio amplification |
| Battery | 3.7V Li-Po | ৳300 - ৳500 | Portable power |
| Charging module | TP4056 | ৳50 - ৳100 | Battery charging |

**Subtotal: ৳1,330 - ৳2,300**

---

### Physical Controls

| Component | Specification | Est. Price (BDT) | Notes |
|:----------|:--------------|:-----------------|:------|
| Push buttons | Tactile switches | ৳50 - ৳100 | Mode selection |
| Wires/cables | Jumper wires, etc. | ৳100 - ৳200 | Connections |
| Housing | 3D printed / DIY | ৳200 - ৳500 | Device enclosure |

**Subtotal: ৳350 - ৳800**

---

### Server (Development/Processing)

| Component | Specification | Est. Price | Notes |
|:----------|:--------------|:-----------|:------|
| Laptop/PC | Any modern computer | *Existing* | Runs AI models |
| Webcam | USB camera (for testing) | *Existing* | Development testing |

**Subtotal: ৳0 (using existing equipment)**

---

## Total Estimated Cost

| Category | Min (BDT) | Max (BDT) |
|:---------|:---------:|:---------:|
| ESP32-CAM System | ৳1,100 | ৳1,900 |
| Arduino Audio | ৳1,330 | ৳2,300 |
| Controls & Housing | ৳350 | ৳800 |
| Miscellaneous | ৳200 | ৳500 |
| **TOTAL** | **৳2,980** | **৳5,500** |

**Buffer for extras**: ৳1,000 - ৳2,000

**Final Budget**: ~৳4,000 - ৳7,500 BDT

---

## Cost Comparison

| Architecture | Est. Cost | Notes |
|:-------------|:---------:|:------|
| **ESP32 + Arduino** | ৳5,000-7,500 | Current approach |
| Raspberry Pi-based | ৳15,000-20,000 | Previous approach |
| Commercial device | ৳50,000+ | Market alternatives |

**Savings with current architecture**: ~৳10,000+

---

## Procurement Sources

### Local (Bangladesh)

- **Techshop BD** — ESP32, Arduino, modules
- **Robolab BD** — Electronic components
- **Daraz** — General electronics
- **Elephant Road** — Physical components

### Online (International)

- **AliExpress** — Bulk components (longer shipping)
- **Amazon** — Premium components

---

## Budget Allocation

```
ESP32 Camera System    ████████░░░░ 35%
Arduino Audio System   ████████░░░░ 35%
Controls & Housing     ████░░░░░░░░ 15%
Miscellaneous          ███░░░░░░░░░ 15%
```

---

## Development Phases

### Phase 1: Core Hardware (৳2,500)
- [ ] ESP32-CAM + programmer
- [ ] Arduino Nano + Bluetooth
- [ ] Basic testing setup

### Phase 2: Audio System (৳1,500)
- [ ] Microphone + speaker
- [ ] Amplifier + battery
- [ ] Audio integration

### Phase 3: Assembly (৳1,500)
- [ ] Physical buttons
- [ ] Enclosure/housing
- [ ] Cable management

---

## Notes

- Prices are estimates for Bangladesh market (Dec 2025)
- Server uses existing laptop/PC — no additional cost
- 3D printing costs vary based on local availability
- Battery life depends on component selection
- Consider buying extras of small components

---

<div align="center">

*Budget updated for ESP32 + Arduino architecture*

</div>
