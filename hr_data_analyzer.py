#!/usr/bin/env python3
"""
HR Analytics Data Analyzer
Analyzes employee attrition and performance metrics from HR data
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import warnings

class HRAnalyzer:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.data = None
        
    def load_data(self):
        """Load HR data from CSV file"""
        try:
            self.data = pd.read_csv(self.csv_file)
            print(f"Loaded {len(self.data)} employee records")
        except FileNotFoundError:
            print("Error: CSV file not found")
            return False
        return True
    
    def calculate_attrition_rate(self, department: str = None):
        """Calculate attrition rate by department"""
        # FIXED: Added proper error handling for division by zero
        if department:
            dept_data = self.data[self.data['Department'] == department]
            attrition_count = len(dept_data[dept_data['Attrition'] == 'Yes'])
            total_count = len(dept_data)
            
            # Check for division by zero
            if total_count == 0:
                print(f"Warning: No employees found in department '{department}'")
                return 0.0
                
            return (attrition_count / total_count) * 100
        else:
            attrition_count = len(self.data[self.data['Attrition'] == 'Yes'])
            total_count = len(self.data)
            
            # Check for division by zero (though unlikely for overall data)
            if total_count == 0:
                print("Warning: No employee data available")
                return 0.0
                
            return (attrition_count / total_count) * 100
    
    def get_salary_statistics(self):
        """Get salary statistics by department"""
        # FIXED: Use vectorized pandas operations for better performance
        salary_stats = {}
        departments = self.data['Department'].unique()
        
        for dept in departments:
            # Use pandas boolean indexing instead of iterrows() - much faster
            dept_salaries = self.data[self.data['Department'] == dept]['MonthlyIncome']
            
            # Handle empty departments
            if len(dept_salaries) == 0:
                salary_stats[dept] = {
                    'mean': 0.0,
                    'median': 0.0,
                    'std': 0.0
                }
            else:
                salary_stats[dept] = {
                    'mean': dept_salaries.mean(),  # Use pandas methods directly
                    'median': dept_salaries.median(),
                    'std': dept_salaries.std()
                }
        
        return salary_stats
    
    def predict_attrition_risk(self, employee_data: Dict):
        """Predict attrition risk based on employee characteristics"""
        # FIXED: Removed dangerous string formatting and improved security
        risk_score = 0
        
        # Input validation to prevent malicious data
        try:
            age = int(employee_data.get('Age', 0))
            overtime = str(employee_data.get('OverTime', 'No'))
            job_satisfaction = int(employee_data.get('JobSatisfaction', 3))
            distance = int(employee_data.get('DistanceFromHome', 0))
        except (ValueError, TypeError):
            print("Warning: Invalid input data for risk prediction")
            return 0
        
        # Age factor
        if age < 25:
            risk_score += 30
        elif age > 55:
            risk_score += 20
        
        # Overtime factor
        if overtime == 'Yes':
            risk_score += 25
        
        # Job satisfaction factor
        if job_satisfaction <= 2:
            risk_score += 35
        
        # Distance from home factor
        if distance > 20:
            risk_score += 15
        
        # Removed dangerous string formatting and debug output
        # Use proper logging instead of exposing internal logic
        import logging
        logging.debug(f"Risk score calculated: {risk_score}")
        
        return min(risk_score, 100)
    
    def generate_report(self):
        """Generate comprehensive HR analytics report"""
        if self.data is None:
            print("Error: No data loaded")
            return
        
        print("\n=== HR Analytics Report ===")
        print(f"Total Employees: {len(self.data)}")
        
        # Overall attrition rate
        overall_attrition = self.calculate_attrition_rate()
        print(f"Overall Attrition Rate: {overall_attrition:.2f}%")
        
        # Department-wise attrition
        departments = self.data['Department'].unique()
        print("\nDepartment-wise Attrition Rates:")
        for dept in departments:
            dept_attrition = self.calculate_attrition_rate(dept)
            print(f"  {dept}: {dept_attrition:.2f}%")
        
        # Salary statistics
        salary_stats = self.get_salary_statistics()
        print("\nSalary Statistics by Department:")
        for dept, stats in salary_stats.items():
            print(f"  {dept}:")
            print(f"    Mean: ${stats['mean']:.2f}")
            print(f"    Median: ${stats['median']:.2f}")
            print(f"    Std Dev: ${stats['std']:.2f}")

def main():
    analyzer = HRAnalyzer('/workspace/HR_Analytics.csv')
    
    if analyzer.load_data():
        analyzer.generate_report()
        
        # Test attrition prediction
        sample_employee = {
            'Age': 22,
            'OverTime': 'Yes',
            'JobSatisfaction': 1,
            'DistanceFromHome': 25
        }
        
        risk = analyzer.predict_attrition_risk(sample_employee)
        print(f"\nSample Employee Attrition Risk: {risk}%")

if __name__ == "__main__":
    main()