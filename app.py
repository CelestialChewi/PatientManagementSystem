from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import psycopg2

app = Flask(__name__)
conn = psycopg2.connect(database="",
                        host="",
                        user="",
                        password="",
                        port="")

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/view_patient', methods=['GET']) # View all patient's detail
def view_patient():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p."patient_ID", p."patient_name", p."patient_IC", p."patient_passport", p."patient_DOB",
        pa."allergen_ID", a."allergen_name", DATE_PART('year', current_timestamp) - DATE_PART('year', "patient_DOB") AS "patient_Age"
        FROM public."Patient"p
        LEFT JOIN public."PatientAllergies"pa ON p."patient_ID" = pa."patient_ID"
        LEFT JOIN public."Allergens"a ON pa."allergen_ID" = a."allergen_ID"
        ORDER BY p."patient_ID" ASC
        ''')
    
    rows = cursor.fetchall()
    
    return render_template("view_patient.html", patient_name=rows)

@app.route('/add_patient', methods=['GET']) # Success
def show_add_patient_form():
    return render_template('add_patient.html')

@app.route('/add_patient', methods=['POST']) # Success
def add_patient(): # Get the patient's information from the form
    print(request.form)
    patient_name = request.form['patient_name']
    patient_IC = request.form['patient_IC']
    patient_passport = request.form['patient_passport']
    patient_dob = request.form['patient_DOB']

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO public."Patient"("patient_name", "patient_IC", "patient_passport", "patient_DOB") 
        VALUES (%s, %s, %s, %s)''', (patient_name, patient_IC, patient_passport, patient_dob))
    conn.commit()

    return "Patient added successfully"

@app.route('/add_allergy/<patient_ID>', methods=['GET', 'POST'])
def add_allergy(patient_ID):
    if request.method == 'POST':
        patient_allergy = request.form['allergen_name']
        
        # Insert the allergy details into the PatientAllergies table                                # The code has to check the existing allergies before adding it
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO public."PatientAllergies"("patient_ID", "allergen_ID") 
            VALUES (%s, (SELECT "allergen_ID" FROM public."Allergens" 
            WHERE "allergen_name" = %s))''', (patient_ID, patient_allergy))
        conn.commit()

        return "Allergy added successfully"

    else:
        # Get the list of allergens to display in the dropdown menu
        cursor = conn.cursor()
        cursor.execute('''
            SELECT "patient_name" 
            FROM public."Patient" 
            WHERE "patient_ID" = %s''', (patient_ID,))
        
        patient_name = cursor.fetchone()[0]
        cursor.execute('''
            SELECT "allergen_name" 
            FROM public."Allergens"
            ''')
        
        allergens = [allergen[0] for allergen in cursor.fetchall()]

        return render_template('add_allergy.html', patient_ID=patient_ID, patient_name=patient_name, allergens=allergens)

@app.route('/edit_patient/<patient_ID>', methods=['POST', 'GET'])
def edit_patient(patient_ID):
    if request.method == "POST": # Update the patient's details
        patient_name = request.form['patient_name']
        patient_IC = request.form['patient_IC']
        patient_passport = request.form['patient_passport']
        patient_dob = request.form['patient_DOB']        

        cursor = conn.cursor() 
        cursor.execute('''
            UPDATE public."Patient" 
            SET "patient_name" = %s, "patient_IC" = %s, "patient_passport" = %s, "patient_DOB" = %s 
            WHERE "patient_ID" = %s''', (patient_name, patient_IC, patient_passport, patient_dob, patient_ID))

        conn.commit()

        return "Patient updated successfully"
    
    else: # Display the form to edit the patient's details
        cursor = conn.cursor() 
        cursor.execute('''
            SELECT * 
            FROM public."Patient" 
            WHERE "patient_ID" = %s''', (patient_ID,))
        patient = cursor.fetchone()

        return render_template("edit_patient.html", patient=patient)

@app.route('/view_medicine', methods=['GET'])
def medicine():
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ma.*, al."allergen_name", a."medicine_name"
        FROM public."Medicine"a
        JOIN public."MedicineAllergens"ma ON a."medicine_ID" = ma."medicine_ID"
        JOIN public."Allergens"al ON al."allergen_ID" = ma."allergen_ID"
        ORDER BY a."medicine_name" ASC
        ''')
    medicine_list = cursor.fetchall()
    cursor.close()

    return render_template('view_medicine.html', medicine_list=medicine_list)

@app.route('/add_allergen', methods=['GET', 'POST'])
def add_allergen():
    if request.method == 'POST':
        allergen_name = request.form.get('allergen_name')
        
        # Insert the new allergen into the database
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO public."Allergens" ("allergen_name") 
            VALUES (%s)''', (allergen_name,))
        conn.commit()
        cursor.close()
        
        return f'Successfully added allergen "{allergen_name}" to the database!'
    
    # If the request method is GET, render the template with the form
    return render_template('add_allergen.html')

@app.route('/edit_medicine/<int:medicine_id>', methods=['GET', 'POST'])
def edit_medicine(medicine_id):
    # Get the medicine details
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * 
        FROM public."Medicine" 
        WHERE "medicine_ID" = %s''', (medicine_id,))
    
    medicine = cursor.fetchone()

    if not medicine:
        return "Medicine not found"

    if request.method == 'POST':
        medicine_name = request.form['medicine_name']
        allergen_name = request.form['allergen_name']

        # Update the medicine name if it has been changed
        if medicine_name != medicine[1]:
            cursor.execute('''
                UPDATE public."Medicine" SET "medicine_name" = %s 
                WHERE "medicine_ID" = %s', (medicine_name, medicine_id)
            ''')

        # Get the allergen ID for the given allergen name
        cursor.execute('''
            SELECT "allergen_ID" 
            FROM public."Allergens" 
            WHERE "allergen_name" = %s', (allergen_name,)
            ''')
        allergen_id = cursor.fetchone()[0]

        # Check if the medicine-allergen relationship already exists
        cursor.execute('''
            SELECT * 
            FROM public."MedicineAllergens" 
            WHERE "medicine_ID" = %s AND "allergen_ID" = %s', (medicine_id, allergen_id)
            ''')
        existing_relationship = cursor.fetchone()

        # If the medicine-allergen relationship does not exist, insert the new relationship into the MedicineAllergy table
        if not existing_relationship:
            cursor.execute('''
                INSERT INTO public."MedicineAllergens"("medicine_ID", "allergen_ID")
                VALUES (%s, %s)', (medicine_id, allergen_id)
                ''')                                                            # Change to Update (assuming 1-1 relation)
            conn.commit()

        return "Medicine updated successfully"

    else:
        # Get the list of allergens to display in the dropdown menu
        cursor.execute('''
            SELECT "allergen_name" 
            FROM public."Allergens"
            ''')
        allergens = [allergen[0] for allergen in cursor.fetchall()]

        return render_template('edit_medicine.html', medicine=medicine, allergens=allergens)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        medicine_name = request.form['medicine_name']
        allergen_name = request.form['allergen_name']

        # Check if the medicine name already exists
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * 
            FROM public."Medicine" 
            WHERE "medicine_name" = %s', (medicine_name,)
            ''')
        existing_medicine = cursor.fetchone()

        # If the medicine name does not exist, insert the new medicine into the Medicine table
        if not existing_medicine:
            cursor.execute('''
                INSERT INTO public."Medicine"("medicine_name") 
                VALUES (%s) RETURNING "medicine_ID"', (medicine_name,)
                ''')
            medicine_id = cursor.fetchone()[0]

        else:
            medicine_id = existing_medicine[0]

        # Get the allergen ID for the given allergen name
        cursor.execute('''
            SELECT "allergen_ID" 
            FROM public."Allergens" 
            WHERE "allergen_name" = %s', (allergen_name,)
            ''')
    
        allergen_id = cursor.fetchone()[0]

        # Check if the medicine-allergen relationship already exists
        cursor.execute('''
            SELECT * 
            FROM public."MedicineAllergens" 
            WHERE "medicine_ID" = %s AND "allergen_ID" = %s', (medicine_id, allergen_id)
            ''')

        existing_relationship = cursor.fetchone()

        # If the medicine-allergen relationship does not exist, insert the new relationship into the MedicineAllergy table
        if not existing_relationship:
            cursor.execute('''
                INSERT INTO public."MedicineAllergens"("medicine_ID", "allergen_ID") 
                VALUES (%s, %s)', (medicine_id, allergen_id)
                ''')
            conn.commit()

        return "Medicine added successfully"

    else:
        # Get the list of allergens to display in the dropdown menu
        cursor = conn.cursor()
        cursor.execute('''
            SELECT "allergen_name" 
            FROM public."Allergens"
            ''')

        allergens = [allergen[0] for allergen in cursor.fetchall()]

        return render_template('add_medicine.html', allergens=allergens)

@app.route('/check_allergy')
def allergy():
    # Get the list of medicine names
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "medicine_name" 
        FROM public."Medicine"
        ''')
    
    medicine_names = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # Get the list of patient names
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "patient_name" 
        FROM public."Patient"
        ''')
    
    patient_names = [row[0] for row in cursor.fetchall()]
    cursor.close()

    return render_template('check_allergy.html', medicine_names=medicine_names, patient_names=patient_names)

@app.route('/add_to_cart/<patient_ID>', methods=['POST', 'GET'])
def add_to_cart(patient_ID):
        
    # Get the patient's name based on the patient ID
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "patient_name"
            FROM public."Patient"p
            WHERE p."patient_ID" = %s''', (patient_ID,))
    patient_name = cursor.fetchone()[0]
    cursor.close()

    if request.method == 'POST':
        medicine_name = request.form.get('medicine_name')
        quantity = request.form.get('quantity')

        # Get the patient ID based on the patient's name
        cursor = conn.cursor()
        cursor.execute('''
            SELECT *
                FROM public."Patient"p
                WHERE p."patient_ID" = %s''', (patient_ID,))
        patient_ID = cursor.fetchone()[0]
        cursor.close()

        # Get the list of allergies for the patient
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a."allergen_name"
                FROM public."PatientAllergies" pa
                JOIN public."Allergens" a ON pa."allergen_ID" = a."allergen_ID"
                WHERE pa."patient_ID" = %s''', (patient_ID,))
        allergies = [row[0] for row in cursor.fetchall()]
        cursor.close()

        # Check if the medicine is allergic to the patient
        cursor = conn.cursor()
        cursor.execute('''
            SELECT "allergen_name"
                FROM public."MedicineAllergens" ma
                JOIN public."Allergens" a ON ma."allergen_ID" = a."allergen_ID"
                JOIN public."Medicine" m ON ma."medicine_ID" = m."medicine_ID"
                WHERE m."medicine_name" = %s''', (medicine_name,))
        allergen = cursor.fetchone()[0] if cursor.rowcount else None
        cursor.close()

        if allergen and allergen in allergies:
            # If the medicine is allergic to the patient, return a warning
            return "Warning: This medicine is allergic to the patient's existing allergies! Please contact nearest specialist."

        # If the medicine is not allergic to the patient, add it to the view cart
        cursor = conn.cursor()  # Get the medicine ID based on the medicine name
        cursor.execute('''                              
            SELECT "medicine_ID"
                FROM public."Medicine"
                WHERE "medicine_name" = %s''', (medicine_name,))
        medicine_ID = cursor.fetchone()[0]

        # Insert the patient ID, medicine ID, and quantity into the view cart
        cursor.execute('''
            INSERT INTO public."ViewCart"("patient_ID", "medicine_ID", "quantity")
            VALUES (%s, %s, %s)''', (patient_ID, medicine_ID, quantity))
        conn.commit()
        cursor.close()

        # Return a success message
        return "Medicine added to cart successfully"

    # If the request method is GET, render the template with the form
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m."medicine_name"
            FROM public."Medicine" m
            ORDER BY m."medicine_name" ASC
        ''')
    medicines = [row[0] for row in cursor.fetchall()]
    cursor.close()

    return render_template('add_to_cart.html', patient_ID=patient_ID, medicines=medicines, patient_name=patient_name)

@app.route('/view_cart/<patient_ID>', methods=['GET', 'POST'])
def view_cart(patient_ID):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, m."medicine_name"
            FROM public."ViewCart"v
            JOIN public."Medicine"m on v."medicine_ID" = m."medicine_ID"
            WHERE v."patient_ID" = %s''', (patient_ID,))
    cart_items = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    cursor.execute('''
        SELECT "patient_name" FROM public."Patient"
        WHERE "patient_ID" = %s''', (patient_ID,))
    patient_name = cursor.fetchone()[0]
    cursor.close()

    if request.method == 'POST':
        Cart_ID = request.form['Cart_ID']
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM public."ViewCart"
            WHERE "Cart_ID" = %s ''', (Cart_ID))
        conn.commit()
        cursor.close()
        flash('Item has been removed from your cart', 'success')

    return render_template('view_cart.html', patient_ID=patient_ID, patient_name=patient_name, cart_items=cart_items)

@app.route('/submit_cart/<patient_ID>', methods=['GET', 'POST'])
def submit_cart(patient_ID):
    # Get the cart items for the patient
    cursor = conn.cursor()
    cursor.execute('''
        SELECT vc."patient_ID", vc."medicine_ID", vc."quantity", m."medicine_name"
            FROM public."ViewCart"vc
            JOIN public."Medicine"m ON vc."medicine_ID" = m."medicine_ID"
            WHERE vc."patient_ID" = %s''', (patient_ID,))
    cart_items = cursor.fetchall()
    cursor.close()

    if not cart_items:
        # If the cart is empty, return a message
        return "Your shopping cart is empty"

    # Get the patient's name
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "patient_name"
            FROM public."Patient"
            WHERE "patient_ID" = %s''', (patient_ID,))
    patient_name = cursor.fetchone()[0]
    cursor.close()

    # Get the current date and time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        # Insert the transaction details into the transaction history
        cursor = conn.cursor()
        for cart_item in cart_items:
            cursor.execute('''
                INSERT INTO public."TransactionHistory"("patient_ID", "medicine_ID", "quantity", "purchase_date")
                VALUES (%s, %s, %s, %s)''', (patient_ID, cart_item[1], cart_item[2], now))
        conn.commit()
        cursor.close()

        # Delete the items from the view cart
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM public."ViewCart"
            WHERE "patient_ID" = %s''', (patient_ID,))
        conn.commit()
        cursor.close()

        # Return a success message
        return f"Your shopping cart has been submitted successfully for {patient_name}!"

@app.route('/view_transaction_history/<patient_ID>', methods=['GET'])
def view_transaction_history(patient_ID):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT "patient_name"
            FROM public."Patient"
            WHERE "patient_ID" = %s''', (patient_ID,))
    patient_name = cursor.fetchone()[0]
    cursor.close()

    cursor = conn.cursor()
    cursor.execute('''
        SELECT th."order_ID", m."medicine_name", th."quantity", th."purchase_date"
            FROM public."TransactionHistory"th
            JOIN public."Medicine" m ON th."medicine_ID" = m."medicine_ID"
            WHERE th."patient_ID" = %s
            ORDER BY th."purchase_date" DESC''', (patient_ID,))
    transaction_history = cursor.fetchall()
    cursor.close()

    return render_template('view_transaction_history.html', patient_ID=patient_ID, patient_name=patient_name, transaction_history=transaction_history)


