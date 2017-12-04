# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 11:13:54 2017

@author: justintran
"""
from webscrape import getData
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

court_shapes = []

outer_lines_shape = dict(
  type='rect',
  xref='x',
  yref='y',
  x0='-250',
  y0='-47.5',
  x1='250',
  y1='422.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(outer_lines_shape)

hoop_shape = dict(
  type='circle',
  xref='x',
  yref='y',
  x0='7.5',
  y0='7.5',
  x1='-7.5',
  y1='-7.5',
  line=dict(
    color='rgba(10, 10, 10, 1)',
    width=1
  )
)

court_shapes.append(hoop_shape)
backboard_shape = dict(
  type='rect',
  xref='x',
  yref='y',
  x0='-30',
  y0='-7.5',
  x1='30',
  y1='-6.5',
  line=dict(
    color='rgba(10, 10, 10, 1)',
    width=1
  ),
  fillcolor='rgba(10, 10, 10, 1)'
)

court_shapes.append(backboard_shape)

outer_three_sec_shape = dict(
  type='rect',
  xref='x',
  yref='y',
  x0='-80',
  y0='-47.5',
  x1='80',
  y1='143.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(outer_three_sec_shape)

inner_three_sec_shape = dict(
  type='rect',
  xref='x',
  yref='y',
  x0='-60',
  y0='-47.5',
  x1='60',
  y1='143.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(inner_three_sec_shape)

left_line_shape = dict(
  type='line',
  xref='x',
  yref='y',
  x0='-220',
  y0='-47.5',
  x1='-220',
  y1='92.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(left_line_shape)

right_line_shape = dict(
  type='line',
  xref='x',
  yref='y',
  x0='220',
  y0='-47.5',
  x1='220',
  y1='92.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(right_line_shape)

three_point_arc_shape = dict(
  type='path',
  xref='x',
  yref='y',
  path='M -220 92.5 C -70 300, 70 300, 220 92.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(three_point_arc_shape)

center_circle_shape = dict(
  type='circle',
  xref='x',
  yref='y',
  x0='60',
  y0='482.5',
  x1='-60',
  y1='362.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(center_circle_shape)

res_circle_shape = dict(
  type='circle',
  xref='x',
  yref='y',
  x0='20',
  y0='442.5',
  x1='-20',
  y1='402.5',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(res_circle_shape)

free_throw_circle_shape = dict(
  type='circle',
  xref='x',
  yref='y',
  x0='60',
  y0='200',
  x1='-60',
  y1='80',
  line=dict(
      color='rgba(10, 10, 10, 1)',
      width=1
  )
)

court_shapes.append(free_throw_circle_shape)

res_area_shape = dict(
  type='circle',
  xref='x',
  yref='y',
  x0='40',
  y0='40',
  x1='-40',
  y1='-40',
  line=dict(
    color='rgba(10, 10, 10, 1)',
    width=1,
    dash='dot'
  )
)
 
court_shapes.append(res_area_shape)



def getShotChart(name, season):
  shot_df = getData(name, 'ShotLog', season)

  missed_shot_trace = go.Scatter (
    x = shot_df[shot_df['EVENT_TYPE'] == 'Missed Shot']['LOC_X'],
    y = shot_df[shot_df['EVENT_TYPE'] == 'Missed Shot']['LOC_Y'],
    mode = 'markers',
    name = 'Missed Shot',
    marker = dict(
      size = 5,
      color = 'rgba(255, 255, 0, .8)',
      line = dict(
        width = 1,
        color = 'rgb(0,0,0,1)'
        )
      )
    )

  made_shot_trace = go.Scatter (
    x = shot_df[shot_df['EVENT_TYPE'] == 'Made Shot']['LOC_X'],
    y = shot_df[shot_df['EVENT_TYPE'] == 'Made Shot']['LOC_Y'],
    mode = 'markers',
    name = 'Made Shot',
    marker = dict(
      size = 5,
      color = 'rgba(0,200,100,.8)',
      line = dict(
        width = 1,
        color = 'rgb(0,0,0,1)'
        )
      )
    )

  data = [missed_shot_trace, made_shot_trace]

  layout = go.Layout(
    title = 'Shots by ' + name.title() + ' in ' + season + '-' + str(int(season[-2:])+1),
    showlegend=True,
    xaxis=dict(
      showgrid=False,
      range=[-300,300]
      ),
    yaxis=dict(
      showgrid=False,
      range=[-100,500]
      ),
    height=600,
    width=650,
    shapes=court_shapes
  )

  fig = go.Figure(data=data, layout=layout)
  return plot(fig)