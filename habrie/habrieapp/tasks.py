import csv
from loguru import logger
import pandas as pd
from celery import shared_task
from django.http import HttpResponse
from .models import AcademicDetail, Document, Parent, Student, Csv
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError



@shared_task
def csv_upload():
    try:
        obj = Csv.objects.get(activated=False)

        required_fields = [
            'name', 'gender', 'aadhar', 'dob', 'id_mark', 'admission_cat', 'height', 'weight', 'mail', 'contact', 'address', 'father_name', 'father_qualification', 'father_profession', 'father_designation', 'father_aadhar', 'father_number', 'father_mail', 'mother_name', 'mother_qualification', 'mother_profession', 'mother_designation', 'mother_aadhar', 'mother_number', 'mother_mail', 'enroll_id', 'class_id', 'section_id', 'doj', 'document', 'session'
        ]

        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)  # This reads and stores the header row.

            if not all(field in headers for field in required_fields):
                raise ValidationError("CSV file does not contain all the required fields.")

            for row in reader:  # This will now start from the first row of data.
                academic_data = {
                    'enroll_id': row[25],
                    'class_id': row[26],
                    'section_id': row[27],
                    'doj': row[28],
                    'session': row[30]
                }

                if not all(value == '' for value in academic_data.values()):
                    academic_detail, _ = AcademicDetail.objects.update_or_create(
                        enroll_id=row[25],
                        defaults=academic_data,
                        session=row[30]
                    )
                
                academic_detail = AcademicDetail.objects.get(enroll_id=row[25])
                student_data = {
                    'name': row[0],
                    'gender': row[1],
                    'aadhar': row[2],
                    'dob': row[3],
                    'id_mark': row[4],
                    'admission_cat': row[5],  # Corrected 'addmission_cat' to 'admission_cat'
                    'height': row[6],
                    'weight': row[7],
                    'mail': row[8],
                    'contact': row[9],
                    'address': row[10],
                    'enroll_number': academic_detail,
                }
                student, _ = Student.objects.update_or_create(name=row[0], defaults=student_data)

                parent_data = {
                    'student_name': student,
                    'father_name': row[11],
                    'father_qualification': row[12],
                    'father_profession': row[13],
                    'father_designation': row[14],
                    'father_aadhar': row[15],
                    'father_number': row[16],
                    'father_mail': row[17],
                    'mother_name': row[18],
                    'mother_qualification': row[19],
                    'mother_profession': row[20],
                    'mother_designation': row[21],
                    'mother_aadhar': row[22],
                    'mother_number': row[23],
                    'mother_mail': row[24],
                }
                Parent.objects.update_or_create(student_name=student, defaults=parent_data)

                document_data = {
                    'student_name': student,
                }
                Document.objects.update_or_create(student_name=student, defaults=document_data)
                
            obj.activated = True
            obj.save()
            logger.info(f"Task Result: {obj}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
    return "DONE"



@shared_task
def send_templated_email(recipient_email, recipient_name, enroll_no, class_id, section, session):
    try:
        subject = 'Templated Email'
        from_email = 'nitin.ekka30@gmail.com'
        to = ['nitin.ekka30@gmail.com']
    
        student_email_content = render_to_string('student_mail.html', {'recipient_name': recipient_name, 'enroll_no': enroll_no, 'class_id': class_id, 'section': section, 'session': session})
        admin_email_content = render_to_string('admin_mail.html', {'recipient_name': recipient_name, 'enroll_no': enroll_no, 'class_id': class_id, 'section': section, 'session': session})
        email_student = EmailMessage(subject, student_email_content, from_email, to)
        email_student.content_subtype = 'html'
        email_student.send()

        email_admin = EmailMessage(subject, admin_email_content, from_email, to)
        email_admin.content_subtype = 'html'
        email_admin.send()
        logger.info(f"Task result: {student_email_content}, {admin_email_content}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
    
    
