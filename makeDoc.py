#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict

def describeChapter(vertical, p, readme):
    chapter_path = p/'chapter'
    for c in chapter_path.iterdir():
        chap_txt = c.open().readlines()
        first_line = chap_txt[0]
        chap_name = first_line[first_line.index('="')+2:first_line.index('">')]
        readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, str(c)))
        seq_list = [l[l.index('="')+2:l.index('"/>')] for l in chap_txt if "sequential" in l]
        describeSequen(seq_list, vertical, p, readme)


def describeSequen(seq, ver, p, readme):
    seq_path = p/'sequential'
    for s in seq:
        s_name = s + '.xml'
        sFile = seq_path/s_name
        s_txt = sFile.open().readlines()
        fline = s_txt[0]
        sequ_name = fline[fline.index('="')+2:fline.index('"/>')]
        readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, str(sFile)))
        readme.write('\t\t [Problems Pointers] - [{0}]({0})\n'.format(ver[s][0]))
        describeProb(ver[s][1:], p, readme)


def describeProb(probs, p, readme):
    pro_path = p / 'drafts' / 'problem'
    for pro in probs:
        pro+='.xml'
        pFile = pro_path / pro
        p_txt = pFile.open().readlines()
        fline = p_txt[0]
        p_name = fline[fline.index('display_name="')+14:].split('"')[0]
        readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(p_name, str(pFile)))


def describeVertical(p):
    vert_path = p / 'drafts' / 'vertical'
    structure = defaultdict(list)
    for v in vert_path.iterdir():
        if v.suffix != '.xml':
            continue
        v_txt = v.open().readlines()
        fline = v_txt[0]
        sec_name = fline[fline.index('+block@')+7:].split('"')[0]
        structure[sec_name].append(str(v))
        for vline in v_txt[1:]:
            if '<problem ' in vline:
                prob = vline[vline.index('="')+2:].split('"')[0]
                structure[sec_name].append(prob)
    return structure


def describe():
    path = Path('.')
    ver_structure = describeVertical(path)
    print ver_structure
    readme = open('README.md', 'w')
    readme.write("###Folder structure\n")
    describeChapter(ver_structure, path, readme)
    readme.close()


describe()





