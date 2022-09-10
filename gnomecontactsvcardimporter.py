#!/usr/bin/env python3

import sys
import datetime
import io
import random
import sqlite3
import vobject

db_path = sys.argv[1]
vcard_path = sys.argv[2]

def generate_uid():
    return 'pas-id-%030x' % random.randrange(16**40)

def handle_vcard(vcard_lines, endTagFound=True):
    # Get raw data with newlines since we parsed out whitespace earlier
    vcard_raw = '\n'.join(vcard_lines)
    
    # Use vobject to read the card data
    vcard = vobject.readOne(vcard_raw)
    
    ### Figure out information needed for DB columns
    
    # Generate a unique uid
    uid = generate_uid()

    # Not supported in vCard 2.1 which is what I imported so I don't care    
    nickname = None # Make sure Null in DB
    
    #FN
    full_name = None
    try:
        full_name = vcard.fn.value
    except AttributeError:
        pass
        
    #N
    given_name = None
    family_name = None
    file_as = full_name
    try:
        # Name is split into different parts
        # We need given name and family name for the DB if available
        name = vcard.n_list
        if len(name) >= 1:
            family_name = name[0].strip()
        if len(name_split) >= 2:
            given_name = name[1].strip()
            # file_as in the DB (what is this?) is formatted this way
            file_as = family_name + ', ' + given_name
    except AttributeError:
        pass
    
    # Insert the main db entry. Only added things with names
    # A blank full_name may or may not have broken loading things in Gnome-Contacts
    if full_name != None:
        print('Importing: ' + full_name)
        
        # Insert Main entry
        insert_db_main(uid, file_as, nickname, full_name, given_name, family_name, vcard_raw)
        
        # Insert Email Addresses
        try:
            for email in vcard.email_list:
                insert_db_email(uid, email.value)
        except AttributeError:
            pass
        
        # Insert Phone Numbers
        try:
            for tel in vcard.tel_list:
                insert_db_phone(uid, tel.value)
        except AttributeError:
            pass

def insert_db_email(uid, email):
    # Connect to the DB
    db_con = sqlite3.connect(db_path)
    db_cursor = db_con.cursor()

    # Insert the email address
    db_cursor.execute('insert into folder_id_email_list (uid, value) values (?, ?)', (uid, email))
    
    # commit
    db_con.commit()

    # Close the DB connection
    db_con.close()
        
def insert_db_phone(uid, phone):
    # Connect to the DB
    db_con = sqlite3.connect(db_path)
    db_cursor = db_con.cursor()

    # Insert the phone number
    db_cursor.execute('insert into folder_id_phone_list (uid, value) values (?, ?)', (uid, phone))
    
    # commit
    db_con.commit()

    # Close the DB connection
    db_con.close()

def insert_db_main(uid, file_as, nickname, full_name, given_name, family_name, vcard):
    db_path = sys.argv[1]
    # Connect to the DB
    db_con = sqlite3.connect(db_path)
    db_cursor = db_con.cursor()

    # Get a timestamp for the Rev column
    rev_date_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Insert the contact data
    db_cursor.execute('insert into folder_id (uid, Rev, file_as, nickname, full_name, given_name, family_name, vcard, is_list, list_show_addresses, wants_html, x509Cert, pgpCert) values (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, 0)', (uid, rev_date_time, file_as, nickname, full_name, given_name, family_name, vcard))
    
    # commit
    db_con.commit()

    # Close the DB connection
    db_con.close()
    
if __name__ == '__main__':
    # Read command line parameters
    if(len(sys.argv) < 3):
        print('The contacts.db filepath and vcard filepath are required parameters')
    else:
        # Open the VCard file
        with open(vcard_path, 'r', encoding='utf-8') as vcard_file:
            cur_vcard_lines = []
            in_vcard = False
            # Iterate through it
            while line := vcard_file.readline():
                line = line.rstrip()

                if line == 'BEGIN:VCARD':
                    # If we reach here while in the middle of a vCard
                    # It means the previous one wasn't terminated properly
                    if in_vcard:
                        handle_vcard(cur_vcard_lines, endTagFound=false)
                        cur_vcard_lines = []
                        
                    # Start new card
                    in_vcard = True
                    cur_vcard_lines.append(line)
                elif line == 'END:VCARD':
                    if in_vcard:
                        cur_vcard_lines.append(line)
                        
                        # Handle writing the card to the db
                        # and prepare for the next card
                        handle_vcard(cur_vcard_lines)
                        cur_vcard_lines = []
                        in_vcard = False
                elif in_vcard:
                    # Keep track of all the card's information
                    cur_vcard_lines.append(line)
