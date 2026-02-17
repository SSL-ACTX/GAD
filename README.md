# 🌿 GAD Corner - Municipality of Montalban

**GAD Corner** is the official digital hub for Gender and Development (GAD) initiatives for the Municipality of Montalban (Rodriguez), Rizal. This platform serves as a centralized archive for policies, reports, and community projects aimed at promoting gender equality, inclusivity, and citizen empowerment.

---

## 🚀 Features

- **Modular Architecture:** Utilizes Flask Blueprints for a scalable and organized backend.
- **Document Management:** Dedicated modules for Circulars, Office Orders, Memoranda, and Resolutions.
- **Dynamic Projects Archive:** Year-by-year breakdown of GAD-related community programs.
- **Developer Spotlight:** A unique, modular developer showcase highlighting the technical architects.
- **Citizen-Centric Design:** High-performance, responsive UI optimized for accessibility using Tailwind CSS.
- **Modern Search & Filter:** Intuitive tools to find legislative documents quickly.

---

## 🛠️ Technical Stack

### **Backend**
- **Python 3.x / Flask:** Core logic using a modular Blueprint pattern.
- **Jinja2:** Component-based templating system with inheritance.
- **Werkzeug:** Reliable routing and WSGI utility.

### **Frontend**
- **Tailwind CSS 3.4+:** Utility-first CSS framework for custom UI/UX.
- **JavaScript (ES6+):** Interactive navigation and mobile-responsive logic.
- **FontAwesome 6:** Comprehensive iconography for visual hierarchy.
- **Google Fonts (Poppins):** Clean, professional typography.

### **Build Tools**
- **npm / Node.js:** Manages Tailwind CSS compilation and minification.
- **Pip:** Python package management.

---

## 📂 Project Structure

```text
GAD                               
├─ routes                         # Flask Blueprints (Modular Logic)
│  ├─ main.py                     # Home, About, News
│  ├─ policies.py                 # Document Hub, Reports
│  ├─ projects.py                 # Year-based Archives
│  └─ legal.py                    # Privacy, Terms, Dev Team
├─ static                         # Static Assets
│  ├─ assets                      # Images & Brand Logos
│  ├─ input.css                   # Tailwind source
│  ├─ output.css                  # Compiled minified CSS
│  └─ script.js                   # UI Interactions
├─ templates                      # Jinja2 HTML Templates
│  ├─ about/                      # About, Vision, Committee
│  ├─ legal/                      # Legal documents
│  ├─ news/                       # News Feed & Articles
│  ├─ policies/                   # Legislative documents
│  ├─ projects/                   # Project Year archives
│  ├─ team/                       # Developer Showcase
│  ├─ base.html                   # Master Template
│  └─ index.html                  # Landing Page
├─ app.py                         # Application Entry Point
├─ package.json                   # Build Scripts & Dependencies
├─ requirements.txt               # Python Dependencies
└─ tailwind.config.js             # Tailwind Configuration
```

---

## ⚙️ Local Development Setup

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/Amitred11/GAD.git

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 2. Frontend (Tailwind) Setup
Ensure you have [Node.js](https://nodejs.org/) installed.
```bash
# Install Node dependencies
npm install

# Compile Tailwind CSS
npm run build

# Or use the watcher during development
npm run watch
```

---

## 👨‍💻 Development Team

This platform was engineered and designed by the Montalban IT Development Team.

**Lead Architect & UI/UX Frontend:** [Leoncio D. Amadore III](https://github.com/Amitred11)  
**Backend Specialist:** [Adrian Vine A. Cruz](https://github.com/AlT4lR)

---

## 📄 License & Proprietary Notice

**Copyright © 2026 Municipality of Montalban. All rights reserved.**

This software and all associated files are **proprietary**. Unauthorized use, copying, modification, or distribution of this Software is strictly prohibited without express written permission from the Municipality of Montalban.

---

## 📧 Contact & Support

For technical inquiries or system-related concerns:
- **Email:** gad@montalban.gov.ph
- **Location:** GAD Office, 2nd Floor Municipal Hall, Rodriguez, Rizal.

*Developed for the service of the people of Montalban.*
