#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Handle UI
"""
# TODO: Switch to use pandas
# TODO: Fix UI timezone problem
# TODO: Refactor

import numpy as np
from bokeh.io import output_file, save
from bokeh.layouts import widgetbox
from bokeh.models import HBox, CustomJS, ColumnDataSource, WidgetBox
from bokeh.models.widgets import Panel, Tabs, Select, DataTable, TableColumn
from bokeh.plotting import figure

from data import PinnakisaData


def daily_ticks_by_species(data_source):
    """
    A line chart visualization of daily ticks by species.

    :param data_source: ColumnDataSource
    :return: Panel
    """
    sp_callback = CustomJS(args=dict(source=data_source), code="""
            var data = source.data;
            var f = cb_obj.value;

            data['ticks'] = data[f];
            source.trigger('change');
        """)

    fig = figure(plot_width=PLOT_WIDTH, plot_height=PLOT_HEIGHT, x_axis_type='datetime',
                 title="Pinnoja lajeittain per päivä")
    fig.line('dates', 'ticks', source=data_source, line_width=3, color="navy", alpha=0.5)

    select = Select(title="Option:", options=['-- Yhteensä --'] + all_species, callback=sp_callback)

    layout = HBox(widgetbox(select), fig)
    return Panel(child=layout, title="Lajit päivittäin")


def daily_most_common_ticks():
    """
    A Table view of the most common ticks per day.

    :return: Panel
    """
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

    return Panel(child=layout, title="Päivien yleisimmät")


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

tab1 = daily_ticks_by_species(ColumnDataSource(species_data))

tab2 = daily_most_common_ticks()

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

tabs = Tabs(tabs=[tab1, tab2])

output_file("index.html")
save(tabs)
