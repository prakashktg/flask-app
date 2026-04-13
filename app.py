from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Admin credentials (in production, use hashed passwords and database storage)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Login required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login as admin to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database initialization
def init_db():
    conn = sqlite3.connect('riasec.db')
    cursor = conn.cursor()
    
    # Create students table with new fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            school_name TEXT NOT NULL,
            address TEXT NOT NULL,
            fathers_name TEXT NOT NULL,
            fathers_phone TEXT NOT NULL,
            mothers_name TEXT NOT NULL,
            mothers_phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create test_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            r_score INTEGER DEFAULT 0,
            i_score INTEGER DEFAULT 0,
            a_score INTEGER DEFAULT 0,
            s_score INTEGER DEFAULT 0,
            e_score INTEGER DEFAULT 0,
            c_score INTEGER DEFAULT 0,
            dominant_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on app startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        school_name = request.form['school_name']
        address = request.form['address']
        fathers_name = request.form['fathers_name']
        fathers_phone = request.form['fathers_phone']
        mothers_name = request.form['mothers_name']
        mothers_phone = request.form['mothers_phone']
        
        # Store student info in database
        conn = sqlite3.connect('riasec.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, grade, school_name, address, fathers_name, fathers_phone, mothers_name, mothers_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, grade, school_name, address, fathers_name, fathers_phone, mothers_name, mothers_phone))
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Store student_id in session
        session['student_id'] = student_id
        session['student_name'] = name
        
        return redirect(url_for('test'))
    
    return render_template('register.html')

@app.route('/test')
def test():
    if 'student_id' not in session:
        return redirect(url_for('register'))
    return render_template('test.html')

@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'student_id' not in session:
        return redirect(url_for('register'))
    
    student_id = session['student_id']
    
    # Define which questions belong to each RIASEC type
    riasec_questions = {
        'R': [1, 7, 14, 22, 30, 32, 37],    # Realistic questions
        'I': [2, 11, 18, 21, 26, 33, 39],   # Investigative questions
        'A': [3, 8, 17, 23, 27, 31, 41],    # Artistic questions
        'S': [4, 12, 13, 20, 28, 34, 40],   # Social questions
        'E': [5, 10, 16, 19, 29, 36, 42],   # Enterprising questions
        'C': [6, 9, 15, 24, 25, 35, 38]     # Conventional questions
    }
    
    # Calculate scores for each RIASEC type
    scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    
    # Get all radio button answers
    for key in request.form:
        if key.startswith('q') and '_yes' in request.form[key]:
            # Extract question number from key (e.g., "q1" -> 1)
            question_num = int(key[1:])
            
            # Check which RIASEC type this question belongs to and count it
            for riasec_type, questions in riasec_questions.items():
                if question_num in questions:
                    scores[riasec_type] += 1
                    break  # Found the type, no need to check others
    
    # Find the top 3 scores to create Interest Code
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    interest_code = ''.join([score[0] for score in sorted_scores[:3]])
    
    # Store results in database
    conn = sqlite3.connect('riasec.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO test_results 
        (student_id, r_score, i_score, a_score, s_score, e_score, c_score, dominant_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, scores['R'], scores['I'], scores['A'], 
          scores['S'], scores['E'], scores['C'], interest_code))
    conn.commit()
    conn.close()
    
    # Clear session and redirect to thank you page
    session.clear()
    flash('Test completed successfully! Your results have been saved. Please contact the administrator to view your results.', 'success')
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('riasec.db')
    cursor = conn.cursor()
    
    # Get total students and tests
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM test_results')
    total_tests = cursor.fetchone()[0]
    
    # Get recent results
    cursor.execute('''
        SELECT s.name, s.grade, s.school_name, tr.dominant_type, tr.created_at
        FROM students s
        JOIN test_results tr ON s.id = tr.student_id
        ORDER BY tr.created_at DESC
        LIMIT 10
    ''')
    recent_results = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_students=total_students,
                         total_tests=total_tests,
                         recent_results=recent_results)

@app.route('/admin/results')
@admin_required
def admin_results():
    conn = sqlite3.connect('riasec.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, s.name, s.grade, s.school_name, tr.dominant_type, tr.created_at
        FROM students s
        JOIN test_results tr ON s.id = tr.student_id
        ORDER BY tr.created_at DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    # Convert dominant_type to string for each result
    processed_results = []
    for result in results:
        processed_results.append((
            result[0],  # id
            result[1],  # name
            result[2],  # grade
            result[3],  # school_name
            str(result[4]) if result[4] is not None else '',  # dominant_type
            result[5]   # created_at
        ))
    
    return render_template('admin_results.html', results=processed_results)

@app.route('/admin/student/<int:student_id>')
@admin_required
def admin_student_detail(student_id):
    conn = sqlite3.connect('riasec.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.grade, s.school_name, s.address, s.fathers_name, s.fathers_phone, s.mothers_name, s.mothers_phone, tr.*
        FROM students s
        JOIN test_results tr ON s.id = tr.student_id
        WHERE s.id = ?
        ORDER BY tr.created_at DESC
        LIMIT 1
    ''', (student_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        student_data = {
            'name': result[0],
            'grade': result[1],
            'school_name': result[2],
            'address': result[3],
            'fathers_name': result[4],
            'fathers_phone': result[5],
            'mothers_name': result[6],
            'mothers_phone': result[7],
            'scores': {
                'R': result[10],  # tr.r_score
                'I': result[11],  # tr.i_score
                'A': result[12],  # tr.a_score
                'S': result[13],  # tr.s_score
                'E': result[14],  # tr.e_score
                'C': result[15]   # tr.c_score
            },
            'dominant_type': str(result[16]) if result[16] is not None else ''  # tr.dominant_type
        }
        return render_template('admin_student_detail.html', data=student_data)
    else:
        flash('Student not found!', 'error')
        return redirect(url_for('admin_results'))

@app.route('/admin/delete_result/<int:student_id>', methods=['POST'])
@admin_required
def delete_result(student_id):
    try:
        conn = sqlite3.connect('riasec.db')
        cursor = conn.cursor()
        
        # First get student name for confirmation message
        cursor.execute('SELECT name FROM students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if student:
            student_name = student[0]
            
            # Delete test results first (due to foreign key constraint)
            cursor.execute('DELETE FROM test_results WHERE student_id = ?', (student_id,))
            
            # Delete student record
            cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully deleted test result for {student_name}', 'success')
        else:
            flash('Student not found!', 'error')
            
    except Exception as e:
        flash(f'Error deleting result: {str(e)}', 'error')
        conn.rollback()
        conn.close()
    
    return redirect(url_for('admin_results'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  