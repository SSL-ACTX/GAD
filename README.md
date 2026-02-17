# 🌿 GAD Corner - Municipality of Montalban

**GAD Corner** is the official digital hub for Gender and Development (GAD) initiatives for the Municipality of Montalban (Rodriguez), Rizal. This platform serves as a centralized archive for policies, reports, and community projects aimed at promoting gender equality, inclusivity, and citizen empowerment.

---

## 🚀 Features

- **Modular Architecture:** Utilizes Flask Blueprints for a scalable and organized backend.
- **Live Search & Suggestions:** Real-time autocomplete API providing instant access to municipal resources and documents.
- **Production Security:** Integrated security headers (CSP, HSTS) and protection against XSS and Clickjacking.
- **Anti-Scraper Protection:** Advanced rate-limiting and automated bot-blocking middleware to protect government data.
- **Dynamic Projects Archive:** Year-by-year breakdown of GAD-related community programs.
- **Citizen-Centric Design:** High-performance, responsive UI optimized for accessibility using Tailwind CSS.

---

## 🛠️ Technical Stack

### **Backend**
- **Python 3.x / Flask:** Core logic using a modular Blueprint pattern.
- **Flask-Talisman:** Production-grade security headers and HTTPS enforcement.
- **Flask-Limiter:** Rate-limiting logic for anti-scraping and brute-force protection.
- **Jinja2:** Component-based templating system with inheritance.

### **Frontend**
- **Tailwind CSS 3.4+:** Utility-first CSS framework for custom UI/UX.
- **JavaScript (ES6+):** Async Fetch API for live search and mobile-responsive logic.
- **FontAwesome 6:** Comprehensive iconography for visual hierarchy.

### **Build & Environment**
- **Node.js / npm:** Tailwind CSS compilation and minification pipeline.
- **python-dotenv:** Secure environment variable management.
- **Waitress:** Production-grade WSGI HTTP server.

---

## 📂 Project Structure

```text
GAD                               
├─ routes                         # Flask Blueprints (Modular Logic)
│  ├─ main.py                     # Home, About, News, Search API
│  ├─ policies.py                 # Document Hub, Reports
│  ├─ projects.py                 # Year-based Archives
│  └─ legal.py                    # Privacy, Terms, Dev Team
├─ static                         # Static Assets
│  ├─ assets                      # Images & Brand Logos
│  ├─ input.css                   # Tailwind source
│  ├─ output.css                  # Compiled minified CSS
│  └─ script.js                   # Live Search & UI logic
├─ templates                      # Jinja2 HTML Templates
│  ├─ about/                      # About, Vision, Committee
│  ├─ news/                       # News Feed & Articles
│  ├─ policies/                   # Legislative documents
│  ├─ projects/                   # Project Year archives
│  ├─ search-results.html         # Dynamic search UI
│  ├─ base.html                   # Master Template (Security Integrated)
│  └─ index.html                  # Landing Page
├─ app.py                         # Secure Entry Point (Middleware enabled)
├─ package.json                   # Build Scripts
├─ requirements.txt               # Refined Production Dependencies
└─ .env.example                   # Template for environment secrets
```

---

## ⚙️ Local Development Setup

### 1. Environment Configuration
Create a `.env` file in the root directory:
```text
SECRET_KEY=your_random_secret_string
DEBUG=True
```

### 2. Backend Setup
```bash
# Install refined dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 3. Frontend (Tailwind) Setup
```bash
# Install Node dependencies
npm install

# Compile & Minify CSS
npm run build

# Use watcher for active development
npm run watch
```

---

## 🛡️ Security Implementation

- **Rate Limiting:** Default limits set to 50 requests per hour per IP to prevent aggressive scraping.
- **Content Security Policy (CSP):** Strict policy governing script and style sources to mitigate XSS risks.
- **Bot Mitigation:** Automated blocking of common scraper User-Agents (Requests, Selenium, Scrapy, etc.).
- **Data Privacy:** Full compliance with the **Data Privacy Act of 2012 (RA 10173)**.

---

## 👨‍💻 Development Team

This platform was engineered and designed by the Montalban IT Development Team.

**Lead Architect & UI/UX Frontend:** [Leoncio D. Amadore III](https://github.com/Amitred11)  
**Backend & Security Specialist:** [Adrian Vine A. Cruz](https://github.com/AlT4lR)

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
