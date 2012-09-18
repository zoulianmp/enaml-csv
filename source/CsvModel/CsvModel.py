#!/usr/bin/env python

import os
import numpy as np
import csv
from traits.api import (
    File, HasTraits, Array, List, Instance, Function, Int, Float, Bool, Dict,
    String
)
from enaml.stdlib.table_model import TableModel
from enaml.core.item_model import AbstractItemModel
from enaml.noncomponents.abstract_icon import AbstractTkIcon
from enaml.backends.qt.noncomponents.qt_icon import QtIcon
from enaml.backends.wx.noncomponents.wx_icon import WXIcon
from enaml.core.item_model import ModelIndex
from chaco.api import Plot, ArrayPlotData, marker_trait, OverlayPlotContainer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from selection_handler import SelectionHandler
from script_handler import ScriptHandler
from workspace_handler import WorkspaceHandler
from enable.api import ColorTrait
from traitsui.api import View, Item
from pandas.io.parsers import read_csv
from enaml_item_models import DataFrameModel
from enaml.styling.font import Font
from pandas import DataFrame
from statsmodels.api import OLS
from scipy.io import loadmat, savemat

def my_font_func(a,b,c):
    return Font().from_string('monospace 10')




class MyTableModel(AbstractItemModel):
    def font(self, index):
        return 'times 10'

class CsvModel(HasTraits):
    '''
    The object that is passed to the MainWindow of the enaml view. This
    represents a general model for different plots in the csv editor.
    '''
    
    
    # The pandas data frame associated with the current instance of the editor.
    data_frame = Instance(DataFrame,())
    
    # Lenght of the selected column
    column_length = Int
    
    # Number of unique items in a selection
    unique_items_nos = Int
    
    # the unique mapping from a list of items to a list of integers
    unique_map = Dict

    # The .csv file to be opened.
    filename = File
    
    # The filename of the file to be saved
    save_filename = String
    
    # The numpy array associated with the data in the file
    table = Array
    
    # The headers of the csv data
    headers = List
    
    # The mean of the 2-D block of the array, represented by the current
    # selection
    selection_mean = Float
    
    # The variance of the 2-D block of the array, represented by the current
    # selection
    selection_var = Float
    
    # The standard deviation of the 2-D block of the array, represented by the
    # current selection
    selection_std = Float
    
    # The sum of the current selection
    selection_sum = Float
    
    # The minimum value from the current selection
    selection_min = Float
    
    # The maximum value from the current selection
    selection_max = Float
    
    # The covariance between a pair of rows or columns
    # NOT IMPLEMENTED
    selection_cov = Float(0)
    
    # The TableModel instance to be passed to the item_model attribute of the
    # TableView
    table_model = Instance(TableModel,())
    
    # class for handling scripts
    script_handler = Instance(ScriptHandler())
    
    # class for handling the workspace generated by the script
    workspace_handler = Instance(WorkspaceHandler,())
    
    # Class for handling selections from the TableView
    selection_handler = Instance(SelectionHandler)
    
    # If the file should be imported as a Pandas dataframe
    AS_PANDAS_DATAFRAME = Bool
    
    # Dict containing icons
    icons_dict = Dict
    
    
    def __init__(self, data=None, AS_PANDAS_DATAFRAME=False):
        
        if AS_PANDAS_DATAFRAME:
            self.AS_PANDAS_DATAFRAME = AS_PANDAS_DATAFRAME
        if data is not None:
            if self.AS_PANDAS_DATAFRAME:
                self.data_frame = data
            else:
                self.table = data
        self.pca = PCA(n_components=2)
        self.pca.whiten = True
        self.script_handler = ScriptHandler()
        self.workspace_handler = WorkspaceHandler({})
        self.selection_handler = SelectionHandler()
        
        left_icon = QtIcon().from_file(
            os.path.join('..','Icons','left.gif'))
        self.icons_dict['left'] = left_icon
        
        right_icon = QtIcon().from_file(
            os.path.join('..','Icons','right.gif'))
        self.icons_dict['right'] = right_icon
        
        delete_icon = QtIcon().from_file(
            os.path.join('..','Icons','cross.gif')
        )
        self.icons_dict['delete'] = delete_icon
        
        load_icon = QtIcon().from_file(
            os.path.join('..','Icons','load.png')
        )
        self.icons_dict['load'] = load_icon
        
        save_icon = QtIcon().from_file(
            os.path.join('..','Icons','save.png')
        )
        self.icons_dict['save'] = save_icon
        
        run_icon = QtIcon().from_file(
            os.path.join('..','Icons','run.png')
        )
        self.icons_dict['run'] = run_icon
        
        up_icon = QtIcon().from_file(
            os.path.join('..','Icons','up.png')
        )
        self.icons_dict['up'] = up_icon
        
        down_icon = QtIcon().from_file(
            os.path.join('..','Icons','down.png')
        )
        self.icons_dict['down'] = down_icon
        
        bold_icon = QtIcon().from_file(
            os.path.join('..','Icons','bold.png')
        )
        self.icons_dict['bold'] = bold_icon
        
        under_icon = QtIcon().from_file(
            os.path.join('..','Icons','under.png')
        )
        self.icons_dict['under'] = under_icon
        
        italic_icon = QtIcon().from_file(
            os.path.join('..','Icons','italic.png')
        )
        self.icons_dict['italic'] = italic_icon
        
        cut_icon = QtIcon().from_file(
            os.path.join('..','Icons','cut.png')
        )
        self.icons_dict['cut'] = cut_icon
        
        copy_icon = QtIcon().from_file(
            os.path.join('..','Icons','copy.gif')
        )
        self.icons_dict['copy'] = copy_icon
        
        paste_icon = QtIcon().from_file(
            os.path.join('..','Icons','paste.png')
        )
        self.icons_dict['paste'] = paste_icon
        
        undo_icon = QtIcon().from_file(
            os.path.join('..','Icons','undo.png')
        )
        self.icons_dict['undo'] = undo_icon
        
        redo_icon = QtIcon().from_file(
            os.path.join('..','Icons','redo.png')
        )
        self.icons_dict['redo'] = redo_icon
        
        navigator_icon = QtIcon().from_file(
            os.path.join('..','Icons','navigator.png')
        )
        self.icons_dict['navigator'] = navigator_icon
        
        indent_icon = QtIcon().from_file(
            os.path.join('..','Icons','indent.png')
        )
        self.icons_dict['indent'] = indent_icon
        
        dedent_icon = QtIcon().from_file(
            os.path.join('..','Icons','dedent.png')
        )
        self.icons_dict['dedent'] = dedent_icon
    
    def _table_default(self):
        '''
        The default array in the TableView is a 100x100 array of zeros
        '''
        
        x = np.zeros((100,100))
        return x
    
    def _table_model_default(self):
        '''
        The default TableModel instance corresponding to the array of zeros
        '''
        
        tblmodel =TableModel(self.table, editable=True, font_func=my_font_func)
        return tblmodel
    
    def _image_plot_default(self):
        '''
        Default chaco plot object for the image plot.
        '''
        
        self.img_plotdata = ArrayPlotData(imagedata=self.table)
        p = Plot(self.img_plotdata)
        p.img_plot('imagedata')
        return p
    
    def _hist_plot_default(self):
        '''
        Default chaco plot object for the histogram.
        '''
        
        h = np.histogram(self.table,10)[0]
        self.hist_plotdata = ArrayPlotData(x=h)
        p = Plot(self.hist_plotdata)
        p.plot('x',type='bar',color='auto',bar_width=0.3)
        return p
    
    def _filename_changed(self, new):
        '''
        Executes whenever a file is loaded into the view.
        '''
        if self.AS_PANDAS_DATAFRAME:
            self.data_frame = read_csv(self.filename)
            self.table_model = DataFrameModel(
                self.data_frame,
                editable=True,
                horizontal_headers=self.data_frame.columns,
            )
        else:
            self.table = np.genfromtxt(self.filename, delimiter=',', skip_header=1)
            csv_reader= csv.reader(file(self.filename))
            self.headers = csv_reader.next()
            del csv_reader
            self.table_model = TableModel(self.table, editable=True,
                                     horizontal_headers=self.headers)
    
    
    def redraw_tablemodel(self):
        if self.AS_PANDAS_DATAFRAME:
            self.table_model = DataFrameModel(
                self.data_frame, editable= True,
                horizontal_headers=self.data_frame.columns
            )
        else:
            self.table_model = TableModel(self.table, editable=True,
                                          horizontal_headers=self.headers)
    
    def create_plot_properties():
        pass
    
    
    def use_selection_preview(self):
        pass
    
    
    def use_selection_histogram(self):
        pass
    
    def use_selection_imageplot(self):
        pass
    
    def use_selection_pcaplot(self):
        pass
    
    def calculate_selection_params(self):
        
        '''
        Called to calculate statistics of a selection.
        '''
        self.selection_handler.create_selection()
        tuple_list = self.selection_handler.selected_indices

        if self.AS_PANDAS_DATAFRAME:
            if len(tuple_list)==1:
                # works for one column name
                column_name = self.data_frame.columns[tuple_list[0][1]]
                t = self.data_frame[column_name]
                
                
        else:
            
            if len(tuple_list) == 1:
                if tuple_list[0][1]==tuple_list[0][3]:
                    t = self.table[tuple_list[0][0]:tuple_list[0][2],
                                   tuple_list[0][3]]
                elif tuple_list[0][0]==tuple_list[0][2]:
                    t = self.table[tuple_list[0],
                                   tuple_list[0][1]:tuple_list[3]]
                t.reshape((1,t.size))
                for index in tuple_list[1:len(tuple_list)-1]:
                    x = self.table[index[0]:index[2],index[1]:index[3]]
                    t = np.hstack((t,x.reshape((1,x.size))))

        self.selection_mean = t.mean()
        self.selection_std = t.std()
        self.selection_var = t.var()
        self.selection_sum = t.sum()
        self.selection_max = np.amax(t)
        self.selection_min = np.amin(t)
        
        
        self.selection_handler.flush()
    
    def create_pandas_dataframe(self):
        pass
    
    def string_ops(self):
        '''
        Perform trivial ops on a column of the data frame.
        '''
        self.selection_handler.create_selection()
        
        if len(self.selection_handler.selected_indices)==1:
            column = self.selection_handler.selected_indices[0][1]
            # currently works only for a single column
            if self.AS_PANDAS_DATAFRAME:                
                column_name = self.data_frame.columns[column]
                self.column_length = len(self.data_frame[column_name])
                self.unique_items_nos = len(self.data_frame[column_name].unique())
            else:
                self.column_length = len(self.table[:,column])
                self.unique_items_nos = len(np.unique(self.table[:,column]))
        
        self.selection_handler.flush()
    
    def map_to_unique(self):
        '''
        USed to map a set of items onto unique integers,
        and change tabular display accordingly.
        '''
        self.selection_handler.create_selection()
        
        if len(self.selection_handler.selected_indices)==1:
            # currently works only for a single coulmn
            self.unique_map = {}
            column = self.selection_handler.selected_indices[0][1]
            column_name = self.data_frame.columns[column]
            data = self.data_frame[column_name]
            m = 0
            index = 0
            for item in data:
                if item not in self.unique_map.keys():
                    self.unique_map[item]=m
                    m+=1
            for item in data:
                self.data_frame[column_name][index]=self.unique_map[item]
                index +=1
            self.table_model = DataFrameModel(
                self.data_frame,
                editable=True,
                horizontal_headers=self.data_frame.columns,
            )
            
            
        self.selection_handler.flush()
    
    def save_as(self):
        '''
        Save the current table as a csv file
        '''
        
        if self.AS_PANDAS_DATAFRAME:
            self.data_frame.to_csv(self.save_filename,index=False)
            
        else:
            # add file writing script for a numpy array
            pass
        
    
    def normalize_selection(self):
        '''
        Normalize the current selection.
        '''
        self.selection_handler.create_selection()
        if len(self.selection_handler.selected_indices)==1:
            column_index = self.selection_handler.selected_indices[0][1]
            if self.AS_PANDAS_DATAFRAME:
                column_name = self.data_frame.columns[column_index]
                x = self.data_frame[column_name]
                x = x - x.mean()
                x = x/x.std()
                self.data_frame[column_name]=x
                self.table_model = DataFrameModel(
                    self.data_frame,
                    editable=True,
                    horizontal_headers=self.data_frame.columns
                )
            else:
                x = self.table[:,column_index]
                x = x - x.mean()
                x = x/x.std()
                self.table[:,column_index] = x
                self.table_model = TableModel(self.table, editable=True,
                                              horizontal_headers=self.headers)
        self.selection_handler.flush()

    
    def add_uservariables(self, var_dict):
        '''
        Used to add variables selected from the tabular view and named by
        the user to the local workspace. These variables are identifiable by
        their user given names in the script.
        '''
        
        for key in var_dict:
            
            top_left = var_dict[key][0]
            exec('top_left='+top_left)
            
            
            bot_right = var_dict[key][1]
            exec('bot_right='+bot_right)
            
            
            x = self.table[top_left[0]:bot_right[0]+1,
                           top_left[1]:bot_right[1]+1]
            
            self.script_handler.my_locals[key] = x
            
    
    def delete_rowcol(self):
        '''
        Called to delete columns from the pandas dataframe
        '''
        self.selection_handler.create_selection()
        
        to_remove = []        
        for index in self.selection_handler.selected_indices:
            column_name = self.data_frame.columns[index[1]]
            to_remove.append(column_name)
        for column_name in to_remove:
            del self.data_frame[column_name]
        
        self.redraw_tablemodel()
        self.selection_handler.flush()
    
    def shift_selection(self, what, where):
        '''
        Called to shift a column to the left or to the right
        '''
        # currently works only for pandas dataframes
        if self.AS_PANDAS_DATAFRAME:
            if what == 'column':
            
                self.selection_handler.create_selection()
                column_list = list(self.data_frame.columns)
                selected_column_index = self.selection_handler.selected_indices[0][1]
                selected_column = column_list.pop(selected_column_index)
                if where == 'left':
                    to_insert_index = selected_column_index - 1
                else:
                    to_insert_index = selected_column_index + 1
                column_list.insert(to_insert_index, selected_column)
                self.data_frame = self.data_frame.reindex(columns = column_list)
        
        
            elif what == 'row':
        
                self.selection_handler.create_selection()
                index = self.selection_handler.selected_indices[0][0]
                row_list = list(self.data_frame.index)
                selected_row = row_list.pop(index)
                if where == 'up':
                    to_insert_index = index - 1
                else:
                    to_insert_index = index + 1
                row_list.insert(to_insert_index, selected_row)
                self.data_frame = self.data_frame.reindex(index=row_list)
        
            self.redraw_tablemodel()        
        
        self.selection_handler.flush()
    
    def sort_selection(self, sort_type):
        '''
        Called to sort the selected column
        '''
        # currently works only for pandas dataframes
        
        self.table_model.begin_change_layout()
        
        if self.AS_PANDAS_DATAFRAME:
            self.selection_handler.create_selection()
            column_index = self.selection_handler.selected_indices[0][1]
            column_name = self.data_frame.columns[column_index]
            column = self.data_frame[column_name].copy()
            if sort_type == 0:
                column = column.order()
                
            else:
                column = column.order(ascending=False)
            
            del self.data_frame[column_name]
            self.data_frame[column_name] = list(column)
                
            
        self.table_model.end_change_layout()
        
        self.redraw_tablemodel()
        
        
        
        self.selection_handler.flush()
    
    def add_row_col(self, selected_label):
        
        self.selection_handler.create_selection()
        selected_index = self.selection_handler.selected_indices[0][0]
        var_name = self.workspace_handler.workspace.keys()[selected_index]
        data = self.workspace_handler.workspace[var_name]

        if selected_label == 'As Row':
            if self.AS_PANDAS_DATAFRAME:
                if data.shape[1] == self.data_frame.shape[1]:
                    self.data_frame = self.data_frame.append(data)
                    print self.data_frame.shape
            else:
                if data.shape[1] == self.table.shape[1]:
                    self.table = np.vstack((self.table, data))
        else :
            
            if self.AS_PANDAS_DATAFRAME:
                if data.shape[0] == self.data_frame.shape[0]:
                    self.data_frame[var_name] = data
                    print self.data_frame.shape
            else:
                if data.shape[0] == self.table.shape[0]:
                    self.table = np.hstack((self.table, data))
        
        self.headers.append(var_name)        
        self.selection_handler.flush()
        self.redraw_tablemodel()
        
    
    def set_table_selection(self, row, col):
        '''
        
        '''
        none_types = [' ', 'None']
        
        
        
        if self.AS_PANDAS_DATAFRAME:
            data = self.data_frame
        else:
            data = self.table
        print row, col
        if (row in none_types) and (col not in none_types):
            top_left = (0, int(col))
            bot_right = (data.shape[0], int(col))
        elif (row not in none_types) and (col in none_types):
            top_left = (int(row), 0)
            bot_right = (int(row), data.shape[1])
        
        top_left_mi = self.table_model.create_index(row=top_left[0],
                                                    column=top_left[1],
                                                    context=None)
        bot_right_mi = self.table_model.create_index(row=bot_right[0],
                                                    column=bot_right[1],
                                                    context=None)
        
        return [(top_left_mi, bot_right_mi)]
    
    def increase_indent(self, selection):
        t = selection.split('\n')
        indented = ''
        for elem in t:
            elem = '    '+elem+'\n'
            indented = indented + elem
        indented = indented.rstrip()
        return indented
    
    def decrease_indent(self, selection):
        pass
    
    def remove_workspace_selection(self):
        pass
    
    def save_workspace(self, file_path):
        to_save = {}
        for elem in self.workspace_handler.workspace:
            obj = self.workspace_handler.workspace[elem]
            if isinstance(obj, np.ndarray):
                to_save[elem] = obj
        if len(to_save)>0:
            savemat(file_path, to_save)
    
    def load_workspace(self, file_path):
        loaded_workspace = loadmat(file_path)
        for elem in loaded_workspace:
            self.workspace_handler.workspace[elem] = loaded_workspace[elem]
        self.script_handler.my_locals = self.workspace_handler.workspace

