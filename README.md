# 📊 Mitsubishi Financial Matrix Calculator

A high-fidelity Streamlit web application designed to precisely match complex spreadsheet valuation structures for vehicle financing, accessory bundling, and localized insurance calculations. Built with a bespoke, editorial user interface optimized for financial scannability.

---

## ✨ Key Features

* **High-Fidelity Math Engine:** Replicates exact Excel formula behavior, tracking baseline template value configurations (`u19_valuation_base`) to handle additive step calculations dynamically.
* **Smart Insurance & VRI Matrix:** Automatically maps specific rates (e.g., 3.00% vs. 2.75% premiums) and custom administrative fees based on variant codes (PR, PRP, HLP, G08, etc.), falling back seamlessly to flat-rate rules for exceptions.
* **Precision VAT Logging:** Tracks 5% VAT implications across standard taxable components while maintaining isolated, non-taxable lines for specific financial options.
* **Premium UX Interface:** Tailored layout adopting standard UX scaling metrics, using a warm light clay palette paired with an intentional typographical system:
  * **Headings:** Quicksand (Geometric & modern)
  * **Data & Numerics:** Amethysta (Editorial, highly readable numeric rendering)
  * **Body Copy:** Karma (Balanced serif for scanning text)

---

## 🛠️ Data Dependency Architecture

The application automatically checks for and parses the following underlying master catalogs:

1. **`NFC New VRI Project (2).xlsx`** – Houses the primary core vehicle data, variant matrix sheets, and template accessories.
2. **`Bank & RMC Details.xlsx`** – Stores localized supplementary banking parameters and operational RMC rule parameters.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8 or higher
* `pip` package manager

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
