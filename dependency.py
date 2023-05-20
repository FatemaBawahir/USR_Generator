import os
import sys
from isc_parser import Parser
parser = Parser(lang='hin')
from wxconv import WXC

def log(mssg, logtype='OK'):
    '''Generates log message in predefined format.'''

    # Format for log message
    print(f'[{logtype}] : {mssg}')
    if logtype == 'ERROR':
        sys.exit()

def process_relation(output):
    dependency_mapper = {
        "r6-k1": "k1",
        "r6-k2": "k2",
        "r6v": "rhh",
        "k1inv": "rvks",
        "k2inv": "rbks",
        "adv": "krvn",
        "rs": "re",
        "jjmod": "intf"
    }

    #to fetch necessary rule info in first iteration
    words = []
    verbs = []
    k2exists = False
    k2gexists = False

    for row in output:
        if len(row) > 0:
            if row[7] == 'k2':
                k2exists = True
                k2_head_verb_index = row[6]
                k2_index = row[0]
            if row[7] == 'k2g':
                k2gexists = True
                k2g_head_verb_index = row[6]
                k2g_index = row[0]
            if row[7] == 'main':
                head_verb_index = row[0]

    #Swap k2 and k2g if both point to same head verb
    if k2exists and k2gexists:
        if k2_head_verb_index == k2g_head_verb_index and k2_head_verb_index == head_verb_index :
            up_dep = 'k2g'
            output[k2_index-1][7] = up_dep
            up_dep = 'k2'
            output[k2g_index-1][7] = up_dep

    #For direct dependency mapping
    for row in output:
        if len(row) > 0:
            dep_reln = row[7]
            if dep_reln in dependency_mapper:
                up_dep = dependency_mapper[dep_reln]
                row[7] = up_dep

    return output

def format_data(row):
    if len(row) == 0:
        return []
    hindi_format = WXC(order="utf2wx", lang="hin")
    index = int(row[0])  if row[0] != '' else log('Value in the index col is missing')
    token = row[1]
    wx_token = hindi_format.convert(row[2]) if row[2] != '' else log('Value int the token col is missing')
    category = row[3]
    category_1 = row[4]
    col6 = row[5]
    related_to = int(row[6]) if row[6] != '' else log('Value in the related_to col is missing')
    relation = row[7]
    col9 = row[8]
    col10 = row[9]

    formatted_row = [index, token, wx_token, category, category_1, col6, related_to, relation, col9, col10]
    return formatted_row

def read_file(file_name):

    open(file_name).readlines()

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
    data = read_file(input)
    data = data.strip()
    hindi_format = WXC(order="wx2utf", lang="hin")
    hindi_input = hindi_format.convert(data)

def get_parser_output():
    input_file = "/Users/fatema/Desktop/workspace/LanguageCommunicator/AutomaticUSRGenerator/input.txt"
    clean_input_file(input_file)
    os.system("isc-parser -i input.txt -o output.txt")

if __name__ == "__main__":
    get_parser_output()
    # hindi_format = WXC(order="wx2utf", lang="hin")
    # generate_hindi_text = hindi_format.convert('mohana laMgadAkara calawA hE')
    # print(generate_hindi_text)
    # with open('out.txt', 'w') as file:
    #     file.write(generate_hindi_text)
    data = read_file("output.txt")
    out = parse_file(data)
    for row in out:
        with open("parser_output.txt", 'w') as file:
            file.write(str(out))
            file.write("\n")
