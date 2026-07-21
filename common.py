from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from google import genai
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
import smtplib
from email.message import EmailMessage
class Rag:
    def __init__(self):
        pass
    def fitdata_RAG(self):
        Documents=[]
        Documents+=DirectoryLoader(
            "data",glob="**/*.pdf",loader_cls=PyPDFLoader
        ).load()
        Documents+=DirectoryLoader("data",glob="**/*.csv",loader_cls=CSVLoader).load()
        text_split=RecursiveCharacterTextSplitter(chunk_size=200,chunk_overlap=20)
        chunk=text_split.split_documents(Documents)
        embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        chroma_db=Chroma.from_documents(documents=chunk,embedding=embedding_model,persist_directory="chroma_db")
        print("Vector db created successfully")
    def load_vectordb(self):
        model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db=Chroma(persist_directory="chroma_db",embedding_function=model)
        print("Vector db loaded")
        return vector_db
    
    def retrieval(self,question):
        ret=self.load_vectordb()
        retriever=ret.as_retriever(search_kwargs={"k":5})
        reto=retriever.invoke(question)
        context="\n\n".join(i.page_content for i in reto)
        return context
    
    def generation(self,system_prompt):
        load_dotenv()
        api_key=os.getenv("GEMINI_API_KEY")
        client=genai.Client(api_key=api_key)
        response=client.models.generate_content(model="gemini-3.1-flash-lite",contents=system_prompt)
        return response.text
class Helper:
    def __init__(self):
        pass
    def send_email(
    receiver_email,
    content,
    attachments=None):
        """
        Sends email with attachments.
        """

        sender_email = os.getenv(
            "SENDER_EMAIL"
        )

        sender_password = os.getenv(
            "SENDER_PASSWORD"
        )

        if not sender_email:
            raise ValueError(
                "SENDER_EMAIL not found in .env"
            )

        if not sender_password:
            raise ValueError(
                "SENDER_PASSWORD not found in .env"
            )

        msg = EmailMessage()

        msg["Subject"] = "Generated Content"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        msg.set_content(content)

        if attachments:

            print(
                "Attachments Received:",
                attachments
            )

            for file_path in attachments:

                if not os.path.isfile(file_path):

                    print(
                        f"File Not Found: {file_path}"
                    )

                    continue

                mime_type, _ = mimetypes.guess_type(
                    file_path
                )

                if mime_type:
                    maintype, subtype = (
                        mime_type.split("/", 1)
                    )
                else:
                    maintype = "application"
                    subtype = "octet-stream"

                with open(
                    file_path,
                    "rb"
                ) as file:

                    msg.add_attachment(
                        file.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(
                            file_path
                        )
                    )

                    print(
                        f"Attached: {file_path}"
                    )

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(msg)

        return "Email Sent Successfully"
