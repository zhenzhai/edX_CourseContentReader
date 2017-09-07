#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict

class Doc:

    path = Path('.')
    course_path = path / 'course'
    chapter_path = path / 'chapter'
    seq_path = path / 'sequential'
    draft_path = path / 'drafts'
    vert_path = draft_path / 'vertical'
    chapter_list = []
    problems_struct = defaultdict(list)


    def __makeCourse(self):
        course_path = self.course_path / 'course.xml'
        course_txt = course_path.open().readlines()[1:]
        for cline in course_txt:
            if 'chapter' in cline:
                chap_name = cline.split('"')[1]
                self.chapter_list.append(chap_name)

    def __makeStruct(self):
        self.problems_struct = defaultdict(list)
        for v in self.vert_path.iterdir():
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
            self.problems_struct[sec_name].append(comp_list)
        for k in self.problems_struct:
            sorted_struct = sorted(self.problems_struct[k], key = lambda x: x[0])
            self.problems_struct[k] = [s[1:] for s in sorted_struct]


    def __init__(self):
        self.__makeCourse()
        self.__makeStruct()


    def describeCourse(self):
        readme = open('README.md', 'w')
        readme.write("###Course structure - [course/course.xml](course/course.xml)\n")
        self.describeChapter(readme)
        readme.close()


    def describeChapter(self, readme):
        for c in self.chapter_list:
            c += '.xml'
            cFile = self.chapter_path / c
            chap_txt = cFile.open().readlines()
            first_line = chap_txt[0]
            chap_name = first_line.split('"')[1]
            readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, str(cFile)))
            seq_list = [l.split('"')[1] for l in chap_txt if "sequential" in l]
            self.describeSequen(seq_list, readme)


    def describeSequen(self, seq, readme):
        for s in seq:
            s_name = s + '.xml'
            sFile = self.seq_path / s_name
            s_txt = sFile.open().readlines()
            fline = s_txt[0]
            sequ_name = fline.split('"')[1]
            readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, str(sFile)))
            self.describeUnit(self.problems_struct[s], readme)


    def describeUnit(self, unit, readme):
        for u in unit:
            uPath = Path(u[0])
            fline = uPath.open().readlines()[0]
            u_name = fline.split('"')[1]
            readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(u_name, u[0]))
            self.describeProb(u[1:], readme)

    
    def describeProb(self, probs, readme):
        for pro in probs:
            pro_name = pro[1]+'.xml'
            pFile = self.draft_path / pro[0] / pro_name
            p_txt = pFile.open().readlines()
            fline = p_txt[0]
            p_name = fline.split('"')[1]
            if pro[0] == 'problem':
                readme.write('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, str(pFile)))
            else:
                readme.write('\t\t\t* [{0}] - [{1}]({1})\n'.format(pro[0], str(pFile)))




if __name__ == "__main__":
    writeDoc = Doc()
    writeDoc.describeCourse()

