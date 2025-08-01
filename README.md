About the Project:

This project is called the "Book of Knowledge" and the objective is to take company project files that have "meeting notes" (which are in pdf format) and extract them so that we can add it to a central repository and be able to query it for the engineers. 

These meeting notes contain important data about the project: Materials used, calculations used, loads used, etc.

The Big reason for this is that engineers want to be able to use previously used project information when working on new projects.

Another reason would be that it will help the younger engineers who may not be too sure on what to do or dont want to start from scratch.

So its crucial that this project has an efficent and accurate process to parse meeting notes out of the project file. Luckily these meeting notes can be anywhere from 1-5 pages so its not to big in scale.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Main Dependencies(Poppler):

In this section I will go over the main and more complicated dependencies needed to run the code. These dependencies are needed to run the OCR extractor. When done with "Main Dependencies(Poppler)" move on to "Main Dependencies(pytesseract)"

First in the terminal: "pip install pdf2image" after this is done go to step 1

Step 1.) To use the OCR extractor first you need Poppler. Here is the link to the site where you download it (Make sure to only download "Release-24.08.0-0.zip"): https://github.com/oschwartz10612/poppler-windows/releases/tag/v24.08.0-0

Step 2.) Once Poppler is installed extract the zip and put the poppler file in your program files

Step 3.) Open your "control pannel" then select system security

Step 4.) Now select system then advanced system settings 

Step 5.) Then select Enviorment Variables 

Step 6.) In the user variables section select path and make sure its highlighted then select edit

Step 7.) Now select new and then browse 

Step 8.) Finally choose the file path of where poppler is located and then select ok. The file path should look exactly like this for the most part: "c:\Program Files\poppler-24.08.0\library\bin"

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Main Dependencies(pytesseract):

This is part 2 to the Main Dependencies section.

First in the terminal: "pip install pytesseract" after this is done go to step 1

Step 1.) To use the OCR extractor second you need pytesseract. Here is the link to the site where you download it (Make sure to download "tesseract-ocr-w64-setup-5.5.0.20241111.exe (64 bit)": https://github.com/UB-Mannheim/tesseract/wiki

Step 2.) Now before going to the exe and fully installing on your computer make a new folder in program files called "Tesseract-OCR".

Step 3.) Then go to the exe installer and fully install Tesseract on your computer and make sure the file path looks like this "C:\\Program Files\\Tesseract-OCR"

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Small Dependencies:

In this section it will show the different small dependencies needed to run the code and the method to install them.

0.) All dependencies: pip install -r requirements.txt

1.) pandas: pip install pandas

2.) numpy: pip install numpy

3.) pdfplumber: pip install pdfplumber

4.) PyMuPdf(fitz): pip install pymupdf

5.) cv2: pip install opencv-python

6.) openyxl: pip install openpyxl

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Very Important Info:

1.) PyTesseract- 
Make sure this is what the configuration in the code looks like: TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe". This is where your tesseract path is located and the code pulls from when running through the configuration.

2.) input_folder- 
Make sure your input_folder (located in the mainextractor.py and MAIN EXECUTION section of the code) equals where your directory is holding the folder that has the pdf meeting notes in them. Example: input_folder = r"C:\\insert\\insert\\insert\\folder insert"

3.) MultiProcessing- 
When it comes to Multiprocessing it's all based on how many cpu cores your computer has. If you have 8 cpu cores that means you can run 8 processes and if you have 12 then you can run 12 processes. To put it simply if you have 8 processes that means you can extract 8 pdfs at once which drastically speeds up how long it takes to extract info from a folder full of pdfs. So before running the code make sure to chech how many cpu cores your pc has and adjust the number here in the code: "with Pool(processes=min(8, cpu_count())) as pool". This is also located in the MAIN EXECUTOIN section. Finally it is recommended to not go over your cpu core count it will slow down the time or crash the system altogether.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Happy Extracting!!!
