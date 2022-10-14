
# Pacakges for finding date 
import re
import sys

# Packages for text matching (Name and Location)
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree


'''

Instructions to run code:

1) Run: python deid-YUFUNGDAVIDWANG.py id.text YUFUNGDAVIDWANG.phi

2) Will be prompted with some inputs in terminal
    - I implemented 2 functions, one to find DATES and one to find NAMES
    - Main function is DATES (grade on this) as it produces good results ... NAMES is just to show a attempt with NLTK as it has bad results
        - If testing NAMES, will be prompted with another GPE or PERSONS where GPE will find locations and PERSONS will find HCPNames and PTNames
        - Note that NAMES function has considerable overhead, so will take a minute to run
        
3) Run: python stats.py id.deid id-phi.phrase YUFUNGDAVIDWANG.phi 
    - To see results

'''


date_pattern = r'\d{2}/\d{2}|\d{2}/\d{1}|\d{1}/\d{2}|\d{1}/\d{1}|\d{1}/\d{2}/\d{4}|\d{2}/\d{1}/\d{4}|\d{1}/\d{1}/\d{4}|\d{1}/\d{2}/\d{2}|\d{2}/\d{1}/\d{2}|\d{1}/\d{1}/\d{2}'
date_reg = re.compile(date_pattern)

def check_for_date(patient,note,chunk, output_handle):
    ''' 
        Explanation of Below Code:
            Code that works well to find date using the re package as seen in finding phone numbers. The process was to change the regex pattern to match that of dates which I noticed
            can be in the forms... xx/xx, x/x, xx/x, x/xx, x/xx/xxxx, xx/x/xxxx, x/x/xxxx, x/xx/xx, xx/x/xx, x/x/xx.
            By doing so, Date category produced a senstivity/recall of 0.878 and a ppv/specificity value of 0.631.

        Inputs:
            - patient: Patient Number, will be printed in each occurance of personal information found
            - note: Note Number, will be printed in each occurance of personal information found
            - chunk: one whole record of a patient
            - output_handle: an opened file handle. The results will be written to this file.
                to avoid the time intensive operation of opening and closing the file multiple times
                during the de-identification process, the file is opened beforehand and the handle is passed
                to this function. 
        Logic:
            Search the entire chunk for the occurances of date in forms of xx/xx, x/x, xx/x, x/xx, x/xx/xxxx, xx/x/xxxx, x/x/xxxx, x/xx/xx, xx/x/xx, x/x/xx
            Find the location of these occurances relative to the start of the chunk, and output these to the output_handle file. 
            If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
            Using regex compile expression to find the dates.

    '''

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found

    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in date_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')




def check_for_text(patient,note,chunk, output_handle, text_label):

    ''' 
        Explanation of Below Code:
            Scratched out code for finding location and name, scratched out because of terrible results (as we are graded for results) for matching text with NLTK. NLTK can tag names (PERSON), location (GPE), etc.
            Cannot identify between PTName, HCPName, PTNameInitials, Other, Location, and RelativeProxyName. Sensitivity and recall was 0.054 and specificity was 0.357 for location (GPE).
            Sensivity and recall was 0.02 and specificity was 0.697 for HCPName and sensitvity and recall was 0.111 and specificity was 0.698 for PTName.
            However, wanted to show work done and attempted for the function. Can give argument in input to RUN. Note that runtime may take up to a minute.

        Inputs:
            - patient: Patient Number, will be printed in each occurance of personal information found
            - note: Note Number, will be printed in each occurance of personal information found
            - chunk: one whole record of a patient
            - output_handle: an opened file handle. The results will be written to this file.
                to avoid the time intensive operation of opening and closing the file multiple times
                during the de-identification process, the file is opened beforehand and the handle is passed
                to this function. 
        Logic:
            Search the entire chunk for the occurances of either location or name. Find the location of these occurances 
            relative to the start of the chunk, and output these to the output_handle file. 
            If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
            Using NLTK to compile trees of tags to be parsed where subtrees will be combined to form the words.

    '''

    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
    nltk_chunk = ne_chunk(pos_tag(word_tokenize(chunk)))
        
    for subtree in nltk_chunk:

        if type(subtree) == Tree and subtree.label() == text_label.upper(): # == 'PERSON':        ## GPE is NLTK tag for location or PERSON for name
            text = ''

            for leaf in subtree.leaves():
                text += leaf[0] + ' '
            
            if text in chunk:
                start_i = chunk.index(text) - 27
                end_i = start_i + len(text) - 27

                print(patient, note,end=' ')
                print(start_i, end_i, text)

                result = str(start_i) + ' ' + str(start_i) + ' ' + str(end_i)

                output_handle.write(result + '\n')

                
            
            
def deid(text_path= 'id.text', output_path = 'YUFUNGDAVIDWANG.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each match found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no match detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each match detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end match
        where `start` is the start position of the detected string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # input arguments to switch between the two functions I wrote
    print("DATE: Date (More Accurate)        NAME: Location/HCPName/PTName (Not Accurate)")
    dateorname = input("Input DATE or NAME:   ")
    # if input was for name (check_for_text function), then further argument to read locations or human names
    if dateorname.upper() == "NAME":
        print("GPE: Location       PERSON: Name")
        text_label = input("Input GPE or PERSON:   ")

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number

                    # run date or name function
                    if dateorname.upper() == "DATE":
                        check_for_date(patient,note,chunk.strip(), output_file)     
                    else:
                        check_for_text(patient,note,chunk.strip(), output_file, text_label)     

                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    deid(sys.argv[1], sys.argv[2])
    