# X5 Lite Controller for Android

A lightweight Android app built with **Kivy** that reads input from an **X5 Lite gamepad** (via USB OTG or Bluetooth) and sends real-time joystick/button data over **UDP**.

Perfect for controlling robots, drones, or simulators wirelessly from your Android device.

![App Screenshot](screenshot.png) <!-- Optional but recommended -->

---

## 🚀 Features
- Reads X5 Lite gamepad input using Kivy's native Android joystick support
- Sends data as JSON over UDP (configurable IP/port)
- Displays round-trip latency
- Auto-rotating UI (portrait + landscape)
- Saves IP/Port settings during session
- No root or special permissions required

---

## 📱 How to Use
1. **Connect your X5 Lite** via USB OTG or Bluetooth  
   → Make sure it's in **gamepad mode** (press **HOME + X**)
2. Open the app
3. Tap **"Configure IP/Port"** to set your target device address
4. Move sticks or press buttons → data is sent automatically

> 📦 **UDP Format**:  
> ```json
> {"lx": -100, "ly": 0, "rx": 0, "ry": 50, "btn": 16, "btnM": 0}
> ```

---

## 🛠️ Build from Source

### ⚠️ Important: Use the Correct Environment
This project **only builds reliably** with a specific combination:

| Component | Version |
|----------|--------|
| **Python** | 3.10+ (system Python) |
| **Cython** | `0.29.35` |
| **Kivy** | `2.1.0` |
| **Android NDK** | `r25b` |
| **Architectures** | `arm64-v8a` only |

> ❌ Do **not** use Cython 3.x or Kivy ≥2.2.1 — they cause build failures on Android.

### Step-by-Step Build

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install -y git build-essential python3-pip
2. **Install Cython**
   ```bash
   pip install --user "cython==0.29.35"
3. **Install buildozer**
   ```bash
   pip install --user buildozer
4. **Clone and build**
   ```bash
   git clone https://github.com/123monirith-sys/KivyApp.git
   cd KivyApp
   buildozer android debug
5. **Find your APK app**
   ```bash
   ls bin
   
   
    



   
