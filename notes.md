- There are partners
- This partner pays worker by the hour
- Employees belong to a job group
- The job group determines their wages
- Each employee has a unique ID
- CSV file has (date, hours worked, emp id, job group)
- Footer has report ID
- Requirements
    - Parse CSV file and store data in relational DB
    - Display a payroll report
        - One row per employee, per pay period
        - Sort by employee ID, pay period
        - Report based on ALL data
- Two pay periods (1 - 15, 16 - ...)

Notes
- We should be able to support multiple partners (DONE)
- We should support multiple types of pay periods (DONE)
- We should abstract the date format used (DONE)
- Do we allow selections of columns for the CSV file 
- We need to think about changing of job groups (DONE)
- What if the partner decides to change the work period?


Models
- Partner - partner name
- Partner Profile - date settings, pay period
- Pay Period - 
- EmployeeWorkLog
- Payroll