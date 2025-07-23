About the Project:

This project is called the "Book of Knowledge" and the objective is to take company project files that have "meeting notes" (which are in pdf format) and extract them so that we can add it to a central repository and be able to query it for the engineers. 

These meeting notes contain important data about the project: Materials used, calculations used, loads used, etc.

The Big reason for this is that engineers want to be able to use previously used project information when working on new projects.

Another reason would be that it will help the younger engineers who may not be too sure on what to do or dont want to start from scratch.

So its crucial that this project has an efficent and accurate process to parse meeting notes out of the project file. Luckily these meeting notes can be anywhere from 1-5 pages so its not to big in scale.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Main Dependencies:

In this section I will go over the main more complicated dependencie needed to run the code. This dependencie is needed to run the OCR extractor.

1.) pdf2image: pip install pdf2image

2.) pytesseract: pip install pytesseract

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Small Dependencies:

In this section I will go over the different small dependencies needed to run the code.

0.) To download all dependencies use: pip install -r requirements.txt

1.) pandas: pip install pandas

2.) numpy: pip install numpy

3.) pdfplumber: pip install pdfplumber

4.) PyMuPdf(fitz): pip install pymupdf

5.) cv2: pip install opencv-python

6.) openyxl: pip install openpyxl


