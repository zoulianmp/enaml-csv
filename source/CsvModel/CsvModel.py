#!/usr/bin/env python

import numpy as np
import csv
from traits.api import (
    File, HasTraits, Array, List, Instance, Function, Int, Float, Bool, Dict,
    String
)
from enaml.stdlib.table_model import TableModel
from enaml.core.item_model import AbstractItemModel
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
from pandas import DataFrame
from statsmodels.api import OLS


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
    
    # An sklearn.decomposition.PCA object, required for the
    # reduced-dimensionality plots
    pca = Instance(PCA)
    
    # Default row to be plotted in the histogram
    hist_row_index = Int(2)
    
    # Defulat number of bins for the histogram
    hist_nbins = Int(10)
    
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
    
    # chaco.api.ArrayPlotData instance for the image plot
    img_plotdata = Instance(ArrayPlotData,())
    
    # chaco.api.plot instance for the image plot
    image_plot = Instance(Plot,())
    
    # chaco.api.ArrayPlotData instance for the PCA plot
    pca_plotdata = Instance(ArrayPlotData,())
    
    # chaco.api.plot instance for the pca plot
    pca_plot = Instance(Plot,()) 
    
    # chaco.api.ArrayPlotData instance for the histogram
    hist_plotdata = Instance(ArrayPlotData,())
    
    # chaco.api.plot instance for the histogram
    hist_plot = Instance(Plot,())
    
    # class for handling scripts
    script_handler = Instance(ScriptHandler())
    
    # class for handling the workspace generated by the script
    workspace_handler = Instance(WorkspaceHandler,())
    
    # Class for handling selections from the TableView
    selection_handler = Instance(SelectionHandler)
    
    # If the file should be imported as a Pandas dataframe
    AS_PANDAS_DATAFRAME = Bool
    
    def __init__(self):
        '''
        So far only the PCA objects and the XY plot container needs to be 'initialized'.
        '''
        
        self.pca = PCA(n_components=2)
        self.pca.whiten = True
        self.script_handler = ScriptHandler()
        self.workspace_handler = WorkspaceHandler({})
        self.selection_handler = SelectionHandler()
    
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
        
        tblmodel =TableModel(self.table, editable=True)
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
            # currently works only for a single column
            column = self.selection_handler.selected_indices[0][1]
            column_name = self.data_frame.columns[column]
            self.column_length = len(self.data_frame[column_name])
            self.unique_items_nos = len(self.data_frame[column_name].unique())
        
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
        
        for key in var_dict:
            
            top_left = var_dict[key][0]
            exec('top_left='+top_left)
            
            
            bot_right = var_dict[key][1]
            exec('bot_right='+bot_right)
            
            
            x = self.table[top_left[0]:bot_right[0]+1,
                           top_left[1]:bot_right[1]+1]
            print x
            self.script_handler.my_locals[key] = x
            
    
    
def create_array(data, tuple_list):
    x_ = np.empty((0,))
    for index in tuple_list:
        x = data[index[0]:index[2],index[1]:index[3]]
        x_ = np.hstack((x_,x.reshape((1,x.size))))
    return x_.var(), x_.std(), x_.sum(), x_.mean()
