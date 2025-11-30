# OCRROO

A Python-based OCR and image processing project using OpenCV and Pillow.

---

## Features
- Real-time image capture and processing  
- Extracting only the coding segment from a OCR

---

## Requirements
Before running the program, ensure you have:
- **Python 3.12 or later**
- **Git** installed
- **uv 0.9.2 or later**

---

## Installation

### 1. Install uv
The command needs to be done in powershell, not git bash.
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Verify uv is installed
```powershell
uv --version
```

### 3. Clone the repository
```bash
git clone https://github.com/Turbat-git/TT-dip-pin-prj-adv-ocrroo-2025
cd TT-dip-pin-prj-adv-ocrroo-2025
```

### 4. Download dependencies
```bash
uv sync
```

### 5. Download AI model
Go to [Ollama Installation](https://ollama.com/download/mac) and follow the instruction to download ollama locally 

Confirm it is installed by running the following command.
```bash
ollama --version
```

After it is installed, run the following command
```bash
ollama pull llama3.1
```

### 6. Run the program (This will be changed as project progresses)
```bash
uvicorn main:app --reload
```

---
## Contribution

Contributors please visit the following link for the contribution guideline. [Contribution Guideline](https://github.com/Turbat-git/TT-dip-pin-prj-adv-ocrroo-2025/blob/main/docs/CONTRIBUTION.md)

---

## Code of Conduct

As students of North Metro TAFE, the student code of conduct extends to this project. The NMTAFE code of conduct can be 
found here, [Code of Conduct](https://www.northmetrotafe.wa.edu.au/sites/default/files/2025-01/Student%20Code%20of%20Conduct%202025_0.pdf)
