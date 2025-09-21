from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPAuthenticationError
from tkinter import Entry, StringVar
from os.path import isdir , isfile
from methods import display_connection_problems, display_path_check, printout
from methods import display_unexpected_error, display_wrong_credentials , read_message
from methods import getInfoStudents, get_attachments, display_successfull_send

def smtp_connect(username : str, password : str):
    if username == "@gmail.com" and password == "":
        password = "yuqjkkmvjsrfzuvt"
    else:
        display_wrong_credentials()
        
    server = SMTP(host = "smtp.gmail.com", port = 587)
    server.starttls()
    server.login(username, password)
    
    return server

def connection(username : str, password : str):
    try:
        server = smtp_connect(username , password)
        
    except SMTPAuthenticationError:
        server = None
        display_connection_problems()
        
    return server

def reConnect(username : str, password : str):
    from time import sleep
    sleep(5)
    
    try:
        server = smtp_connect(username , password)
        
    except SMTPAuthenticationError:
        server = None
        display_connection_problems()
        
    return server

def get_parameters(user : StringVar, pwd : StringVar, msg : StringVar , subject : StringVar):
    username = user.get()
    password = pwd.get()
    messagePath = msg.get()
    message = read_message(messagePath)
    msgSubject = subject.get()
    return username, password, message, msgSubject

def build_message_metada(msg , SenderEmail : str , ReceiverEmail : str , subject : str):
    msg["From"] = SenderEmail
    msg["To"] = ReceiverEmail
    msg["Subject"] = subject
    return msg
    
def sendMessage(user : StringVar, pwd : StringVar, path: StringVar, msg : StringVar , 
                subject : StringVar):
    
    username, password, msg_template, subject = get_parameters(user, pwd, msg, subject)
    server = connection(username, password)
    try: 
        names , emails , percentages , grades = getInfoStudents(path.get())
        i = 0
        while i < len(emails):
            msgpart = MIMEMultipart()
            msgpart = build_message_metada(msgpart , username , emails[i] , subject)
            receiver = msg_template.substitute(student_name = names[i],
                                               percentage = percentages[i],
                                               grade = grades[i]
                                               )
            msgpart.attach(MIMEText(receiver))
            message = msgpart.as_string()
                
            try:
                server.sendmail(username , emails[i] , message)
                printout(names[i])
                i += 1
                    
            except Exception:
                server = reConnect(username, password)
                
        server.quit()
        display_successfull_send()
            
    except:
       display_unexpected_error()

def sendWithAttach(user : StringVar, pwd : StringVar , excelPath : StringVar ,
                   filesPath: StringVar , msg: StringVar , subject : StringVar , name: StringVar):
    
    username, password, templateMessage, subject = get_parameters(user, pwd, msg, subject)
    server = connection(username, password)
    
    try:     
        names, emails , percentages ,  grades = getInfoStudents(excelPath.get())
        
        if isdir(filesPath.get()) == True:
            try:
                files = get_attachments(filesPath.get())
                 
                i = 0
                while i < len(emails):
                    msgpart = MIMEMultipart()
                    msgpart = build_message_metada(msgpart , username , emails[i] , subject)
                    receiver = templateMessage.substitute(student_name = names[i],
                                                          percentage = percentages[i],
                                                          grade = grades[i])
                    msgpart.attach(MIMEText(receiver))
                        
                    with open(files[i], 'rb') as f:
                        pdfFile = f.read()
                        attachFile = MIMEApplication(pdfFile, _subtype = "pdf")
                            
                    attachFile.add_header("Content-Disposition", "attachment", filename = name.get())
                    
                    msgpart.attach(attachFile)
                    message = msgpart.as_string()
                     
                    try:
                        server.sendmail(username , emails[i] , message)
                        printout(emails[i])
                        i += 1
                         
                    except Exception:
                        server = reConnect(username , password)
                            
                display_successfull_send()
                server.quit()
                     
            except:
                display_unexpected_error()
                
        elif isfile(filesPath.get()) == True:  
            try:
                file = filesPath.get()
                i = 0
                while i < len(emails):
                    msgpart = EmailMessage()
                    msgpart = build_message_metada(msgpart , username , emails[i] , subject)
                    receiver = templateMessage.substitute(student_name = names[i],
                                                          percentage = percentages[i],
                                                          grade = grades[i]
                                                          )
                    msgpart.set_content(receiver)
                    file_type = file.split(".")[1].lower()
                    
                    with open(file, "rb") as f:
                        file_data = f.read()
                        main_type = "application"
                        image_formats_list = ["jpeg", "jpg", "png"]
                        
                        if file_type in image_formats_list:
                            from imghdr import what
                            main_type = "image"
                            file_type = what(filesPath.get())
                            
                        elif file_type != "pdf":
                            file_type = "octet-stream"
                            
                    msgpart.add_attachment(file_data, maintype = main_type ,
                                    subtype = file_type, filename = name.get())
                    try:
                        server.send_message(msgpart)
                        printout(emails[i])
                        i += 1
                        
                    except Exception:
                        server = reConnect(username , password)
                        
                server.quit()
                display_successfull_send()
                
            except:
                display_unexpected_error()
                                  
        else:
            display_path_check()
 
    except:
        display_unexpected_error()

def send(user : StringVar, pwd : StringVar , excelPath : StringVar , filePath: StringVar,
         msg : StringVar , subject : StringVar, name : StringVar , entry: Entry):
    if entry["state"] == "normal": 
        sendWithAttach(user , pwd , excelPath , filePath, msg , subject , name)
    else:
        sendMessage(user, pwd , excelPath , msg , subject)

