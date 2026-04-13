# RIASEC Career Interest Test - Flask Application

A web-based application for administering the RIASEC (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) Career Interest Test. This application helps students discover their personality type and get career recommendations based on their interests.

## Features

- **Student Registration**: Collect student information (name, class, date of birth)
- **42-Question Test**: Complete RIASEC assessment with all original questions
- **Automated Scoring**: Calculate scores for all six personality types
- **Detailed Results**: Display individual scores and dominant personality type
- **Career Recommendations**: Provide relevant career suggestions based on personality type
- **Database Storage**: Store all student information and test results in SQLite database
- **Admin View**: View all test results with statistics and breakdowns

## RIASEC Personality Types

1. **Realistic (R)**: Prefer working with things, machines, tools, plants, or animals
2. **Investigative (I)**: Prefer working with ideas, thinking, organizing, and understanding
3. **Artistic (A)**: Prefer working with forms, designs, and patterns, communicating feelings and ideas
4. **Social (S)**: Prefer working with people, helping, informing, teaching, or serving
5. **Enterprising (E)**: Prefer working with people, influencing, persuading, performing, leading, or managing
6. **Conventional (C)**: Prefer working with data, keeping records, filing, reproducing materials, following a set plan

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   - Open your web browser
   - Go to `http://localhost:5000`

## Usage

### For Students
1. Visit the home page
2. Click "Start the Test"
3. Fill in your registration information (name, class, date of birth)
4. Complete the 42-question test by checking boxes for statements that describe you
5. Submit the test to view your results
6. Review your scores and career recommendations

### For Administrators
1. Visit the home page
2. Click "View All Results" to see all test results
3. View statistics and breakdowns by personality type

## Database Schema

The application uses SQLite with two main tables:

### Students Table
- `id`: Primary key
- `name`: Student's full name
- `class_name`: Student's class/grade
- `date_of_birth`: Student's date of birth
- `created_at`: Timestamp of registration

### Test Results Table
- `id`: Primary key
- `student_id`: Foreign key to students table
- `r_score`: Realistic score
- `i_score`: Investigative score
- `a_score`: Artistic score
- `s_score`: Social score
- `e_score`: Enterprising score
- `c_score`: Conventional score
- `dominant_type`: Highest scoring personality type
- `created_at`: Timestamp of test completion

## File Structure

```
riasec-test/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── riasec.db            # SQLite database (created automatically)
└── templates/           # HTML templates
    ├── index.html       # Home page
    ├── register.html    # Student registration form
    ├── test.html        # Test questions
    ├── results.html     # Individual results page
    └── all_results.html # Admin results view
```

## Customization

### Adding New Questions
To add new questions to the test:
1. Edit `templates/test.html`
2. Add new question divs with appropriate RIASEC type names
3. Update the scoring logic in `app.py` if needed

### Modifying Career Recommendations
To update career suggestions:
1. Edit `templates/results.html`
2. Modify the career lists for each personality type

### Styling Changes
All styling is contained within the HTML templates using CSS. Modify the `<style>` sections in each template to change the appearance.

## Security Notes

- Change the `app.secret_key` in `app.py` to a secure random string for production use
- Consider adding authentication for admin features in production
- The application uses session management for tracking student progress

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` or stop other applications using port 5000
2. **Database errors**: Delete `riasec.db` and restart the application to recreate the database
3. **Template errors**: Ensure all template files are in the `templates/` directory

### Error Messages
- If you see "No module named 'flask'", run `pip install -r requirements.txt`
- If the database doesn't work, check file permissions in the project directory

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application. 