import argparse
import os
from tqdm import tqdm as original_tqdm

# Monkey patch tqdm to always use leave=False
class QuietTqdm(original_tqdm):
    def __init__(self, *args, **kwargs):
        # Set leave=False by default but allow override
        if 'leave' not in kwargs:
            kwargs['leave'] = False
        super().__init__(*args, **kwargs)

# Replace the original tqdm with our patched version
import tqdm as tqdm_module
tqdm_module.tqdm = QuietTqdm

# Now import the anonymizer after patching tqdm
from dicomanonymizer import anonymize, keep

def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "input",
        help="Path to the input directory.",
    )
    parser.add_argument(
        "output",
        help="Path to the output directory.",
    )
    args = parser.parse_args()

    input_dicom_path = args.input
    output_dicom_path = args.output

    extra_anonymization_rules = {}

    # Per https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
    # it is all right to retain only the year part of the birth date for
    # de-identification purposes.
    def set_date_to_year(dataset, tag):
        element = dataset.get(tag)
        if element is not None:
            element.value = f"{element.value[:4]}0101" # YYYYMMDD format

    # Patient's Birth Date
    extra_anonymization_rules[(0x0010, 0x0030)] = set_date_to_year 
    # Study Date
    extra_anonymization_rules[(0x0008, 0x0020)] = set_date_to_year

    # Patient Sex (keep)
    extra_anonymization_rules[(0x0010, 0x0040)] = keep
    # Accession Number (keep)
    extra_anonymization_rules[(0x0008, 0x0050)] = keep
    # Series Description (keep)
    extra_anonymization_rules[(0x0008, 0x103E)] = keep

    # Get all patient directories
    all_patients = [d for d in os.listdir(input_dicom_path) 
                   if os.path.isdir(os.path.join(input_dicom_path, d))]
    
    # Process each patient directory
    for i, patient in enumerate(original_tqdm(all_patients, desc="Patients")):
        # Create anonymized patient folder name
        anon_patient_name = f"pat{i+1:07d}"
        patient_path = os.path.join(input_dicom_path, patient)
        output_patient_path = os.path.join(output_dicom_path, anon_patient_name)
        
        all_studies = [d for d in os.listdir(patient_path) 
                      if os.path.isdir(os.path.join(patient_path, d))]
        
        # Process each study directory
        for study in all_studies:
            study_path = os.path.join(patient_path, study)
            output_study_path = os.path.join(output_patient_path, study)
            
            all_series = [d for d in os.listdir(study_path) 
                         if os.path.isdir(os.path.join(study_path, d))]
            
            # Process each series directory
            for series in all_series:
                series_path = os.path.join(study_path, series)
                output_series_path = os.path.join(output_study_path, series)
                
                # Create the series directory in output
                if not os.path.exists(output_series_path):
                    os.makedirs(output_series_path)
                
                anonymize(
                    series_path,
                    output_series_path,
                    extra_anonymization_rules,
                    delete_private_tags=True,
                )

if __name__ == "__main__":
    main()