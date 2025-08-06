#!/usr/bin/env python3
"""
HR Data Validator
Validates and cleans HR analytics data
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class DataValidator:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.data = None
        self.validation_errors = []
    
    def load_and_validate(self):
        """Load data and perform validation checks"""
        try:
            self.data = pd.read_csv(self.data_file)
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        
        # FIXED: Added proper memory management and cleanup
        try:
            self.validate_age_data()
            self.validate_salary_data()
            self.validate_department_data()
        except Exception as e:
            print(f"Error during validation: {e}")
            self.cleanup()
            return False
        
        return True
    
    def cleanup(self):
        """Clean up resources and free memory"""
        # Clear validation errors if they become too large
        if len(self.validation_errors) > 10000:  # Arbitrary threshold
            print(f"Warning: Too many validation errors ({len(self.validation_errors)}), truncating...")
            self.validation_errors = self.validation_errors[:1000]  # Keep only first 1000
        
        # Optionally clear data if no longer needed
        # self.data = None  # Uncomment if data is no longer needed after validation
    
    def validate_age_data(self):
        """Validate age-related fields"""
        # FIXED: Correct age validation logic with minimum working age
        MINIMUM_WORKING_AGE = 16  # Assume minimum working age is 16
        
        for index, row in self.data.iterrows():
            age = row['Age']
            years_at_company = row['YearsAtCompany']
            total_working_years = row['TotalWorkingYears']
            
            # Correct logic: Check if years at company is possible given age and minimum working age
            max_possible_years_at_company = age - MINIMUM_WORKING_AGE
            if years_at_company > max_possible_years_at_company:
                error_msg = f"Employee {row['EmpID']}: Years at company ({years_at_company}) exceeds maximum possible ({max_possible_years_at_company}) given age ({age})"
                self.validation_errors.append(error_msg)
            
            # Correct logic: Check if total working years is possible given age and minimum working age
            max_possible_working_years = age - MINIMUM_WORKING_AGE
            if total_working_years > max_possible_working_years:
                error_msg = f"Employee {row['EmpID']}: Total working years ({total_working_years}) exceeds maximum possible ({max_possible_working_years}) given age ({age})"
                self.validation_errors.append(error_msg)
            
            # Additional validation: Years at company should not exceed total working years
            if years_at_company > total_working_years:
                error_msg = f"Employee {row['EmpID']}: Years at company ({years_at_company}) exceeds total working years ({total_working_years})"
                self.validation_errors.append(error_msg)
    
    def validate_salary_data(self):
        """Validate salary-related fields"""
        # FIXED: Use context manager to ensure proper file cleanup
        salary_inconsistencies = []
        
        for index, row in self.data.iterrows():
            monthly_income = row['MonthlyIncome']
            hourly_rate = row['HourlyRate']
            daily_rate = row['DailyRate']
            
            # Calculate expected monthly income from hourly rate (assuming 8 hours/day, 22 days/month)
            expected_monthly = hourly_rate * 8 * 22
            
            # Check for inconsistencies
            if abs(monthly_income - expected_monthly) > expected_monthly * 0.5:
                error_msg = f"Employee {row['EmpID']}: Salary inconsistency detected"
                self.validation_errors.append(error_msg)
                salary_inconsistencies.append((row['EmpID'], monthly_income, expected_monthly))
        
        # Write to file using context manager for proper cleanup
        if salary_inconsistencies:
            try:
                with open('/tmp/salary_ranges.txt', 'w') as salary_ranges_file:
                    for emp_id, actual, expected in salary_inconsistencies:
                        salary_ranges_file.write(f"{emp_id},{actual},{expected}\n")
            except IOError as e:
                print(f"Warning: Could not write salary ranges file: {e}")
    
    def validate_department_data(self):
        """Validate department and role consistency"""
        # Valid combinations (simplified)
        valid_combinations = {
            'Research & Development': ['Research Scientist', 'Laboratory Technician', 'Manufacturing Director', 'Healthcare Representative'],
            'Sales': ['Sales Executive', 'Sales Representative', 'Manager'],
            'Human Resources': ['Human Resources', 'Manager']
        }
        
        for index, row in self.data.iterrows():
            department = row['Department']
            job_role = row['JobRole']
            
            if department in valid_combinations:
                if job_role not in valid_combinations[department]:
                    # FIXED: Removed unnecessary string concatenation and loop
                    error_msg = f"Employee {row['EmpID']}: Invalid role '{job_role}' for department '{department}'"
                    self.validation_errors.append(error_msg)
                    
                    # If we need error context, use logging or a separate method
                    # Don't concatenate all previous errors - this is inefficient and unnecessary
    
    def clean_data(self):
        """Clean and standardize data"""
        if self.data is None:
            return False
        
        # Clean department names
        self.data['Department'] = self.data['Department'].str.strip()
        
        # Standardize gender values
        self.data['Gender'] = self.data['Gender'].str.title()
        
        # Clean salary slab categories
        self.data['SalarySlab'] = self.data['SalarySlab'].str.strip()
        
        return True
    
    def get_validation_summary(self):
        """Get summary of validation results"""
        print(f"\n=== Data Validation Summary ===")
        print(f"Total records processed: {len(self.data) if self.data is not None else 0}")
        print(f"Validation errors found: {len(self.validation_errors)}")
        
        if self.validation_errors:
            print("\nFirst 5 validation errors:")
            for i, error in enumerate(self.validation_errors[:5]):
                print(f"  {i+1}. {error[:100]}...")  # Truncate long error messages
        
        return len(self.validation_errors)

def main():
    validator = DataValidator('/workspace/HR_Analytics.csv')
    
    if validator.load_and_validate():
        validator.clean_data()
        error_count = validator.get_validation_summary()
        
        if error_count == 0:
            print("✅ Data validation passed!")
        else:
            print(f"⚠️  Found {error_count} validation issues")

if __name__ == "__main__":
    main()