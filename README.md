# ShopEasy-web-app
Project Overview: 
ShopEasy is a web-based shopping list tool created as a final project.Users can build 
and manage shopping lists, explore items by category, and keep track of their 
purchases. The program prioritizes usability, security, and clean backend design. 
Project Objectives 
• Enable users to build and manage shopping lists. 
• Categorize grocery goods (meat, dairy, vegetables, etc.). 
• Provide search and filtering functionality. 
• Implement safe user authentication. 
• Demonstrate CRUD procedures using a relational database. 
System Features 
User Authentication 
• User Registration and Login 
• Secure password hashing. 
• Session-based authentication. 
• Protected routes (login is required) 
• Unauthorized access returns HTTP 401. 
• Forbidden access returns HTTP 403. 
Categories 
• View all categories. 
• Create new categories. 
• Categories are used to organize shopping items. 
Items 
• Add items under specific categories 
• Search items by name 
• Filter items by category 
• Update and delete items 
Shopping Lists 
• Create personal shopping lists 
• Add items to lists 
• Remove items from lists 
• Mark items as checked/unchecked 
• Users can only access their own lists 
Search & Filter 
• Search items by keyword 
• Filter items by category 
• Filter list items by checked or unchecked status 
Technologies Used 
Backend 
• Python 
• Flask 
• Flask-SQLAlchemy 
• Flask-Login 
• Flask-CORS 
Database 
• MySQL (via XAMPP & phpMyAdmin) 
Frontend 
• HTML 
• CSS 
• JavaScript (Fetch API) 
Database Structure 
The system uses a relational database with the following tables: 
• users 
• categories 
• items 
• lists 
• list_items 
Relationships are handled using foreign keys and SQLAlchemy ORM. 
Security Measures 
• Passwords are hashed before storage 
• Login-required routes protected using decorators 
• Users cannot access or modify other users’ data 
• Proper HTTP status codes are returned for errors 
How to Run the Project 
1. Start MySQL using XAMPP 
2. Create a database named: 
3. shopeasy 
4. Activate the virtual environment: 
5. venv\Scripts\activate 
6. Run the Flask application: 
7. python app.py 
8. Open the browser and visit: 
9. http://127.0.0.1:5000/ 
Project Status 
✔ Backend completed 
✔ Authentication implemented 
✔ Search and filtering implemented 
✔ Frontend functional 
✔ Ready for submission 
Developer 
Hope Nokuthaba Sethibang 
System Development – Final Project
