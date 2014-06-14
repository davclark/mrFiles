#!/usr/bin/python

from pytables import *
from tables import *

# So, MATLAB's reading of a VLArray is at best clunky - you end up with a cell
# array of h5array objects - all the same type.  You'd have to assemble them by
# hand.
roi_data = UInt16Atom(shape=3, flavor="numpy")
roi_data
rt_file = openFile('roi_test1.h5', mode='w')
vlarray = rt_file.createVLArray(rt_file.root, 'roi_vlarray', roi_data)
test = test.reshape(20,3)
vlarray.append(test)
vlarray.append(test[0:10,])
vlarray.append(test[0:10:2,])

# Note - may eventually want to index on name?
# In reading these - MATLAB keeps the strings justified to the full width - so
# somewhere some spaces are sneaking in.
class ROI(IsDescription):
    color = StringCol(2)
    name = StringCol(8)
    viewType = StringCol(10)

table = rt_file.createTable(rt_file.root, 'ROI_metadata', ROI, "Test for ROI file")

# The following doesn't maintain the previous values for the row once it's
# appended!  I guess you're supposed to do this via the default mechanism or
# something...
roi_row = table.row
roi_row['color'] = 'b'
roi_row['name'] = 'LIPC'
roi_row['viewType'] = 'Inplane'
roi_row.append()
roi_row['name'] = 'IFG'
roi_row.append()
roi_row['name'] = 'VLPFC'
roi_row.append()

