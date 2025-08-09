# Real-Time Gesture-Controlled Virtual Drawing System

A touchless virtual drawing tool that enables users to draw, erase, and interact with a digital canvas using **hand and facial gestures**.  
Built using **Python, OpenCV, and MediaPipe**, the system supports advanced gesture recognition, real-time responsiveness, and personalized calibration for diverse users.

---

## ✨ Features
- **Hand Gesture Control** – Draw and erase without touching any input device.
- **Facial Gesture Commands** – Perform actions like:
  - **Mouth Open** → Start drawing
  - **Eyebrow Raise** → Erase
  - **Winks** → Undo/Redo actions
- **Auto-Calibration** – Adapts to different facial structures for consistent accuracy.
- **Real-Time Processing** – Smooth, lag-free interaction using efficient MediaPipe pipelines.

---

## 🛠️ Tech Stack
- **Programming Language:** Python  
- **Computer Vision:** OpenCV  
- **Gesture Recognition:** MediaPipe  
- **Environment:** Any system with a webcam

---

## 📂 Project Structure
```
📁 Real-Time-Virtual-Drawing
│── 📄 main.py               # Main execution file
│── 📂 controllers           # Hand, face, and eye controllers
│── 📂 drawing               # Canvas drawing logic
│── 📄 requirements.txt      # Dependencies
│── 📄 README.md             # Project documentation
```

---

## ⚙️ Installation & Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/gesture-controlled-drawing.git
   cd gesture-controlled-drawing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## 🎯 Usage
- **Look into the webcam** and perform gestures.
- **Drawing Mode**: Open mouth or use specific hand gestures.
- **Erase Mode**: Raise eyebrow.
- **Undo/Redo**: Wink left or right eye.
- **Stop**: Neutral face.

---



---

## 🚀 Future Improvements
- Multi-user support  
- Customizable gestures  
- Cloud saving of drawings

---

## 📜 License
This project is licensed under the MIT License – feel free to use and modify.
