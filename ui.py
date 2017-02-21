#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle UI
"""
# TODO: Switch to use pandas
# TODO: Fix UI timezone problem
# TODO: Refactor

import numpy as np
from bokeh.layouts import widgetbox
from bokeh.models import HBox, CustomJS, ColumnDataSource, WidgetBox
from bokeh.models.widgets import Panel, Tabs, Select, DataTable, TableColumn
from bokeh.io import output_file, show, save
from bokeh.plotting import figure

from data import PinnakisaData


PLOT_WIDTH = 1100
PLOT_HEIGHT = 700

kisa = PinnakisaData()
kisa.read_contest_data('3778f94604f8dd433ed80bbf63042198abd0cbea')

all_species = kisa.get_all_species()

start_date, end_date = kisa.get_date_limits()

species_data = {}
initial_x = []

totals = []

for species in all_species:
    sp_data = kisa.get_species_cumulation(species, start_date, end_date)
    species_data[species] = [sp[1] for sp in sp_data]
    if not initial_x:
        initial_x, _ = zip(*sp_data)
    if not len(totals):
        totals = np.array(species_data[species])
    else:
        totals += np.array(species_data[species])

species_data['dates'] = initial_x
species_data['ticks'] = totals
species_data['-- Yhteensä --'] = totals


output_file("index.html")

#############

sp_source = ColumnDataSource(species_data)

sp_callback = CustomJS(args=dict(source=sp_source), code="""
        var data = source.data;
        var f = cb_obj.value;

        data['ticks'] = data[f];
        source.trigger('change');
    """)

p1 = figure(plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT, x_axis_type='datetime', title="Pinnoja lajeittain per päivä")
p1.line('dates', 'ticks', source=sp_source, line_width=3,  color="navy", alpha=0.5)

select = Select(title="Option:", options=['-- Yhteensä --'] + all_species, callback=sp_callback)

layout = HBox(widgetbox(select), p1)
tab1 = Panel(child=layout, title="Lajit päivittäin")

#############

# TODO: Show all ticks for a day as a bar chart
# p2 = figure(plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT, x_axis_type='datetime',
#             title="TODO")
# # p2.line('dates', 'totals', source=sp_source, line_width=3,  color="navy", alpha=0.5)
# p2.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)
# tab2 = Panel(child=p2, title="Päivä")

#############

# TODO: Visualize daily total ticks for each person
# p3 = figure(plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT, title="TODO")
# p3.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)
# tab3 = Panel(child=p3, title="Henkilö")

#############

ticks = kisa.get_daily_popular_ticks(start_date, end_date)
tick_source = {}
# print(ticks)  # TODO: Handle empty species names somewhere
dates, species, count = zip(*((dat, sp[0], sp[1]) for (dat, sp) in ticks))

tick_source['date'] = dates
tick_source['species'] = species
tick_source['count'] = count

tick_source = ColumnDataSource(tick_source)

columns = [TableColumn(field="date", title="Päivämäärä"),
           TableColumn(field="species", title="Päivän yleisin laji"),
           TableColumn(field="count", title="Pinnojen lukumäärä")]
table = DataTable(source=tick_source, columns=columns, width=PLOT_WIDTH, height=PLOT_HEIGHT)
layout = WidgetBox(table)

tab4 = Panel(child=layout, title="Päivien yleisimmät")

#############

tabs = Tabs(tabs=[tab1,  # tab2, tab3,
                  tab4])

save(tabs)
