#%%
from flask import Flask, render_template, redirect, url_for, request, flash, session
import os
import time
import csv
import re
from flask import send_file
from werkzeug.utils import secure_filename
from flask import send_from_directory
import glob
from PIL import Image
import pytesseract


app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Dummy user data for simplicity
users = {
    "admin": "password"
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('start_screen'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('start_screen'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/start')
def start_screen():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('start.html')

@app.route('/start')
def start():
    return render_template('start.html')


@app.route('/view_csv')
def view_csv():
    if 'username' not in session:
        return redirect(url_for('login'))

    csv_file_path = 'invoice_data.csv'
    csv_data = []
    if os.path.exists(csv_file_path):
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_data.append(row)

    return render_template('view_csv.html', csv_data=csv_data)


@app.route('/upload', methods=['GET', 'POST'])
def upload_invoice():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_time = time.time()
        company_name = request.form['company_name']
        paid_notpaid = request.form['paid_notpaid']
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            upload_time = time.time() - start_time
            print(f"Time taken to upload: {upload_time} seconds")

            start_time = time.time()
            csv_file_path = 'invoice_data.csv'
            results = process_screenshot(file_path, csv_file_path, company_name, paid_notpaid)
            processing_time = time.time() - start_time
            print(f"Time taken to process: {processing_time} seconds")

            return render_template('result.html', results=results)
    return render_template('upload.html')



# Function to preprocess image
def preprocess_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert('L')  # Convert to grayscale
        img = img.resize((img.width // 2, img.height // 2))  # Reduce resolution by half
        return img

# Function to process screenshot
def process_screenshot(image_path, csv_file_path, company_name, paid_notpaid):
    img = preprocess_image(image_path)
    text = pytesseract.image_to_string(img)
    words = text.split()
    cleaned_text = " ".join(word.strip('.,!?()[]{}:;"\'') for word in words)
    results = dissect(cleaned_text)
    results['Company Name'] = company_name
    results['Paid Status'] = paid_notpaid
    save_to_csv(results, csv_file_path)
    return results

# Function to dissect text and extract invoice details
def dissect(text):
    results = {}

    invoice_id_pattern = r'Invoice\sID\s+(\d+)'
    invoice_date_pattern = r'Invoice\sdate\s+(\d{2}-\d{2}-\d{4})'
    due_date_pattern = r'Due\sdate\s+(\d{2}-\d{2}-\d{4})'
    total_without_tax_pattern = r'Subtotal\s+([\d,]+\.\d{2})'
    total_with_tax_pattern = r'Total\s+([\d,]+\.\d{2})'

    invoice_id = re.search(invoice_id_pattern, text)
    if invoice_id:
        results['Invoice ID'] = invoice_id.group(1)
    else:
        results['Invoice ID'] = 'Not found'

    invoice_date = re.search(invoice_date_pattern, text)
    if invoice_date:
        results['Invoice Date'] = invoice_date.group(1)
    else:
        results['Invoice Date'] = 'Not found'

    due_date = re.search(due_date_pattern, text)
    if due_date:
        results['Due Date'] = due_date.group(1)
    else:
        results['Due Date'] = 'Not found'

    total_without_tax = re.search(total_without_tax_pattern, text)
    if total_without_tax:
        results['Total without Tax'] = total_without_tax.group(1)
    else:
        results['Total without Tax'] = 'Not found'

    total_with_tax = re.search(total_with_tax_pattern, text)
    if total_with_tax:
        results['Total with Tax'] = total_with_tax.group(1)
    else:
        results['Total with Tax'] = 'Not found'

    return results

# Function to save results to CSV
def save_to_csv(results, csv_file_path):
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            header = list(results.keys())
            writer.writerow(header)
        row = list(results.values())
        writer.writerow(row)





if __name__ == '__main__':
    app.run(debug=True)



# %%
