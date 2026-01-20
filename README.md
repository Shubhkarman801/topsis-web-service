# 🌐 TOPSIS Web Service  
**Cloud-Based Multi-Criteria Decision Support System**

This project is a **Flask-based web application** that implements the **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)** algorithm to help users rank alternatives based on multiple criteria.  

Users can upload a CSV file, provide weights and impacts for each criterion, and receive a ranked result file directly via **email**. The system is designed to be simple, secure, and deployment-ready for real-world and academic use.

---

## 🚀 Features

- Web-based interface for non-technical users
- Upload CSV dataset for evaluation
- Supports benefit (`+`) and cost (`-`) criteria
- Automatic weight normalization
- Input validation (file format, weights, impacts, email)
- Email delivery of results as CSV attachment
- Cross-platform and cloud deployable
- Lightweight and fast execution

---

## Working

1. **Upload Dataset**  
   User uploads a CSV file where the first column represents alternatives and the remaining columns represent criteria.

2. **Provide Parameters**  
   - Weights (comma-separated values)  
   - Impacts (`+` for benefit, `-` for cost)  
   - Email ID to receive results

3. **Processing Engine**  
   The system:
   - Normalizes criteria using vector normalization
   - Applies user-defined weights
   - Determines ideal best and worst solutions
   - Computes separation distances
   - Calculates TOPSIS scores and ranks

4. **Result Delivery**  
   The ranked CSV file is automatically emailed to the user.

---

