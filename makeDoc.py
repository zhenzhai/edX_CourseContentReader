#!/usr/bin/env python

from pathlib import Path
from collections import defaultdict
from collections import OrderedDict
import re
import json
import sys
import os

class Doc:
    """
    Create a detail documentation for the course file exported from edX.
    """

    def __makeCourse(self):
        """
        Create a list of chapters by reading course.xml
        """
        course_file_list = list(self.course_path.iterdir())
        self.course_file = [x for x in course_file_list if x.suffix == '.xml'][0]
        course_txt = self.course_file.open().readlines()
        for cline in course_txt:
            if 'chapter' in cline:
                chap_name = cline.split('"')[1]
                self.chapter_list.append(chap_name)

    def __makeDraftStruct(self):
        """
        Create a problems to units mapping for drafts by reading files from folder vertical
        Draft problems are linked backward. When draft problems are published, it will then link from top down.
        Therefore, we need to construct the draft files ahead of time.
        """
        for v in self.draft_vert_path.iterdir():
            if v.suffix != '.xml':
                continue
            v_txt = v.open().readlines()
            fline = v_txt[0]
            sec_name = fline.split('parent_url=')[1].split('"')[1].split('/')[-1].split('@')[-1]
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
            if sec_name not in self.draft_problems_struct.keys():
                self.draft_problems_struct[sec_name] = [comp_list]
            else:
                self.draft_problems_struct[sec_name].append(comp_list)
        for k in self.draft_problems_struct:
            sorted_struct = sorted(self.draft_problems_struct[k], key = lambda x: x[0])
            self.draft_problems_struct[k] = [s[1:] for s in sorted_struct]

    def __init__(self, start_path):
        """
        Initialize the class by assigning values to path variables.
        Input:
            [start_path]: name of the course directory. The course need to be unzipped.
        """
        if not os.path.isdir(start_path):
            sys.exit("\033[91m ERROR: can't find directory {} \033[0m".format(start_path))

        ## Path variables
        self.path = Path(start_path)
        self.course_path = self.path / 'course'
        self.chapter_path = self.path / 'chapter'
        self.seq_path = self.path / 'sequential'
        self.vert_path = self.path / 'vertical'

        self.draft_path = self.path / 'drafts'
        self.draft_vert_path = self.draft_path / 'vertical'

        ## List of all chapters
        self.chapter_list = []

        ## Structure of sections and units
        self.draft_problems_struct = OrderedDict()
        self.public_problems_struct = OrderedDict()
        self.all_problems_struct = OrderedDict()

        ## Make course struct
        self.__makeCourse()
        self.__makeDraftStruct()


    def describeCourse(self):
        """
        Write header to the README.md with the course name.
        """
        readme = open(str(self.path)+'/README.md', 'w')
        readme.write("###Course structure - [course/{0}](course/{0})\n".format(self.course_file.name))
        self.describeChapter(readme)
        readme.close()


    def describeChapter(self, readme):
        """
        Write section information into readme
        """
        for c in self.chapter_list:
            # build path
            c += '.xml'
            cFile = self.chapter_path / c

            # write to file
            chap_txt = cFile.open().readlines()
            cFile = cFile.relative_to(*cFile.parts[:1])
            first_line = chap_txt[0]
            chap_name = first_line.split('"')[1]
            readme.write('* [Section] {0} - [{1}]({1})\n'.format(chap_name, str(cFile)))

            # remove empty sequential item
            seq_list = [l.split('"')[1] for l in chap_txt if "sequential" in l]

            # pass to describe the sequence further
            pub_seq_struct, all_seq_struct = self.describeSequen(seq_list, readme)

            ### public struct
            self.public_problems_struct[chap_name] = pub_seq_struct
            ### use section title + last 5 digits of file id as key
            self.all_problems_struct['('+c[-9:-4]+')'+chap_name] = (str(cFile), all_seq_struct)

        self.public_problems_struct = dict((k, v) for k, v in self.public_problems_struct.iteritems() if v)


    def describeSequen(self, seq, readme):
        """
        Write subsection information into readme
        Input:
            [seq]: the list of sequential file to describe further
        """
        pub_seq = OrderedDict()
        all_seq = OrderedDict()
        for s in seq:
            unpublished = False
            s_name = s + '.xml'
            sFile = self.seq_path / s_name
            seq_txt = sFile.open().readlines()
            sFile = sFile.relative_to(*sFile.parts[:1])
            first_line = seq_txt[0]
            sequ_name = first_line.split('"')[1]
            readme.write('\t* [Subsection] {0} - [{1}]({1})  \n'.format(sequ_name, str(sFile)))
            if len(seq_txt) > 2:
                unit_list = [l.split('"')[1] for l in seq_txt if "vertical" in l]
                pub_dict, all_dict = self.describeUnit(unit_list, readme)
                pub_seq[sequ_name] = pub_dict

                ### check draft
                if s in self.draft_problems_struct.keys():
                    ### if a file exist both in draft and public, means it is altered and not saved.
                    ### keep the public file in README.
                    old_list = self.draft_problems_struct[s][:]
                    for u in old_list:
                        u_id = u[0].split('/')[-1].split('.xml')[0]
                        if u_id in unit_list:
                            unpublished = True
                            self.draft_problems_struct[s].remove(u)
                    if self.draft_problems_struct[s]:
                        all_dict2 = self.describeDraftUnit(self.draft_problems_struct[s], readme)
                        for d in all_dict2:
                            all_dict[d] = all_dict2[d]

                ### use subsection title + last 5 digits of file id as key
                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

                if unpublished:
                    print('\033[93m Warning: There are unpublished changes in published problems under subsection {}. Only looking at published version.\033[0m'.format(sequ_name))

            else: #check draft
                if s not in self.draft_problems_struct.keys():
                    all_dict = OrderedDict()
                else:
                    all_dict = self.describeDraftUnit(self.draft_problems_struct[s], readme)
                ### use subsection title + last 5 digits of file id as key
                all_seq['('+s_name[-9:-4]+')'+sequ_name] = (str(sFile), all_dict)

        pub_seq = dict((k, v) for k, v in pub_seq.iteritems() if v)
        return pub_seq, all_seq

    def describeUnit(self, uni, readme):
        """
        Write unit information into readme
        Input:
            [uni]: the list of unit files to describe further
        """
        pub_uni = OrderedDict()
        all_uni = OrderedDict()
        for u in uni:
            u += '.xml'
            uFile = self.vert_path / u
            uni_txt = uFile.open().readlines()
            uFile = uFile.relative_to(*uFile.parts[:1])
            first_line = uni_txt[0]
            u_name = first_line.split('"')[1]
            readme.write('\t\t* [Unit] {0} - [{1}]({1})\n'.format(u_name, uFile))
            prob_list = []
            for l in uni_txt[1:]:
                if '<problem ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['problem',prob])
                elif '<video ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['video', prob])
                elif '<html ' in l:
                    prob = l.split('"')[1]
                    prob_list.append(['html', prob])
                #elif '<discussion ' in l:
                #    prob = l.split('"')[1]
                #    comp_list.append(['discussion', prob])

            pub_dict, all_dict = self.describeProb(prob_list, readme)
            pub_uni[u_name] = pub_dict
            ### use unti title + last 5 digits of file id as key
            all_uni['('+u[-9:-4]+')'+u_name] = (str(uFile), all_dict)
        pub_uni = dict((k, v) for k, v in pub_uni.iteritems() if v)
        return pub_uni, all_uni

    def describeProb(self, prob_list, readme):
        """
        Write component information into readme
        Input:
            [prob_list]: the list of problems to describe further
        """
        pub_prob = OrderedDict()
        pro_list = []

        pat1 = re.compile(r'<problem ([^>]+)>')
        pat2 = re.compile(r'(\S+)="([^"]+)"')

        for pro in prob_list:
            pro_name = pro[1]+'.xml'
            pFile = self.path / pro[0] / pro_name
            p_txt = pFile.open().readlines()
            pFile = pFile.relative_to(*pFile.parts[:1])
            fline = p_txt[0]
            m = pat1.match(fline)
            if m:
                params = m.group(1)
                m2 = pat2.findall(params)
                Dict= {key:val for key,val in m2 if key!='markdown'}
                p_name = Dict['display_name']
                if 'weight' in Dict.keys():
                    weight = Dict['weight']
                    if 'max_attempts' in Dict.keys():
                        max_att = Dict['max_attempts']
                        pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight'], 'max_attempts':Dict['max_attempts']}
                    else:
                        pub_prob[p_name] = {'file':pro_name, 'weight':Dict['weight']}
                readme.write('\t\t\t* [{0}] {1} - [{2}]({2})\n'.format(pro[0], p_name, str(pFile)))
                #readme.write('\t\t\t\t Weight: {0}, Max Attempts: {1}\n'.format(weight, max_att))
            else:
                readme.write('\t\t\t* [{0}] - [{1}]({1})\n'.format(pro[0], str(pFile)))
            pro_list.append((str(pFile), pro[0]))

        pub_prob = dict((k, v) for k, v in pub_prob.iteritems() if v)
        return pub_prob, pro_list

    def describeDraftUnit(self, unit, readme):
        """
        Write draft unit information into readme
        Again, draft need to be handled specifically because it is linked backward.
        Input:
            [unit]: the list of unit files that need to be described further.
        """
        all_uni = OrderedDict()
        for u in unit:
            uFile = Path(u[0])
            first_line = uFile.open().readlines()[0]
            uFile = uFile.relative_to(*uFile.parts[:1])
            u_name = first_line.split('"')[1]
            readme.write('\t\t* [Unit]\(Draft\) {0} - [{1}]({1})\n'.format(u_name, str(uFile)))
            prob_list = self.describeDraftProb(u[1:], readme)
            ### use unit title + last 5 digits of file id as key
            all_uni['('+u[0][-9:-4]+')(draft)'+u_name] = (str(uFile), prob_list)
        return all_uni

    
    def describeDraftProb(self, probs, readme):
        """
        Write draft component information into readme
        Again, draft need to be handled specifically because it is linked backward.
        Input:
            [probs]: the list of problem files that need to be described further.
        """
        prob_list = []
        for pro in probs:
            pro_name = pro[1]+'.xml'
            pFile = self.draft_path / pro[0] / pro_name
            p_txt = pFile.open().readlines()
            pFile = pFile.relative_to(*pFile.parts[:1])
            fline = p_txt[0]
            p_name = fline.split('"')[1]
            if pro[0] == 'problem':
                readme.write('\t\t\t* [{0}]\(Draft\) {1} - [{2}]({2})\n'.format(pro[0], p_name, str(pFile)))
            else:
                readme.write('\t\t\t* [{0}]\(Draft\) - [{1}]({1})\n'.format(pro[0], str(pFile)))
            prob_list.append((str(pFile), '(draft)'+pro[0]))
        return prob_list


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("\033[91m Please pass in the name of the course folder.\033[0m")
    else:
        folder_name = sys.argv[1]
    writeDoc = Doc(folder_name)
    writeDoc.describeCourse()
    #all_prob_dict = writeDoc.all_problems_struct

    ### Write problem config file
    #prob_config = writeDoc.public_problems_struct
    #with open('problem_config.json', 'w') as fp:
    #    fp.write(json.dumps(prob_config, indent=4))

