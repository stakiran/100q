# -*- coding: utf-8 -*-

import os
import sys

def file2list(filepath):
    ret = []
    with open(filepath, 'r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

def list2file(filepath, ls):
    with open(filepath, 'w') as f:
        f.writelines(['%s\n' % line for line in ls] )

def terminalencoding2utf8(bytestr):
    return bytestr.decode(sys.stdin.encoding).encode('utf8')

def strbool2bool(bytestr):
    l = bytestr.lower()
    if l in ['n', 'no', 'false']:
        return False
    if l in ['y', 'yes', 'true']:
        return True
    raise RuntimeError('Invalid boolean value "{0}".'.format(bytestr))

def raise_option_error(msg, lineno, line):
    raise RuntimeError('{0} at line {1}, "{2}".'.format(msg, lineno, line))

def append_to_out(appendee_list, appender, use_ignore=False):
    if use_ignore:
        return
    appendee_list.append(appender)

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='100q generator.'
    )
    parser.add_argument('-i', '--input', default=None, required=True,
        help='A input filename.')
    parser.add_argument('-o', '--output', default=None, required=True,
        help='A output filename.')

    parser.add_argument('-l', '--limit', default=-1, type=int,
        help='The limit of the number of output. No limit if minus given.')

    args = parser.parse_args()
    return args

args = parse_arguments()

MYDIR = os.path.abspath(os.path.dirname(__file__))
infile = os.path.join(MYDIR, args.input)
outfile = os.path.join(MYDIR, args.output)
limitcount = args.limit

opt_fmt_cate         = '## (@)'
opt_fmt_q            = '## @@ @'
opt_catemark         = '***'
opt_numbering_format = '03d'
ignore_blank         = False
is_limit_over        = False

lines = file2list(infile)
outlines = []
curno = 1
for i,line in enumerate(lines):
    if limitcount>=0 and curno>limitcount and is_limit_over==False:
        is_limit_over = True
        continue

    # blank line
    if len(line)==0:
        if not ignore_blank:
            append_to_out(outlines, '', is_limit_over)
        continue

    # comment line
    #   ; comment
    #   <!-- comment -->
    #   // comment
    if line[0]==';' or line[0]=='<' or line[0]=='/':
        continue

    # header/footer line
    if line[0]==' ':
        append_to_out(outlines, line[1:])
        continue

    # content line
    #   '-' and '*' is a list grapper in GFM.
    if line[0]=='-' or line[0]=='*':
        # - A question
        # ^^
        # Cut here.
        line = line[1:].strip()

        if line.find(opt_catemark)!=-1:
            appendee = line.replace(opt_catemark, '').strip()
            newline = opt_fmt_cate.replace('@', appendee)
        else:
            numbering_format = '{0:'+opt_numbering_format+'}'
            numbered_format = opt_fmt_q.replace(
                '@@',
                numbering_format.format(curno)
            )
            appendee = line.strip()
            newline = numbered_format.replace('@', appendee)
            curno += 1
        append_to_out(outlines, newline, is_limit_over)
        continue

    # options
    #   (key)=(value)
    if line.find('=')==-1:
        raise_option_error('No option format', i+1, line)
    optname, value = line.split('=', 1)

    if optname=='category_format':
        opt_fmt_cate = value
    elif optname=='question_format':
        opt_fmt_q = value
    elif optname=='category_mark':
        opt_catemark = value
    elif optname=='numbering_format':
        opt_numbering_format = value
    elif optname=='ignore_blank':
        ignore_blank = strbool2bool(value)
    else:
        raise_option_error('Invalid option format', i+1, line)

list2file(outfile, outlines)
