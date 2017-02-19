#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle UI
"""
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models import HBox
from bokeh.models.widgets import Panel, Tabs, Select
from bokeh.io import output_file, show
from bokeh.plotting import figure

from data import PinnakisaData


kisa = PinnakisaData()
kisa.read_contest_data('3778f94604f8dd433ed80bbf63042198abd0cbea')

xx, yy = zip(*kisa.get_species_cumulation('CORRAX', date(2017, 1, 1), date(2017, 2, 28)))

xx = list(xx)  # TODO: Use this
yy = list(yy)

output_file("index.html")

p1 = figure(plot_width=800, plot_height=400)
p1.line(range(len(yy)), yy, line_width=3,  color="navy", alpha=0.5)

select = Select(title="Option:", value="CORRAX", options=["CORRAX", "FRICOE", "COLOEN", "CLAHYE"])

layout = HBox(widgetbox(select), p1)
tab1 = Panel(child=layout, title="Laji")

p2 = figure(plot_width=800, plot_height=400)
p2.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)
tab2 = Panel(child=p2, title="Päivä")

tabs = Tabs(tabs=[tab1, tab2])

show(tabs)
