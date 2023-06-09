import os
import sys
import CONSTANTS
from isc_parser import Parser
parser = Parser(lang='hin')
from wxconv import WXC

verb_lst = ['bol', 'kah', 'pUC']
we_lst = ['wA', 'wI', 'we']
hue_lst = ['huA', 'huI', 'hue']
def log(mssg, logtype='OK'):
    '''Generates log message in predefined format.'''

    # Format for log message
    print(f'[{logtype}] : {mssg}')
    if logtype == 'ERROR':
        sys.exit()

def get_dependency_by_index(output, index):
    dep = ''
    for row in output:
        if len(row) == 10 and row[0] == index :
            dep =  row[7]
            break
    return dep

def get_term_by_index(output, index):
    term = ''
    for row in output:
        if len(row) == 10 and row[0] == index:
            term = row[1]
            break
    return term

def check_term_ending_with(term, end_term):
    for ele in end_term:
        if term.endswith(ele):
            return True
    return False

def get_tag_by_index(output, index):
    tag = ''
    for row in output:
        if len(row) == 10 and row[0] == index:
            tag = row[3]
            break
    return tag

def get_pointing_index(output, index):
    ptr_index = -1
    for row in output:
        if len(row) == 10 and row[0] == index:
            ptr_index = row[6]
            break
    return ptr_index

def process_relation(output):
    dependency_mapper = {
        "r6-k1": "k1",
        "r6-k2": "k2",
        "r6v": "rhh",
        "k1inv": "rvks",
        "k2inv": "rbks",
        "adv": "krvn",
        "rs": "re",
        "jjmod": "intf",
        "jjmod__intf": "intf",
        "nmod_k1inv": "rvks",
        "nmod__k2inv": "rbks",
        "nmod__adj+JJ": "mod",
        "mod+JJ": "mod",
        "nmod__adj +QC": "card",
        "nmod__adj+DEM": "dem"
    }

    #to fetch necessary rule info in first iteration
    words = []
    verbs = []
    k2exists = False
    k2gexists = False
    k4exists = False
    k5exists = False
    CC_exists = False
    head_verb_exists = False
    VM_1_exists = False
    VM_2_exists = False

    for row in output:
        if len(row) > 0:
            if row[7] == 'k2':
                k2exists = True
                k2_head_verb_index = row[6]
                k2_index = row[0]
            elif row[7] == 'k2g':
                k2gexists = True
                k2g_head_verb_index = row[6]
                k2g_index = row[0]
            elif row[7] == 'main':
                head_verb_exists = True
                head_verb_index = row[0]
            elif row[7] == 'k4':
                k4exists = True
                k4_index = row[0]
            elif row[7] == 'k5':
                k5exists = True
                k5_index = row[0]

            if row[3] == 'CC':
                CC_exists = True
                CC_index = row[0]
            elif row[3] == 'VM' and not VM_1_exists:
                VM_1_exists = True
                VM_1_index = row[0]
            elif row[3] == 'VM' and VM_1_exists and not VM_2_exists:
                VM_2_exists = True
                VM_2_index = row[0]

    #For CC and 2 VM processing
    if CC_exists and VM_1_exists and VM_2_exists:
        CC_term = output[CC_index - 1]
        VM_1_term = output[VM_1_index - 1]
        VM_2_term = output[VM_2_index - 1]
        CC_term_head = CC_term[6]
        head_VM = []
        child_VM = []
        if CC_term_head == VM_1_index:
            head_VM = VM_1_term
            child_VM = VM_2_term
        elif CC_term_head == VM_2_index:
            head_VM = VM_2_term
            child_VM = VM_1_term

        head_VM_index = head_VM[0]
        child_VM[6] = head_VM_index
        up_dep = 'vk2'
        child_VM[7] = up_dep

    #Swap k2 and k2g if both point to same head verb
    if k2exists and k2gexists:
        if k2_head_verb_index == k2g_head_verb_index and k2_head_verb_index == head_verb_index:
            up_dep = 'k2g'
            output[k2_index-1][7] = up_dep
            up_dep = 'k2'
            output[k2g_index-1][7] = up_dep

    #Change k4, k5 to k2g when the list of verbs- bol, kah, puC
    if head_verb_exists:
        main_verb = output[head_verb_index-1][1]
        for verb in verb_lst:
            if verb in main_verb:
                up_dep = 'k2g'
                if k4exists:
                    output[k4_index-1][7] = up_dep
                if k5exists:
                    output[k5_index - 1][7] = up_dep

    #For direct dependency mapping
    for row in output:
        if len(row) > 0:
            dep_reln = row[7]
            index = row[0]
            if dep_reln in dependency_mapper:
                up_dep = dependency_mapper[dep_reln]
                row[7] = up_dep
            elif dep_reln.startswith('k') and dep_reln.endswith('u'):
                next_word = get_term_by_index(output, index+1)
                if next_word in ('jEsA', 'jEse', 'jEsI'):
                    up_dep = 'ru'
                    row[7] = up_dep
                else:
                    up_dep = 'rv'
                    row[7] = up_dep

    #For vmod processing
    for row in output:
        if len(row) > 0:
            index = row[0]
            if row[3] == 'VM':
                dependency = get_dependency_by_index(output, index)
                next_term_index = index + 1
                next_term_tag = get_tag_by_index(output, next_term_index)
                next_term = get_term_by_index(output, next_term_index)
                next_term_pointing_index = get_pointing_index(output, next_term_index)
                if dependency == 'vmod':
                    term = get_term_by_index(output, index)
                    if term.endswith('kara'):
                        up_dep = 'rpk'
                        row[7] = up_dep
                    elif check_term_ending_with(term, we_lst):
                        if next_term_tag == 'VAUX' and next_term_pointing_index == index:
                            if check_term_ending_with(next_term, hue_lst):
                                up_dep = 'rsk'
                                row[7] = up_dep
                    elif next_term_tag == 'VAUX' and next_term_pointing_index == index:
                        if next_term.endswith('kara'):
                            up_dep = 'rpk'
                            row[7] = up_dep
                elif dependency == 'k7':
                    term = get_term_by_index(output, index)
                    if term.endswith('ne'):
                        if next_term_tag == 'PSP' and next_term_pointing_index == index:
                            if next_term.endswith('para'):
                                up_dep = 'rblpk'
                                row[7] = up_dep
                #elif dependency == 'k7t':

    #For CC and ccof processing
    if CC_exists:
        CC_dep = output[CC_index - 1][7]
        for row in output:
            row_ptr_index = row[6]
            row_dep = row[7]
            if row_ptr_index == CC_index and row_dep in ('ccof', 'CCOF'):
                up_dep = CC_dep
                row[7] = up_dep

    return output

def format_data(row):
    if len(row) == 0:
        return []
    hindi_format = WXC(order="utf2wx", lang="hin")
    index = int(row[0])  if row[0] != '' else log('Value in the index col is missing')
    wx_token = hindi_format.convert(row[1]) if row[1] != '' else log('Value int the token col is missing')
    token = row[2]
    category = row[3]
    category_1 = row[4]
    col6 = row[5]
    related_to = int(row[6]) if row[6] != '' else log('Value in the related_to col is missing')
    relation = row[7]
    col9 = row[8]
    col10 = row[9]

    formatted_row = [index, wx_token, token, category, category_1, col6, related_to, relation, col9, col10]
    return formatted_row

def read_input_file(file_name):
    hindi_format = WXC(order="wx2utf", lang="hin")
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            file_rows = ''
            for i in range(len(lines)):
                lineContent = lines[i]
                if lineContent.strip() == '':
                    continue
                else:
                    file_rows = hindi_format.convert(lineContent)

            log('File data read.')
    except FileNotFoundError:
        log('No such File found.', 'ERROR')
        sys.exit()
    return file_rows

def generate_parse_data(parser_output_line):
    """
    >>> generate_parse_data("1	यदि	यदि	CC	CC	_	15	vmod	_	_")
    ['1', 'यदि', 'यदि', 'CC', 'CC', '_', '15', 'vmod', '_', '_']
    """
    output = parser_output_line.strip().split()
    return output

def parse_file(parser_output):
    '''
    :param parser_output:
    :return:
    '''
    parsed_output = list(map(lambda x: generate_parse_data(x), parser_output))
    format_output = list(map(lambda x: format_data(x), parsed_output))
    processed_relation = process_relation(format_output)
    return processed_relation

def clean_input_file(input):
    data = read_input_file(input)
    return data

def get_parser_output(input, output):
    data = clean_input_file(input)
    os.system("isc-parser -i " + input + " -o " + output)

def add_wx_conv_col(data):
    hindi_format = WXC(order="utf2wx", lang="hin")
    i = len(data)
    while i > 0:
        i = i - 1
        info = data[i].strip().split("\t")
        wx_form = hindi_format.convert(info[1])
        info[1] = wx_form
        data[i] = '\t'.join(info)
    return data

def read_output_file(file_name):
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            file_rows = []
            for i in range(len(lines)):
                lineContent = lines[i]
                if lineContent.strip() == '':
                    continue
                else:
                    file_rows.append(lineContent)

            log('Parser output file read.')
    except FileNotFoundError:
        log('No output file found.', 'ERROR')
        sys.exit()
    return file_rows

def write_file(data, OUTPUT_FILE):
    with open(OUTPUT_FILE, 'w') as file:
        for row in data:
            file.write(row)
            file.write('\n')
        log('Parser output file write successful')

if __name__ == "__main__":

    get_parser_output(CONSTANTS.INPUT_FILE, CONSTANTS.PARSER_OUTPUT_FILE)
    data = read_output_file(CONSTANTS.PARSER_OUTPUT_FILE)
    output = parse_file(data)
    final_output = []
    for inner_list in output:
        inner_list = [str(ele) for ele in inner_list]
        final_output.append('\t'.join(inner_list))
    write_file(final_output, CONSTANTS.PROCESSED_PARSER_OUTPUT_FILE)