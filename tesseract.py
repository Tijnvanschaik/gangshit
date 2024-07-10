#%%
import os
import glob
import re
import csv
from PIL import Image
import pytesseract
# author: Tijn van Schaik




# thankyou for using the tesseract accounting software! this software will allow you to take a screenshot of 
# your invoice and add it to a csv file for data storage of your company
# the programm simple requires you to name the company of the invoice and asks if it is payed or not payed
# it cannot always find all the data it needs so if it cannot find the data it will say not found for you to add it later 

# preperation to use the software
# make sure you install pytesseract (pip install pytesseract)
# make sure you change the folder path to your own folder path (line 147) you can find this by simply taking a screenshot
# and looking for the file path where it went. apart from that a couple lines of code will be commented 
# these lines serve the simple purpose of testing if that part of the code works. i marked them down with a capital T for test
# if you wanna test these individual parts simply remove the # and you can run it
# apart from that enjoy the use and let me know if there are anny problems





def screenshot_folder(folder_path, file_extension="*"):
    try:
        # to find the file we will need a search pattern that uses the criteria that it is in the folder path we are using
        # it also checks if the file is a png
        search_pattern = os.path.join(folder_path, file_extension)
        
        # using the search filter it will grab all screenshots from the folder not just the most recent one which we are looking for
        list_of_files = glob.glob(search_pattern)
        
        # pretty simple if there are no files it will just say no files
        if not list_of_files:
            print("No files in directory")
            return None
        
        # now that we selected all files from the folder we will need to grab the most recent one 
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    
    # T
    # you can keep this commented like I'm doing now but let's say you are using it for the first time you will need to keep this up
    # since you might select the wrong file path
    # except PermissionError as e:
    #     return f"Permission Error: {e}"
    
    except Exception as e:
        return f"Error: {e}"

# this function will grab the file path we just used 
def screenshot(image_path):
    with Image.open(image_path) as img:
        # uses pytesseract on the uploaded image
        text = pytesseract.image_to_string(img)
        return text

# this function will be used to extract each word from the text based on the whitespaces between them
def extract_words(text):
    words = text.split()
    
    # creates an empty list to add all the words to
    extracted_words = []
    
    # for loop to loop through all the words we split from the image and strips all commas and stuff to be left with only the word
    for word in words:
        cleaned_word = word.strip('.,!?()[]{}:;"\'')
        extracted_words.append(cleaned_word)
    
    return extracted_words

# this function will be used to dissect the text we extracted

def dissect(text):
    results = {}

    # search pattern for individual information we are looking to extract/dissect from the text
    invoice_id_pattern = r'Invoice\sID\s+(\d+)'
    invoice_date_pattern = r'Invoice\sdate\s+(\d{2}-\d{2}-\d{4})'
    due_date_pattern = r'Due\sdate\s+(\d{2}-\d{2}-\d{4})'
    total_without_tax_pattern = r'Subtotal\s+([\d,]+\.\d{2})'
    total_with_tax_pattern = r'Total\s+([\d,]+\.\d{2})'

    # uses the invoice id pattern to look if something in the text fits the description we are looking for
    # once it found the data it will add it to the results variable so it could be used in the final function
    # the other functions here are for dissecting the other information
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

# this function will save the extracted data to a csv file
# it will make a new csv file if one does not exist already
def save_to_csv(results, csv_file_path):
    company_name = input("Enter the company name: ")
    paid_notpaid = input("Is the invoice paid yet? (Y/N): ")
    file_exists = os.path.isfile(csv_file_path)
    
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # writes the top of the csv file jsut like in excel
        if not file_exists:
            header = ["Company Name"] + list(results.keys()) + ["Paid Status"]
            writer.writerow(header)
        
        # adds the inputs we gave it being the company name and if it is not paid at the end and beggening
        row = [company_name] + list(results.values()) + [paid_notpaid]
        writer.writerow(row)

if __name__ == "__main__":
    folder_path = r'C:\Users\ttijn\Pictures\Screenshots'  # this is where you have to put your path to where the screenshots go
    csv_file_path = 'csv_file.csv'  # this will be the csv file you can realisticly name this anything you want
    
    
    # asignes the screenshot to latest screenshot taken to that variable
    latest_screenshot = screenshot_folder(folder_path, '*.png')
    
    # the final excecution of all functions we made il give a quick recap what every functiond does
    if latest_screenshot:
        # the main tesseract function
        extracted_text = screenshot(latest_screenshot)
        
        # splits the words and removes all commas and other things
        words = extract_words(extracted_text)
        
        # puts the words in another text for ease of use
        text = " ".join(words)
        
        # dissects the words we are looking for by using the patters we made
        invoice_results = dissect(text)

        # saves the data to the csv file
        save_to_csv(invoice_results, csv_file_path)
        
        
        # Print the extracted and dissected data
        print("Dissected data:")
        for key, value in invoice_results.items():
            print(f"{key}: {value}")



# %%
