#!/usr/bin/env python

## EPlusInterface (EPI) - An interface for EnergyPlus
## Copyright (C) 2004 Santosh Philip
# =======================================================================
#  Distributed under the MIT License.
#  (See accompanying file LICENSE or copy at
#  http://opensource.org/licenses/MIT)
# =======================================================================

"""legacy code from EPlusInterface"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import eppy.EPlusInterfaceFunctions.mylib1 as mylib1
import eppy.EPlusInterfaceFunctions.mylib2 as mylib2
import eppy.EPlusInterfaceFunctions.mylib3 as mylib3


def nocomment(astr, com):
    """
    just like the comment in python.
    removes any text after the phrase 'com'
    """
    alist = astr.splitlines()
    for i in range(len(alist)):
        element = alist[i]
        pnt = element.find(com)
        if pnt != -1:
            alist[i] = element[:pnt]
    return '\n'.join(alist)

def get_nocom_vars(astr):
    """
    input 'astr' which is the Energy+.idd file as a string
    returns (st1, st2, lss)
    st1 = with all the ! comments striped
    st2 = strips all comments - both the '!' and '\\'
    lss = nested list of all the variables in Energy+.idd file
    """
    nocom = nocomment(astr, '!')# remove '!' comments
    st1 = nocom
    nocom1 = nocomment(st1, '\\')# remove '\' comments
    st1 = nocom
    st2 = nocom1
    # alist = string.split(st2, ';')
    alist = st2.split(';')
    lss = []

    # break the .idd file into a nested list
    #=======================================
    for element in alist:
        # item = string.split(element, ',')
        item = element.split(',')
        lss.append(item)
    for i in range(0, len(lss)):
        for j in range(0, len(lss[i])):
            lss[i][j] = lss[i][j].strip()
    if len(lss) > 1:
        lss.pop(-1)
    #=======================================

    #st1 has the '\' comments --- looks like I don't use this
    #lss is the .idd file as a nested list
    return (st1, st2, lss)

def removeblanklines(astr):
    """
    removeblanklines(astr)
    returns the string after
    remove blank lines in 'astr'
    """
    linesep = mylib3.getlinesep(astr)
    alist = astr.split(linesep)
    lss = []
    for element in alist:
        ell = element.strip()
        if ell != '':
            lss.append(element)
    st1 = linesep.join(lss)
    return st1


def extractidddata(fname, debug=False):
    """
    extracts all the needed information out of the idd file
    if debug is True,  it generates a series of text files.
    Each text file is incrementally different. You can do a diff
    see what the change is
    """
    from StringIO import StringIO
    from io import FileIO
    try:
        if isinstance(fname, (file, StringIO)):
            astr = fname.read()
            try:
                astr = astr.decode('ISO-8859-2')
            except AttributeError:
                pass 
        else:
            astr = mylib2.readfile(fname)
            # astr = astr.decode('ISO-8859-2') -> mylib1 does a decode
    except NameError:
        if isinstance(fname, (FileIO, StringIO)):
            astr = fname.read()
            try:
                astr = astr.decode('ISO-8859-2')
            except AttributeError:
                pass
        else:
            astr = mylib2.readfile(fname)
            # astr = astr.decode('ISO-8859-2') -> mylib2.readfile has decoded
    (nocom, nocom1, blocklst) = get_nocom_vars(astr)


    astr = nocom
    st1 = removeblanklines(astr)
    if debug:
        mylib1.write_str2file('nocom2.txt', st1)


    #find the groups and the start object of the group
    #find all the group strings
    groupls = []
    alist = st1.splitlines()
    for element in alist:
        lss = element.split()
        if lss[0].upper() == '\\group'.upper():
            groupls.append(element)


    #find the var just after each item in groupls
    groupstart = []
    for i in range(len(groupls)):
        iindex = alist.index(groupls[i])
        groupstart.append([alist[iindex], alist[iindex+1]])

    #remove the group commentline
    for element in groupls:
        alist.remove(element)

    if debug:
        st1 = '\n'.join(alist)
        mylib1.write_str2file('nocom3.txt', st1)

    #strip each line
    for i in range(len(alist)):
        alist[i] = alist[i].strip()

    if debug:
        st1 = '\n'.join(alist)
        mylib1.write_str2file('nocom4.txt', st1)

    #ensure that each line is a comment or variable
    #find lines that don't start with a comment
    #if this line has a comment in it
    #   then move the comment to a new line below
    lss = []
    for i in range(len(alist)):
        #find lines that don't start with a comment
        if alist[i][0] != '\\':
            #if this line has a comment in it
            pnt = alist[i].find('\\')
            if pnt != -1:
                #then move the comment to a new line below
                lss.append(alist[i][:pnt].strip())
                lss.append(alist[i][pnt:].strip())
            else:
                lss.append(alist[i])
        else:
            lss.append(alist[i])


    alist = lss[:]
    if debug:
        st1 = '\n'.join(alist)
        mylib1.write_str2file('nocom5.txt', st1)

    #need to make sure that each line has only one variable - as in WindowGlassSpectralData,
    lss = []
    for element in alist:
        # if the line is not a comment
        if element[0] != '\\':
            #test for more than one var
            llist = element.split(',')
            if llist[-1] == '':
                tmp = llist.pop()
            for elm in llist:
                if elm[-1] == ';':
                    lss.append(elm.strip())
                else:
                    lss.append((elm+',').strip())
        else:
            lss.append(element)

    ls_debug = alist[:] # needed for the next debug - 'nocom7.txt'
    alist = lss[:]
    if debug:
        st1 = '\n'.join(alist)
        mylib1.write_str2file('nocom6.txt', st1)

    if debug:
        #need to make sure that each line has only one variable - as in WindowGlassSpectralData,
        #this is same as above.
        # but the variables are put in without the ';' and ','
        #so we can do a diff between 'nocom7.txt' and 'nocom8.txt'. Should be identical
        lss_debug = []
        for element in ls_debug:
            # if the line is not a comment
            if element[0] != '\\':
                #test for more than one var
                llist = element.split(',')
                if llist[-1] == '':
                    tmp = llist.pop()
                for elm in llist:
                    if elm[-1] == ';':
                        lss_debug.append(elm[:-1].strip())
                    else:
                        lss_debug.append((elm).strip())
            else:
                lss_debug.append(element)

        ls_debug = lss_debug[:]
        st1 = '\n'.join(ls_debug)
        mylib1.write_str2file('nocom7.txt', st1)


    #replace each var with '=====var======'
    #join into a string,
    #split using '=====var====='
    for i in range(len(lss)):
        #if the line is not a comment
        if lss[i][0] != '\\':
            lss[i] = '=====var====='

    st2 = '\n'.join(lss)
    lss = st2.split('=====var=====\n')
    lss.pop(0) # the above split generates an extra item at start

    if debug:
        fname = 'nocom8.txt'
        fhandle = open(fname, 'wb')
        k = 0
        for i in range(len(blocklst)):
            for j in range(len(blocklst[i])):
                atxt = blocklst[i][j]+'\n'
                fhandle.write(atxt)
                atxt = lss[k]
                fhandle.write(atxt)
                k = k+1

        fhandle.close()

    #map the structure of the comments -(this is 'lss' now) to
    #the structure of blocklst - blocklst is a nested list
    #make lss a similar nested list
    k = 0
    lst = []
    for i in range(len(blocklst)):
        lst.append([])
        for j in range(len(blocklst[i])):
            lst[i].append(lss[k])
            k = k+1


    if debug:
        fname = 'nocom9.txt'
        fhandle = open(fname, 'wb')
        k = 0
        for i in range(len(blocklst)):
            for j in range(len(blocklst[i])):
                atxt = blocklst[i][j]+'\n'
                fhandle.write(atxt)
                fhandle.write(lst[i][j])
                k = k+1

        fhandle.close()



    #break up multiple line comment so that it is a list
    for i in range(len(lst)):
        for j in range(len(lst[i])):
            lst[i][j] = lst[i][j].splitlines()
            # remove the '\'
            for k in range(len(lst[i][j])):
                lst[i][j][k] = lst[i][j][k][1:]
    commlst = lst


    #copied with minor modifications from readidd2_2.py -- which has been erased ha !
    clist = lst
    lss = []
    for i in range(0, len(clist)):
        alist = []
        for j in range(0, len(clist[i])):
            itt = clist[i][j]
            ddtt = {}
            for element in itt:
                if len(element.split()) == 0:
                    break
                ddtt[element.split()[0].lower()] = []

            for element in itt:
                if len(element.split()) == 0:
                    break
                # ddtt[element.split()[0].lower()].append(string.join(element.split()[1:]))
                ddtt[element.split()[0].lower()].append(' '.join(element.split()[1:]))


            alist.append(ddtt)

        lss.append(alist)
    commdct = lss

    return blocklst, commlst, commdct


def getobjectref(blocklst, commdct):
    """
    makes a dictionary of object-lists
    each item in the dictionary points to a list of tuples
    the tuple is (objectname,  fieldindex)
    """
    objlst_dct = {}
    for eli in commdct:
        for elj in eli:
            if elj.has_key('object-list'):
                objlist = elj['object-list'][0]
                objlst_dct[objlist] = []

    for objlist in objlst_dct.keys():
        for i in range(len(commdct)):
            for j in range(len(commdct[i])):
                if commdct[i][j].has_key('reference'):
                    for ref in commdct[i][j]['reference']:
                        if ref == objlist:
                            objlst_dct[objlist].append((blocklst[i][0], j))
    return objlst_dct

