from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# make sure upload/prcoessed directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# code to reformat memory dump for logism
def reformat_logisim(hex_codes):
    '''
    takes list of mips code from mars memory dump export and reformats 
    hex code instructions into 4 bit incremented addresses for logisim.

    hex_codes == list of mips code instructions (must be in 32 bit hex strings)
    return == reformatted .txt output with correct addresses
    '''
    format_instructions = []
    address = 0 # starting address

    for code in hex_codes:
        code = code.zfill(8) #double checking code is actually 32 bits, pad w/ 0's if not
        
        # splitting code into every 2 bytes and reversing order
        reordered_code = f"{code[6:8]} {code[4:6]} {code[2:4]} {code[0:2]}"

        # adding register addresses in front of reordered code and add to list
        format_instructions.append(f"{address:04X}: {reordered_code}")
        address += 4 # increment address by 4

    return format_instructions

def read_mem_dump(file_name):
    '''
    reads the memory dump file to use in our reformat_logisim function

    file_name == name of the memory dump file
    return == list of hex instruction strings
    '''
    with open(file_name, 'r') as file:
        # read every line and then strip the whitespace and ignore any potential empty lines
        hex_codes = [line.strip() for line in file if line.strip()]
    return hex_codes

def write_txt(file_name, format_instructions):
    '''
    writes the now formatted instruction into a txt file to use in logism rom

    file_name == name of the output txt file
    format_instructions == the reformatted instruction with addresses
    '''
    with open(file_name, 'w') as file:
        for instruction in format_instructions:
            file.write(instruction + '\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # handle file upload
    if 'file' not in request.files:
        return "No file in request", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)

    # read/format memory dump file
    hex_codes = read_mem_dump(file_path)
    format_instructions = reformat_logisim(hex_codes)

    # write reformatted instruction to new txt file
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'logism_rom.txt')
    write_txt(output_path, format_instructions)

    # generate download file
    return send_file(output_path, as_attachment=True, download_name='logism_rom.txt')

if __name__ == '__main__':
    app.run(debug=True)