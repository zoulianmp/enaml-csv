from traits.api import HasTraits, Bool, Instance, Int, Array, List,Dict
from traitsui.api import View, Item
from chaco.api import (
    Plot, ArrayPlotData, OverlayPlotContainer, marker_trait, PlotGrid,
    Legend
)

from enable.api import ColorTrait
from selection_handler import SelectionHandler


class XYPlotHandler(HasTraits):
    '''
    Class for handling XY plots
    '''
    
    # The container for all current plots. Gets updated everytime a plot is
    # added.
    container = OverlayPlotContainer
    
    # This can be removed.
    plotdata = ArrayPlotData
    
    # The current Plot object.
    plot = Plot
    
    # ColorTrait, mainly required for the TraitsUIItem view.
    color = ColorTrait("blue")
    
    # Marker trait for the view
    marker = marker_trait
    
    # Marker size trait
    marker_size = Int(4)
    
    # An instance of SelectionHandler for adding plots from the current
    # selection.
    selection_handler = Instance(SelectionHandler)
    
    # Bool traits for checking the type of the plot (discrete / continuous)
    plot_type_disc = Bool
    plot_type_cont = Bool
    
    # The data from which to draw the plots, same as the table attribute of
    # CsvModel
    table = Array
    
    # Contains the grid underlays of all the current plots
    grid_underlays = List
    
    # Used for viewing the list of the plots and the legend
    plot_list_view = Dict
    
    # TraitsUI view for plot properties, yet to find an enaml implementation
    view = View(
        Item('color'),
        Item('marker'),
        Item('marker_size')
    )
    
    def __init__(self):
        self.selection_handler = SelectionHandler()
        self.container = OverlayPlotContainer()
        self.underlays = []
    
    
    def add_xyplot_selection(self,plot_name):
        '''
        Called when the 'add plot from selection button is clicked.'
        '''
        if self.selection_handler.xyplot_check():
            self.plotdata = ArrayPlotData(
                x=self.table[:,self.selection_handler.selected_indices[0][1]],
                y=self.table[:,self.selection_handler.selected_indices[1][1]]
            )
            
            plot = Plot(self.plotdata)
            
            if self.plot_type_disc:
                plot_type = 'scatter'
            else:
                plot_type = 'line'
            plot.plot(
                ("x","y"),type = plot_type,
                color = self.color,
                marker = self.marker,
                marker_size = self.marker_size
            )
            
            self.plot = plot
            
            for underlay in self.plot.underlays:
                if isinstance(underlay, PlotGrid):
                    if underlay not in self.grid_underlays:
                        self.grid_underlays.append(underlay)
            
            if plot_name == '':
                self.plot_list_view['plot'+str(len(self.plot_list_view))]=self.plot
            else:
                self.plot_list_view[plot_name]=self.plot
            self.container.add(self.plot)

            self.container.request_redraw()
            
        self.selection_handler.flush()

    def grid_toggle(self, checked):
        '''
        Called when the 'Show Grid' checkbox ins toggled
        '''
        if not checked:
            for plot in self.container.components:
                for underlay in self.grid_underlays:
                    if underlay in plot.underlays:
                        plot.underlays.remove(underlay)
        else:
            for plot in self.container.components:
                for underlay in self.grid_underlays:
                    if underlay not in plot.underlays:
                        plot.underlays.append(underlay)
        self.container.request_redraw()
    
    def remove_selected_plots(self,selection):
        remove_indices = []
        for model_index in selection:
            remove_indices.append(model_index[0].row)
        remove_plots = []
        for index in remove_indices:
            remove_plots.append(self.plot_list_view.keys()[index])
        
        removed_plots = []
        for plot in remove_plots:
            removed_plots.append(self.plot_list_view.pop(plot))
        for plot in self.container.components:
            self.container.remove(plot)
        for plot in self.plot_list_view.keys():
            self.container.add(self.plot_list_view[plot])
        self.container.request_redraw()