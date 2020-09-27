# -*- coding: utf-8 -*-

import shutil

def print_tab(tab_content) :
    
    """ Displays a tab with data in tab_content.
    Format required of tab_content:
        - tab_content is a list.
        - Each element of that list represent a line
            - If the element is None, draw a separator
            - Else, the element has to be a list containing the data to display 
              in that line. Each element of this sublist represent the column data.
    Example:
        tab_content = [None,['Hello','world'],None] produce automatically:
         =====================
        | Hello    | world    |
         =====================
    
    When a line is too long regarding the terminal size, the last column data
    is divided in several line automatically.
    """
    
    OFFSET_LEFT = 1
    OFFSET_RIGHT = 4
    SEP_SIGN = '='
        
    def split_sentence(sentence,maxlen) :
        parts = []
        words = sentence.split(' ')
        while len(words) > 0 :
            if len(words)==1 : 
                parts.append(words[0])
                words = []
            else :
                for i in range(len(words)) :
                    if i != len(words)-1 and len(' '.join(words[:i+2])) > maxlen :
                        break
                parts.append(' '.join(words[:i+1]))
                words = words[i+1:]
        return parts
        
    def split_line_content(line_content,last_col_max_width):
        new_content = []
        last_col_splitted = split_sentence(line_content[-1],last_col_max_width)
        for i in range(len(last_col_splitted)) :
            if i == 0 : new_content.append(line_content[:-1]+[last_col_splitted[0]])
            else : new_content.append(['']*len(line_content[:-1])+[last_col_splitted[i]])
        return new_content
    
    def get_col_widths(tab_content):
        col_widths = []
        for i in range(get_nb_col(tab_content)) :
            col_widths.append(max([len(c[i]) for c in tab_content if c is not None]))
        return col_widths
    
    def get_total_width(tab_content):
        col_widths = get_col_widths(tab_content)
        return sum(col_widths) + (OFFSET_LEFT+OFFSET_RIGHT+1)*len(col_widths) + 2
        
    def get_nb_col(tab_content):
        for line_content in tab_content : 
            if line_content is not None :
                return len(line_content)
            
    def process_tab_content(tab_content):
        terminal_size = shutil.get_terminal_size().columns
        if get_total_width(tab_content) > terminal_size :
            col_widths = get_col_widths(tab_content)
            last_col_max_width = terminal_size - (sum(col_widths[:-1]) + (OFFSET_LEFT+OFFSET_RIGHT+1)*len(col_widths) + 2)
            if last_col_max_width <= 0 : print('Console too small: impossible to display.')
            else: 
                new_tab_content = []
                for i in range(len(tab_content)) :
                    if tab_content[i] is None : new_tab_content.append(None)
                    else : 
                        new_tab_content += split_line_content(tab_content[i],last_col_max_width)
                tab_content = new_tab_content
        return tab_content

    tab_content = process_tab_content(tab_content)
    nb_col = get_nb_col(tab_content)
    col_widths = get_col_widths(tab_content)
    total_width = get_total_width(tab_content)
    
    # Str to print
    str_to_print = ''
    for i in range(len(tab_content)):
        if tab_content[i] is None : 
            str_to_print += ' '+SEP_SIGN*(total_width-3)
        else :
            str_to_print += '|'
            for col in range(nb_col) :
                str_to_print += ' '*OFFSET_LEFT
                str_to_print += tab_content[i][col] + ' '*(col_widths[col]-len(tab_content[i][col]))
                str_to_print += ' '*OFFSET_RIGHT + '|'
        if i != len(tab_content)-1 :
            str_to_print += '\n'
    
    print(str_to_print)