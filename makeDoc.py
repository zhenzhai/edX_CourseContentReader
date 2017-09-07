#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict


def makeCourse(p):
    chapters = []
    chapter_path = p / 'course' /'course.xml'
    course_txt = chapter_path.open().readlines()[1:]
    for cline in course_txt:
        if 'chapter' in cline:
            chap_name = cline.split('"')[1]
            chapters.append(chap_name)
    return chapters


def describeChapter(vertical, chapters, p, readme):
    chapter_path = p/'chapter'
    for c in chapters:
        c += '.xml'
        cFile = chapter_path / c
        chap_txt = cFile.open().readlines()
        first_line = chap_txt[0]
        chap_name = first_line[first_line.index('="')+2:first_line.index('">')]
        readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, str(cFile)))
        seq_list = [l[l.index('="')+2:l.index('"/>')] for l in chap_txt if "sequential" in l]
        describeSequen(seq_list, vertical, p, readme)


def describeSequen(seq, ver, p, readme):
    seq_path = p/'sequential'
    for s in seq:
        s_name = s + '.xml'
        sFile = seq_path/s_name
        s_txt = sFile.open().readlines()
        fline = s_txt[0]
        sequ_name = fline[fline.index('="')+2:].split('"')[0]
        readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, str(sFile)))
        describeVert(ver[s], p, readme)


def describeVert(ver, p, readme):
    for v in ver:
        vp = Path(v[0])
        fline = vp.open().readlines()[0]
        v_name = fline[fline.index('name="')+6:].split('"')[0]
        readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(v_name, v[0]))
        describeProb(v[1:], p, readme)


def describeProb(probs, p, readme):
    pro_path = p / 'drafts'
    for pro in probs:
        pro_name = pro[1]+'.xml'
        pFile = pro_path / pro[0] / pro_name
        p_txt = pFile.open().readlines()
        fline = p_txt[0]
        p_name = fline.split('"')[1]
        if pro[0] == 'problem':
            readme.write('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, str(pFile)))
        else:
            readme.write('\t\t\t* [{0}] - [{1}]({1})\n'.format(pro[0], str(pFile)))


def makeVertical(p):
    vert_path = p / 'drafts' / 'vertical'
    structure = defaultdict(list)
    for v in vert_path.iterdir():
        if v.suffix != '.xml':
            continue
        v_txt = v.open().readlines()
        fline = v_txt[0]
        sec_name = fline[fline.index('+block@')+7:].split('"')[0]
        rank = fline[fline.index('index'):].split('"')[1]
        comp_list = [int(rank), str(v)]
        for vline in v_txt[1:]:
            if '<problem ' in vline:
                prob = vline.split('"')[1]
                comp_list.append(['problem',prob])
            elif '<video ' in vline:
                prob = vline.split('"')[1]
                comp_list.append(['video', prob])
            elif '<html ' in vline:
                prob = vline.split('"')[1]
                comp_list.append(['html', prob])
        structure[sec_name].append(comp_list)
    for k in structure:
        sorted_struct = sorted(structure[k], key = lambda x: x[0])
        structure[k] = [s[1:] for s in sorted_struct]
    return structure


def describe():
    path = Path('.')
    chap_list = makeCourse(path)
    ver_structure = makeVertical(path)
    readme = open('README.md', 'w')
    readme.write("###Course structure - [course/course.xml](course/course.xml)\n")
    describeChapter(ver_structure, chap_list, path, readme)
    readme.close()


describe()

