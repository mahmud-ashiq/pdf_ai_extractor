"""
PDF Auditor Form Data Extractor
Extracts form data and embedded documents from PDF files and generates summaries using Google Gemini AI.
"""

import fitz  # PyMuPDF
import json
import os
import easyocr
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file, overriding existing ones
load_dotenv('.env', override=True)

def select_pdf_from_directory():
    # Get list of all files in current directory
    all_files = os.listdir('.')
    
    # Iterate through files to find the first PDF
    for file in all_files:
        if file.lower().endswith('.pdf'):
            return file
        else:
            continue
    
    # Exit if no PDF files found
    print("No PDF files found in the current directory.")
    exit()

def extract_form_data(pdf_path):   
    """Extracts form field data from PDF file and counts embedded documents."""
    doc = fitz.open(pdf_path)
    attachment_count = doc.embfile_count()
    form_data = {}
    
    for page in doc:
        for field in page.widgets():
            key = field.field_name
            val = field.field_value
            if key:
                form_data[key] = val
    
    return doc, form_data, attachment_count

def extract_embedded_documents(doc):
    """Extracts and performs OCR on embedded PDF documents within the main PDF."""
    reader = easyocr.Reader(['en'])
    all_doc = ""
    
    # Process each embedded document
    for i in range(doc.embfile_count()):
        try:
            # Get embedded document metadata and content
            name = doc.embfile_info(i)['filename']
            data = doc.embfile_get(i)  # bytes
            emb_doc = fitz.open(stream=data, filetype="pdf")
            single_doc = ""
            
            # Process each page of the embedded document
            for page in emb_doc:
                pix = page.get_pixmap(dpi=300)
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                results = reader.readtext(img_array)
        
                page_text = " ".join([text for (_, text, _) in results])
                page_text = page_text.replace("{", "").replace("}", "")
                single_doc += page_text + "\n"

            all_doc += f"Document name: {os.path.splitext(name)[0]}\n{single_doc}\n"
       
        except Exception as e:
            print(f"Error processing embedded document {i}: {e}")
            continue
    
    return all_doc

def structure_form_data(form_data):
    """Structure the extracted form data into a json format."""
    data = {
        "cin": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform1[0].CIN_C[0]', ''),
        "gln": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform1[0].GLN_C[0]', ''),
        "company_name": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform1[0].CompanyName_C[0]', ''),
        "registered_office": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform1[0].CompanyAdd_C[0]', '').replace('\r', ' '),
        "company_mail": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform1[0].EmailId_C[0]', ''),
        "appointment_type": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform2[0].DropDownList1[0]', ''),
        "appoitment_date": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform6[0].DateReceipt_D[0]', ''),
        "appointed_period": f"{form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].DateOfAccAuditedFrom_D[0]', '')} - "
                          f"{form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].DateOfAccAuditedTo_D[0]', '')}",
        "auditor_category": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].CategoryOfAuditor[0]', ''),
        "auditor_income_tax_account_number": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].PAN_C[0]', ''),
        "auditor_name": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].NameAuditorFirm_C[0]', ''),
        "auditor_membership_number": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].MemberShNum[0]', ''),
        "auditor_address": (
            f"{form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].permaddress2a_C[0]', '')}, "
            f"{form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].permaddress2b_C[0]', '')}, "
            f"City: {form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].City_C[0]', '')}, "
            f"State: {form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].State_P[0]', '')}, "
            f"Country: {form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].Country_C[0]', '')}, "
            f"PIN: {form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].Pin_C[0]', '')}"
        ),
        "auditor_mail": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].email[0]', ''),
        "financial_year": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform3[0].Subform_4aTo4h[0].NumOfFinanYear[0]', ''),
        "resolution_number": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform6[0].ResoNum[0]', ''),
        "declaration_date": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform6[0].DateOfAppSect_D[0]', ''),
        "signed_by_designation": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform6[0].DesigD_C[0]', ''),
        "DIN": form_data.get('data[0].FormADT1_Dtls[0].Page1[0].Subform6[0].DINOfDir_C[0]', '')
    }
    return data

def generate_summaries(data, gemini_api_key):
    """Generate summaries using Google Gemini AI."""
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_api_key,
        temperature=0.3,
        max_output_tokens=512,
    )
    
    # Summary template for main form data
    summary_template = f"""
            Write a professional 2–3 sentence summary of an auditor appointment using the following data:
            Company Name: {data['company_name']}  
            Auditor Name: {data['auditor_name']}  
            Period: {data['appointed_period']}  
            Effective From: {data['appoitment_date']}  

            output Example: "XYZ Pvt Ltd has appointed M/s Rao & Associates as its statutory auditor for FY 2023–24, effective from 1 July 2023. 
            The appointment has been disclosed via Form ADT-1, with all supporting documents submitted."

            Summary:
            """
    
    # Create prompt templates
    summary_prompt = PromptTemplate(
        input_variables=["company_name", "auditor_name", "appointed_period", "appoitment_date"],
        template=summary_template
    )
        
    # Generate summaries
    pipe = summary_prompt | llm
    summary = pipe.invoke(data)
    
    return summary

def generate_attachment_summaries(all_doc, gemini_api_key):
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_api_key,
        temperature=0.3,
        max_output_tokens=512,
    )

    # Summary template for attachments
    attachment_summary_template = f"""
        You are given several documents related to an auditor appointment.
        {all_doc}
        For each document provide a concise summary in 1-2 sentences.

        Summary:
        """
    
    # Create prompt templates
    attachment_summary_prompt = PromptTemplate(
        input_variables=["all_doc"],
        template=attachment_summary_template
    )

    # Generate summaries  
    pipe = attachment_summary_prompt | llm
    attachment_summary = pipe.invoke({"all_doc": all_doc})

    return attachment_summary

def save_outputs(data, summary, attachment_summary):
    """Save extracted data and summaries to files."""
    # Save structured data as JSON
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
    
    # Save summaries to text file 
    if attachment_summary != "":
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write("Summary\n\n")
            f.writelines(summary.content)
            f.writelines("\n\n\nSummary of the attachments\n\n")
            f.writelines(attachment_summary.content)
    
    else:
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write("Summary\n\n")
            f.writelines(summary.content)
    
    print("Files saved:")
    print("- data.json: Structured form data")
    print("- summary.txt: Generated summaries")

def main():
    """Main function to process PDF and generate summaries."""
    # Configuration
    PDF = select_pdf_from_directory()
    
    try:
        print("Starting PDF processing...")
        
        # Extract form data
        print("Extracting form data...")
        doc, form_data, attachment_count = extract_form_data(PDF)

        # Structure the data
        print("Structuring data...")
        data = structure_form_data(form_data)

        # Generate summaries
        print("Generating summaries with AI...")
        summary = generate_summaries(data, os.getenv('GEMINI_API_KEY'))
        
        attachment_summary =""
        # Checking for embedded documents
        if attachment_count != 0:
            print("Attatchment found\n")
            # Extract embedded documents
            print("Extracting attachment documents...")
            all_doc = extract_embedded_documents(doc)

            # Generate summaries
            print("Generating summaries with AI...")
            attachment_summary = generate_attachment_summaries(all_doc, os.getenv('GEMINI_API_KEY'))
        
        # Save outputs
        print("Saving outputs...")
        save_outputs(data, summary, attachment_summary)
        
        print("Processing completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
