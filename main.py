import pandas as pd
import re
from phonemizer import phonemize
from phonemizer.separator import Separator
import logging
import time
import gc
from multiprocessing import Pool, current_process


def clean_trade_name(name):
    # Define patterns to remove based on categories
    packaging_terms = [
        r' IN (DUPLEX|DEXTOSE|STERILE PLASTIC|PLASTIC) CONTAINER', r' IN WATER', r' LACTATED RINGER\'S', r' RINGER\'S'
    ]
    chemical_additives = [
        r' \(K\)', r' SODIUM', r' POTASSIUM', r' CHLORIDE', r' CALCIUM', 
        r' GLUCONATE', r' CAFFEINE', r' PHOSPHATE', r' CITRATE', r' ZINC', 
        r' SULFATE', r' ASCORBATE', r' ACID', r'MICRONIZED', r' FLAVORED'
        r' HYDROCHLORIDE', r'DEXTROSE', r'HYDROCHLOROTHIAZIDE',r'HYDROCHLORIDE',
        r'SUDIUM', r'CHLORIDE', r'POTASSIUM', r'CALCIUM', r'GLUCONATE', r'PHOSPHATE',
        r'ACETATE', r'ACID', r'HYDROCHLORIDE', r'HYDROCHLOROTHIAZIDE', r'HYDROCHLORIDE',
        r'SODIUM', r'CHLORIDE', r'POTASSIUM', r'CALCIUM', r'GLUCONATE', r'PHOSPHATE',
    ]
    medical_conditions = [
        r' ALLERGY', r' COLD', r' FLU', r' NASAL', r' SINUS', r' DRY', r' WET', r' COUGH',
        r' DUAL ACTION', r' NIGHTTIME', r' DAYTIME', r' NIGHT', r' DAY', r'FLAVORED', r' CONGESTION', r' HOUR'
        r' SPRINKLE', r' RELIEF', r' RELIEVER', r' RELIEVING', r' RELIEVES', r' RELIEVED', r' RELIEVEMENT',
    ]
    operational_terms = [
        r' FREE', r' PRESERVATIVE FREE', r' KIT$', r' MEQ', r'COPACKAGED', r' PREFILLED', r' ELECTROLYTES',
        r' \(FOR WOMEN\)|WOMEN\'S|WOMEN', r' \(FOR MEN\)|MEN\'S', r' \(FOR CHILDREN\)|CHILDREN\'S|CHILDREN'
    ]
    # Revised handling for specific terms
    specific_drug_forms = [
        # Handles forms and abbreviations as standalone words or at the end of the string
        #r'\b(XR|ER|AMP|B|F|XL|S|M|P|I|T|D|E|A|G|K|V|N|C|Z|FE|DI|CR|LA|LO|IV|PM|HR|TC|CD|PD|HC|LQ|IB|PF|ES|BK|SR|PH|DM|XT|LS|SF|GA|DS|EC|AC|MS|HF|NO|AD|ST|VU|FM|HB|AR|AF|HD|SX|AT|XE|SM|CQ|LD|FS|RT|LR|TR|PA|II|GK|JR|MB)\b',
    ]

    common_phrases = [
        r' WITH ', r' AND ', r' W/', r' IN '
        r' WITH$', r' AND$', r' W/$', r' IN$'
    ]
    #numerical_values = [
    #    r' [\d.]+%?', r'\d+', r'/', r','
    #]
    name = re.sub(r'L\.A\.', 'LA', name)

    # Modify the list by adding the new category
    patterns_to_remove = packaging_terms + chemical_additives + medical_conditions + \
                     operational_terms + specific_drug_forms + common_phrases
    
    # Apply the removal of patterns
    name = re.sub('|'.join(patterns_to_remove), ' ', name)
    name = re.sub('|'.join(patterns_to_remove), ' ', name)

    name = re.sub(r' IN$', '', name)

    name = re.sub(r'-', ' ', name)
    name = re.sub(r';', ' ', name)    
    # Additional clean-up steps to remove non-alphabetic characters and normalize spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)  # Remove non-alphabetic characters
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'IN$', '', name)
    name = name.strip().lower()  # Collapse multiple spaces and convert to lower case


    if name == '':
        name = 'PHON_ERROR02 (empty)'
    return name

def phonemize_word(word, language='en-us', backend='espeak'):
    separator = Separator(phone='', word=' ', syllable=None)
    try:
        if word == 'PHON_ERROR02 (empty)':
            return "PHON_ERROR02"
        phonemized_word = phonemize(
            word,
            language=language,
            backend=backend,
            separator=separator,
            strip=True
        )
        return phonemized_word
    except Exception as e:
        print(f"Error in {word}: {str(e)}")
        return "PHON_ERROR01"

def Gender_Children(row):
    name = row['Trade_Name_Processed']
    route = row['Route']
    category = 0
    # Specific patterns for matching with uppercase
    if re.search(r'\b(FOR WOMEN|WOMEN\'S|WOMEN)\b', name):
        category = 1
    elif route == 'VAGINAL':
        category = 1
    elif re.search(r'\b(FOR MEN|MEN\'S)\b', name):
        category = 2
    elif re.search(r'\b(FOR CHILDREN|CHILDREN\'S|CHILDREN)\b', name):
        category = 3
    return category

def Date_Processed(date):
    # Mapping of month abbreviations to their numerical representation
    month_mapping = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    
    # if contains "Approved" return 1/1/1982
    if re.search(r'Approved', date):
        return '1982-01-01'

    # Splitting the date string into components
    parts = date.replace(',', '').split()
    month, day, year = parts[0], parts[1], parts[2]

    # Converting the month name to a number
    month_number = month_mapping[month]

    # Forming the standardized date format 'YYYY-MM-DD'
    standardized_date = f'{year}-{month_number}-{day.zfill(2)}'
    
    return standardized_date

def Split_DF_Route(word):
    Dosage_form = word.split(';')[0]
    Main_Dosage_form = Dosage_form
    Main_Dosage_form = re.sub(r'FOR ', '', Main_Dosage_form)
    Main_Dosage_form = Main_Dosage_form.split(' ')[0]
    # remove ","
    Main_Dosage_form = re.sub(r',', '', Main_Dosage_form)
    Route = word.split(';')[1]
    return pd.Series([Main_Dosage_form, Dosage_form, Route])

def setup_logger():
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - {current_process().name} - %(levelname)s - %(message)s')

def process_batch(data_chunk, batch_index):
    """Process a single batch of data, including phonemization."""
    setup_logger()  # Setup logger for each process
    logging.info(f"Processing batch {batch_index+1} starting with index {data_chunk.index[0]}")
    data_chunk['Phonemized'] = data_chunk['Trade_Name_Processed'].apply(phonemize_word)
    gc.collect()
    logging.info(f"Completed batch {batch_index+1}")
    return data_chunk

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    df = pd.read_csv('products.csv')
    df = df[df['Type'] != 'DISCN']
    df['Trade_Name_Processed'] = df['Trade_Name'].apply(clean_trade_name)
    df['Date_Processed'] = df['Approval_Date'].apply(Date_Processed)
    df[['Main_Dosage_form', 'Dosage_Form', 'Route']] = df["DF;Route"].apply(Split_DF_Route)
    df['Gender_Children'] = df.apply(Gender_Children, axis=1)
    df['unique_group'] = pd.factorize(df['Trade_Name_Processed'])[0] + 1
    df = df.drop_duplicates(subset=['Trade_Name_Processed']).reset_index(drop=True)
    
    df = df.iloc[3000:]

    df.to_csv('/app/data/phonemized_products_before_phonemizer4.csv', index=False, encoding='utf-8-sig')

    start = time.time()
    batch_size = 50  # Adjust batch size based on your data and system capabilities
    batches = [(df.iloc[i:i + batch_size], i // batch_size) for i in range(0, len(df), batch_size)]

    with Pool(processes=4) as pool:  # Adjust number of processes based on your system
        processed_batches = pool.starmap(process_batch, batches)
    
    # Concatenate all processed batches back into a single DataFrame
    df = pd.concat(processed_batches)
    logging.info(f"Completed processing all words, total time: {time.time() - start:.2f} seconds")
    df.to_csv('/app/data/phonemized_products_final.csv4', index=False, encoding='utf-8-sig')
    print("Final data saved successfully")