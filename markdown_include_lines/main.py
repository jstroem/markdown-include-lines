#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# main.py
#
#Cyroxx Software Lizenz 1.0
#Copyright (c) 30.01.2018, Simon Renger <info@simonrenger.de>
#Alle Rechte vorbehalten.
#Durch diese Lizenz ist der nachfolgende Quelltext in all seinen Erscheinungsformen [Beispiele: Kompiliert, Unkompiliert, Script Code] geschützt.
#Im nachfolgenden Text werden die Worte Werk, Script und Quelltext genutzt Diese drei Wörter sind gleichzusetzen und zu schützen.
#Der Autor dieses Werkes kann für keinerlei Schaden die durch das Werk enstanden sein könnten, entstehen werden verantwortlich gemacht werden.
#
#Rechte und Pflichten des Nutzers dieses Werkes:
#Der Nutzer dieses Werkes verpflichtet sich, diesen Lizenztext und die Autoren-Referenz auszuweisen und in seiner originalen Erscheinungsform zu belassen.
#Sollte dieses Werk kommerziell genutzt werden, muss der Autor per E-Mail informiert werden, wenn eine E-Mail Adresse angegeben/bekannt ist.
#Das Werk darf solange angepasst, verändert und zu verändertem Zwecke genutzt werden, wie dieser Lizenztext und die Autor(en)-Referenz ausgewiesen wird und
#nicht gegen die Lizenzvereinbarungen verstößt.
#Das Werk darf nicht für illigale Zwecke eingesetzt werden.
#
# This project is ensprired by https://github.com/cmacmackin/markdown-include
#
# the syntax of this project is: [...] subtsitute with the right content
# {[file type] [start at line] - [end at line] [file]}
# example:
# {include-file 15-20 include.py}
# In case you want to include the whole file:
# {include-file * include.py}
# In case you want to include a suffix of a file:
# {include-file 15- include.py}
# In case you want to include a preffix of a file:
# {include-file -15 include.py}
# In case you want to include only one line:
# {include-file 15 include.py}
# In case you want to include only certain lines of code:
# {include-file [15,20,3] include.py}

from __future__ import print_function
import re
import os.path
from codecs import open
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

# version 1.0
#SYNTAX = re.compile(r'\{([a-z]+)\s(([0-9]+)\s-\s([0-9]+)|([0-9]+)-([0-9]+)|([0-9]+)\s-([0-9]+)|([0-9]+)-\s([0-9]+)|\*)\s(.*)}')
#version 1.2
SYNTAX = re.compile(r'\{include\-file\s(([0-9]+)?\s?-\s?([0-9]+)?|\*|([0-9]+)|\[(.*)\])\s(.*)}')

class MarkdownIncludeLines(Extension):
    def __init__(self, configs={}):
        self.config = {
            'base_path': [os.getcwd(), 'Default location for the file to be checked' \
                'relative paths for the include statement.'],
            'encoding': ['utf-8', 'Encoding of the files ' \
                'statement.']
        }
        for key, value in configs.items():
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'include_lines', IncLinePreprocessor(md,self.getConfigs()),'_begin'
        )

class IncLinePreprocessor(Preprocessor):
    #member vars:
    #contains
    m_filename = None
    m_code = []
    #methods:
    def __init__(self,md,config):
        super(IncLinePreprocessor, self).__init__(md)
        self.base_path = os.path.abspath(config['base_path'])
        self.encoding = config['encoding']
    def run(self,lines):
        done = False
        while not done:
            done = True
            for line in lines:
                loc = lines.index(line)
                if SYNTAX.search(line):
                    match = SYNTAX.match(line)
                    if match == None:
                        continue
                    filename = match.group(6)
                    start = -1
                    end = -1

                    rangeList = []
                    if match.group(2) != None or match.group(3) != None:
                        if match.group(2) != None:
                            start = int(match.group(2))
                        else:
                            start = 0
                        if match.group(3) != None:
                            end = int(match.group(3))
                    elif match.group(5) != None:
                      rangeList = match.group(5).split(",")
                    elif match.group(1) != None:
                      if match.group(1) == "*":
                         start = 0
                      else:
                        end = start = int(match.group(1))

                    result = []
                    if len(rangeList) == 0:
                        result = self.parse(filename,start,end)
                    else:
                        for index in rangeList:
                            line = self.parse(filename,int(index),int(index))
                            if len(line) > 0:
                                result.append("[...]")
                                result.extend(line)
                            else:
                                result.append("Line: "+index+" Could not be found.")
                    if len(result) > 0:
                        done = False
                        lines = lines[:loc] +result+ lines[loc+1:]

                    if filename != self.m_filename:
                        self.m_filename = filename
        return lines

    def parse(self,filename,start=0,end=0):
        if start > 0:
            start -= 1
        if end > 0:
            end -= 1

        #check if filename is not the same then load data
        data = None
        if filename != self.m_filename:
            data = self.readFile(filename)
        else:
            data = self.m_code

        #parse
        outcome = []
        for cnt, line in enumerate(data):
            line = line.rstrip('\n')
            if cnt >= start and (cnt <= end or end == -1):
                outcome.append(str(cnt)+": "+line)
        return outcome

    def readFile(self,filename):
        filename = os.path.expanduser(filename)
        if not os.path.isabs(filename):
            filename = os.path.normpath(
                os.path.join(self.base_path,filename)
            )
        try:
            #open file:
            with open(filename, 'r', encoding=self.encoding) as file:
                self.m_code = file.readlines()
                return self.m_code
        except Exception as e:
            print('Warning: could not find file {}. Ignoring '
                'include statement. Error: {}'.format(filename, e))
            return ['Warning: could not find file {}.'.format(filename, e)]


def makeExtension(*args,**kwargs):
    return MarkdownIncludeLines(kwargs)

# For testing
# if __name__ == "__main__":
#     processor = IncLinePreprocessor(None, {"base_path": ".", "encoding": "utf-8"})
#     print("Result:", processor.run(["{include-file 5- test.txt}"]))
