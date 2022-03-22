"""
ver 1.0.5. - 20220322
============================================================
                       업데이트 내역
------------------------------------------------------------
ver. 1.0.5. 자소검색 와일드카드 문자(*) 오류 수정
ver. 1.0.4. 에러 핸들링: QMessageBox 20220322
ver. 1.0.3. 판다스 데이터프레임을 딕셔너리로 변환 20220322
ver. 1.0.2. 자소검색 기능 추가 20220322
ver. 1.0.1. 검색 스트링을 첫가끝으로 변환 20220317
ver. 1.0.0. Initial Setting 20220309
============================================================
"""
#%% 모듈 임포팅
import re
import os

#%% 스트링을 첫가끝으로 변환
def PUAtoUni(test, dict_0_TOTAL): # df_0_TOTAL: ver. 1.0.2.

    new_line = ''
    for i in range(len(test)):
        tt = ord(test[i])
        ## 한양PUA -> 첫가끝 ##
        if (tt >= 0xe0bc and tt <= 0xefff) or (tt >= 0xf100 and tt <= 0xf66e):
            new_line = new_line + dict_0_TOTAL['조합형'][tt]
            # new_line = new_line + df_0_TOTAL.loc[tt][0] // ver. 1.0.2.
        ## 조합형 -> 첫가끝 ##
        elif (tt >= 0xac00 and tt <=0xd79f):
            onset = chr(((tt - 0xac00) // (28*21)) + 0x1100)
            peak = chr((((tt - 0xac00) % (28*21)) // 28) + 0x1161)
            coda = chr(((tt - 0xac00) % 28) + 0x11a7)
              
            new_line += onset
            new_line += peak
            if (tt - 0xac00) % 28 != 0: new_line += coda
        else:
            new_line += test[i]

    return new_line

#%% 자소 검색이 가능하도록 변환
#먼저 PUAtoUni에 넣고 올 것
def seperation(findWord, dict_0_ONSET, dict_0_PEAK, dict_0_CODA):
    start_list = []
    end_list = []
    sep_list = []
    com_list = []
    sep_re = re.compile('\[(.*?)\]')

    # 자소 검색된 단위 찾기
    for item in sep_re.finditer(findWord):
        start_list.append(item.start())
        end_list.append(item.end())
        sep_list.append(item.group()[1:-1])
    
    # 자모를 조합
    """
    자모 초성: 1100-115e, a960-a97c
    자모 중성: 1161-11a7, d7b0-d7c6
    자모 종성: 11a8-11ff, d7cb-d7fb
    """
    for syllable in sep_list:
        phone_list = syllable.split('/')
        if len(phone_list) != 3:
            return '!!error!!'

        ## onset ##
        if phone_list[0] == '*':
            onset = '[\u1100-\u115e\ua960-\ua97c]'
        elif phone_list[0] == '@':
            onset = ''
        else:
            onset = dict_0_ONSET['SEP'][phone_list[0]]

        ## peak ##
        if phone_list[1] == '*':
            peak = '[\u1161-\u11a7\ud7b0-\ud7c6]'
        else:
            peak = dict_0_PEAK['SEP'][phone_list[1]]

        ## coda ##
        if phone_list[2] == '*':
            coda = '[\u11a8-\u11ff\ud7cb-\ud7fb]'
        elif phone_list[2] == '@':
            coda = ''
        else:
            coda = dict_0_CODA['SEP'][phone_list[2]]

        new_syll = onset + peak + coda
        com_list.append(new_syll)

    for i in range(len(com_list)):
        sep_r = '[' + sep_list[i] + ']'
        findWord = findWord.replace(sep_r, com_list[i])

    return findWord

#%% 검색
def searchForWord(direc, obj_word):
    sent = re.compile('\<(.*?)\>')
    new_file = "result.txt"
    result_line = ''
    full_text = ''
    iter = 1

    file_list = os.listdir(direc)
    f = open(new_file, 'w', encoding='utf-8')

    for file in file_list:
        file_name = direc + file
        file_xml = open(file_name, 'r', encoding='utf-8')
        text_xml = file_xml.readlines()

        for line in text_xml:
            line = line.replace('\t', '')
            if re.match(sent, line):
                pos = re.match(sent, line).group()
                
            for word in re.finditer(obj_word, line):
                page_list = re.findall('page="(.*?)"', pos)
                if len(page_list) != 0:
                    page = page_list[0]
                else:
                    page = '!page error'

                sta = word.start()
                end = word.end()
                new_line = line[:sta] + '▶' + line[sta:end] + '◀' + line[end:]
                new_line = re.sub(r'\<(.*?)\>', '', new_line).replace('\n', '')

                result_line += "[" + str(iter) + "]\t" + file + "\t" + '<' + page + '>\t' + new_line + '\n'

                f.write(result_line)
                full_text += result_line
                iter += 1
                result_line = ''

    f.close()
    return full_text, iter