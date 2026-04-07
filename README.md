# Campus Library Management (Lib50)
#### Video Demo: https://youtu.be/knkOCYuQDlk
#### Description: 

Campus Library Management (also referred to as Lib50) is a fully-responsive web application designed to simulate the digitalization (and streamline the process) of borrowing and returning books in an academic library setting.
Inspired from the design of 'Finance' assignment from Week 9 (Flask), the application allows a student to register for an account, where they can browse a catalog of books via live-search, check out books, return them, and view a complete history of borrows and returns.

### Technology Stack:
* **Frontend**: HTML5, CSS3, Vanilla JavaScript, BootStrap 5
* **Backend**: Python, Flask framework
* **Database**: SQLite3 (via CS50 SQL library)

### Project Structure and File breakdown:
**1. 'app.py'**
This is the central file of the application. It contains all the Flask routes with their implementation. Key routes include:
  * `/`: It queries the database for currently borrowed books and uses Python's `datetime` module to compare the `due_date` against the current date, dynamically injecting an `overdue` flag if the book is overdue for return.
  * `browse` & `fetch`: Handles book searching and borrowing. I implemented a custom API endpoint (`/fetch`) that returns JSON data based on a SQL `LIKE` query.
  * `/return` & `/history`: Manages book returning and a history of borrows and returns.
  * Authentication routes (`/login`, `/register`, `/logout`) for new registrations and session management.

**2. 'lib50.db'**
An SQLite database that stores all the relevant data. It contains four carefully designed tables: `users`, `books`, `borrowings`, and `history`.

**3. 'templates' directory**
  * `layout.html`: The parent html template containing boilerplate and HTML for recurring elements such as header and footer.
  * `index.html`: Features conditional Jinja logic to display either a "No books currently borrowed" empty state or a table of active borrowings.
  * `browse.html`: Contains the search interface. It relies on JavaScript to update the DOM without reloading the page.
  * `return.html` & `history.html`: Interfaces for returning borrowed books and viewing past transactions (i.e., borrows and returns).
  * `login.html` and `register.html`: Forms for user authentication, with dynamic Bootstrap alert banners for error handling.

**4. 'static/style.css'**
Contains custom CSS styles for tailored styling.

### Design Choices:
**1. Search functionality using asynchronous JavaScript**
Rather than forcing the user to submit a form and wait for a page reload, I opted to build an asynchronous search. In `browse.html`, an event listener monitors the search input, which, upon typing, triggers a `fetch()` call to the Flask `/fetch` route that queries the database and returns JSON. The DOM is then manipulated via JavaScript to display the results in real-time.

**2. Bootstrap against custom CSS**
I initially thought of sticking with custom CSS before realising the fact that leveraging BootStrap is far better which saves a lot of time and effort. However, there were a few things that required custom CSS styling to get the application fully tailored to my design choices.

**3. Handling invalid or malicious requests**
From the insights of Week 9 lecture about modifying HTML forms from the client-side to send invalid or malicious requests, I gracefully handled these scenarios with strong validation on the backend, displaying user-friendly error messages on such occasions. One such situation is a user modifying the `value` field of an `option` tag from the client-side while borrowing a book. I tackled this by confirming whether the `book_id` recieved actually exists in the databse and verifying that the book is currently available to borrow before executing the SQL `INSERT` to record the check out.
