
import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from app import app

#GRAPH FUNCTIONS
MAIN_COLOUR = "#1F618D"
MIN_COLOUR = "#a7a725"
MAX_COLOUR = "#3b8e1f"
FONT_COLOUR = "#A6ACAF"
FONT_SIZE = 12
TITLE_COLOUR = "#494e50"
TITLE_SIZE = 20

#import data file
df = pd.read_csv("data.csv")

#transform dataframe so that there are three columns for the Month, Year and Avg House Price
df2 = df.melt(id_vars = "Month", value_vars=["2019", "2020", "2021"],
            var_name="Year", value_name="Avg_House_Price")

#now we want to forecast 2021 data for Sep to Dec

###calculate the average house price by month for 2021 and 2020 combined
df_mom_pct_change = df2.loc[df2["Year"].isin(["2019", "2020"])].groupby("Month").agg(Avg_House_Price = ("Avg_House_Price", "mean")).reset_index()

###now calculate the month on month percentage changes
df_mom_pct_change["MoM_Pct_Change"] = df_mom_pct_change["Avg_House_Price"].pct_change()

###calculate each month's mising value for 2021 based on the average MoM pct change of pevious years
df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Sep"), "Avg_House_Price"] = int(df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Aug"), "Avg_House_Price"].tolist()[0] * (1 + df_mom_pct_change.loc[df_mom_pct_change["Month"] == "Sep", "MoM_Pct_Change"].tolist()[0]))
df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Oct"), "Avg_House_Price"] = int(df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Sep"), "Avg_House_Price"].tolist()[0] * (1 + df_mom_pct_change.loc[df_mom_pct_change["Month"] == "Oct", "MoM_Pct_Change"].tolist()[0]))
df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Nov"), "Avg_House_Price"] = int(df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Oct"), "Avg_House_Price"].tolist()[0] * (1 + df_mom_pct_change.loc[df_mom_pct_change["Month"] == "Nov", "MoM_Pct_Change"].tolist()[0]))
df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Dec"), "Avg_House_Price"] = int(df2.loc[(df2["Year"] == "2021") & (df2["Month"] == "Nov"), "Avg_House_Price"].tolist()[0] * (1 + df_mom_pct_change.loc[df_mom_pct_change["Month"] == "Dec", "MoM_Pct_Change"].tolist()[0]))

#now put all forecast values in their own dataframe (inc 1 month previous to forecast so the lines join up)
df_forecast = df2.loc[(df2["Year"] == "2021") & (df2["Month"].isin(["Aug", "Sep", "Oct", "Nov", "Dec"]))].copy()

#and put all the actuals into their own dataframe
df_actuals = df2.loc[~((df2["Year"] == "2021") & (df2["Month"].isin(["Sep", "Oct", "Nov", "Dec"])))].copy()


#create a dataframe containing the year labels
df_line_label = df2.loc[df2["Month"] == "Dec", ["Year", "Avg_House_Price"]].copy()

#create a table containing all actuals and forecast figures
df3 = pd.concat([df_actuals, df_forecast.loc[df_forecast["Month"] != "Aug"]])

#calculate the min and max price for each year
df_min_max = df3.groupby(["Year"]).agg(Min_Price = ("Avg_House_Price", "min"),
                            Max_Price = ("Avg_House_Price", "max")).reset_index()

###now join on the month for the min and max for each year
df_min_max = df_min_max.merge(df3[["Year", "Avg_House_Price", "Month"]], how = "left", left_on = ["Year", "Min_Price"], right_on = ["Year", "Avg_House_Price"])
df_min_max.drop(columns = ["Avg_House_Price"], inplace = True)
df_min_max.rename(columns = {"Month": "Min_Month"}, inplace = True)
df_min_max = df_min_max.merge(df3[["Year", "Avg_House_Price", "Month"]], how = "left", left_on = ["Year", "Max_Price"], right_on = ["Year", "Avg_House_Price"])
df_min_max.drop(columns = ["Avg_House_Price"], inplace = True)
df_min_max.rename(columns = {"Month": "Max_Month"}, inplace = True)

###add in colour for the min max (this colour variable doesn't need to go inside callback because the colour isn't dependent upon the year)
df_min_max["Max_Colour"] = MAX_COLOUR
df_min_max["Min_Colour"] = MIN_COLOUR

#create a dataframe containing the commentary for the visual which will depend upon the year selected
#provide commentary on both the minimum price for the year and the maximum
df_commentary = pd.DataFrame({
    "Year": ["2019", "2019", "2020", "2020", "2021", "2021"],
    "Min_Max": ["Min", "Max", "Min", "Max", "Min", "Max"],
    "Commentary": [
        'The best time to <b><span style="color:' + MIN_COLOUR + '">BUY</span></b> in <span style="color:' + MAIN_COLOUR + '">2019</span> was <span style="color:' + MIN_COLOUR + '">October</span>, <br>houses sold for an average of <span style="color:' + MIN_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2019") & (df_min_max["Min_Month"] == "Oct"), "Min_Price"].tolist()[0])/1000)),
        'The best time to <b><span style="color:' + MAX_COLOUR + '">SELL</span></b> in <span style="color:' + MAIN_COLOUR + '">2019</span> was <span style="color:' + MAX_COLOUR + '">July</span>, <br>houses sold for an average of <span style="color:' + MAX_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2019") & (df_min_max["Max_Month"] == "Jul"), "Max_Price"].tolist()[0])/1000)),
        'The best time to <b><span style="color:' + MIN_COLOUR + '">BUY</span></b> in <span style="color:' + MAIN_COLOUR + '">2020</span> was <span style="color:' + MIN_COLOUR + '">October</span>, <br>houses sold for an average of <span style="color:' + MIN_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2020") & (df_min_max["Min_Month"] == "Oct"), "Min_Price"].tolist()[0])/1000)),
        'The best time to <b><span style="color:' + MAX_COLOUR + '">SELL</span></b> in <span style="color:' + MAIN_COLOUR + '">2020</span> was <span style="color:' + MAX_COLOUR + '">July</span>, <br>houses sold for an average of <span style="color:' + MAX_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2020") & (df_min_max["Max_Month"] == "Jul"), "Max_Price"].tolist()[0])/1000)),
        'The best time to <b><span style="color:' + MIN_COLOUR + '">BUY</span></b> in <span style="color:' + MAIN_COLOUR + '">2021</span> was <span style="color:' + MIN_COLOUR + '">April</span>, <br>houses sold for an average of <span style="color:' + MIN_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2021") & (df_min_max["Min_Month"] == "Apr"), "Min_Price"].tolist()[0])/1000)),
        'The best time to <b><span style="color:' + MAX_COLOUR + '">SELL</span></b> in <span style="color:' + MAIN_COLOUR + '">2021</span> was <span style="color:' + MAX_COLOUR + '">July</span>, <br>houses sold for an average of <span style="color:' + MAX_COLOUR + '">${}k</span>'.format(int((df_min_max.loc[(df_min_max["Year"] == "2021") & (df_min_max["Max_Month"] == "Jul"), "Max_Price"].tolist()[0])/1000)),
    ]
})

###add in the x and y coordinates of where the text will appear for each piece of commentary
df_commentary.loc[df_commentary["Min_Max"] == "Min", "X_Pos"] = 1
df_commentary.loc[df_commentary["Min_Max"] == "Min", "Y_Pos"] = 0.95

df_commentary.loc[df_commentary["Min_Max"] == "Max", "X_Pos"] = 0
df_commentary.loc[df_commentary["Min_Max"] == "Max", "Y_Pos"] = 0.95

###add in a column to contain how the commentary will be aligned
df_commentary.loc[df_commentary["Min_Max"] == "Min", "Align"] = "right"
df_commentary.loc[df_commentary["Min_Max"] == "Max", "Align"] = "left"

#adjust 2021 so the min and max commentary are the opposite sides to the other years
df_commentary.loc[(df_commentary["Min_Max"] == "Min") & (df_commentary["Year"] == "2021"), "X_Pos"] = 0
df_commentary.loc[(df_commentary["Min_Max"] == "Max") & (df_commentary["Year"] == "2021"), "X_Pos"] = 1
df_commentary.loc[(df_commentary["Min_Max"] == "Min") & (df_commentary["Year"] == "2021"), "Align"] = "left"
df_commentary.loc[(df_commentary["Min_Max"] == "Max") & (df_commentary["Year"] == "2021"), "Align"] = "right"

layout = dbc.Container([
    #create a row containing the radio buttons so users can select the year they want to highlight
    dbc.Row([
        dbc.Col(html.P(""), className = "col-2"),
        dbc.Col([html.P("Select Year: "),
                dbc.RadioItems(id = "main-radio-id",
                                options = [{"label": i, "value": i} for i in df2["Year"].unique()],
                                value="2021",
                                inline = True,
                                labelClassName = "radio-label",
                                inputClassName = "radio-input"
                                )], className = "col-8 col-center"),
        dbc.Col(html.P(""), className = "col-2")
    ]),
    #create a row to display the line graph
    dbc.Row([
        dbc.Col(dcc.Graph(id = "main-graph-id", 
                        config = {"displayModeBar": False, "responsive": True}), className = "col-12")
    ])
])




@app.callback(Output("main-graph-id", "figure"),
                Input("main-radio-id", "value"))
def create_main_page(year_select):

    #create a new column in actuals, forecast and annotations dataframes to contain the colour of the selected year
    df_actuals.loc[df_actuals["Year"] == year_select, "Colour"] = MAIN_COLOUR
    df_forecast.loc[df_forecast["Year"] == year_select, "Colour"] = MAIN_COLOUR
    df_line_label.loc[df_line_label["Year"] == year_select, "Colour"] = MAIN_COLOUR

    #add to the new column in actuals, forecast and annotations dataframes so it contain the colour of the non selected years
    df_actuals.loc[df_actuals["Year"] != year_select, "Colour"] = "#BDC3C7"
    df_forecast.loc[df_forecast["Year"] != year_select, "Colour"] = "#BDC3C7"
    df_line_label.loc[df_line_label["Year"] != year_select, "Colour"] = "#BDC3C7"

    #filter min max dataframe to only contain the year that is selected
    df_min_max_plot = df_min_max.loc[df_min_max["Year"] == year_select].copy()

    #filter the the commentary dataframe so that it contains only the annotation for the selected year
    df_commentary_plot = df_commentary.loc[df_commentary["Year"] == year_select].copy()

    #create a blank plotly graph objects canvas
    fig = go.Figure()
    
    #create a for loop to add individual traces to the graph specific to each year
    for year in df_actuals["Year"].unique():

        #add each year in actuals dataframe as a separate line in the visual
        df_plot = df_actuals.loc[df_actuals["Year"] == year].copy()


        fig.add_trace(go.Scatter(x = df_plot["Month"],
                        y = df_plot["Avg_House_Price"],
                        mode = "lines",
                        line = dict(color = df_plot["Colour"].tolist()[0]),
                        text = df_plot["Year"],
                        hovertemplate =
                        "Month: %{x}-%{text}<br>" +
                        "Avg House Price: %{y}<extra></extra>"
                        ))

    
    fig.add_trace(go.Scatter(x = df_forecast["Month"],
                        y = df_forecast["Avg_House_Price"],
                        mode = "lines",
                        line = dict(color = df_forecast["Colour"].tolist()[0], dash = "dash"),
                        text = df_plot["Year"],
                        hovertemplate =
                        "Month: %{x}-%{text}<br>" +
                        "Avg House Price: %{y}<extra></extra>"
                        ))

    #add the marker for the minimum house price
    fig.add_trace(go.Scatter(x = df_min_max_plot["Min_Month"], 
                            y = df_min_max_plot["Min_Price"],
                            mode = "markers",
                            marker = dict(color = df_min_max_plot["Min_Colour"],
                                        size = 12),
                            text = df_plot["Year"],
                            hovertemplate =
                            "Month: %{x}-%{text}<br>" +
                            "Avg House Price: %{y}<extra></extra>"))

    #add the marker for the maximum house price
    fig.add_trace(go.Scatter(x = df_min_max_plot["Max_Month"], 
                            y = df_min_max_plot["Max_Price"],
                            mode = "markers",
                            marker = dict(color = df_min_max_plot["Max_Colour"],
                                        size = 12),
                            text = df_plot["Year"],
                            hovertemplate =
                            "Month: %{x}-%{text}<br>" +
                            "Avg House Price: %{y}<extra></extra>"))                  

    fig.update_layout(plot_bgcolor = "white",
                    paper_bgcolor = "white",
                    showlegend=False,
                    font = dict(color = FONT_COLOUR, size = FONT_SIZE),
                    yaxis = dict(tickprefix = "$", range = [400000,600000]),
                    width = 1100,
                    height = 495
                    )

    for year, price, colour in zip(df_line_label["Year"], df_line_label["Avg_House_Price"], df_line_label["Colour"]):
        fig.add_annotation(text = year,
                            x = 1.02,
                            y = price,
                            xref ="paper",
                            yref = "y",
                            showarrow = False,
                            align ="left",
                            xanchor ="left",
                            font = dict(color = colour))

    #y-axis title
    fig.add_annotation(text = "AVG HOUSE PRICE",
                        x = -0.06,
                        y = 1.024,
                        xref = "paper",
                        yref = "paper",
                        showarrow = False,
                        textangle = -90,
                        align = "right",
                        yanchor = "top")

    #x-axis title
    fig.add_annotation(text = "MONTH",
                        x = -0.0125,
                        y = -0.055,
                        xref = "paper",
                        yref = "paper",
                        showarrow = False,
                        align = "left",
                        yanchor = "top")



    #add in commentary
    for commentary, x_pos, y_pos, alignment in zip(df_commentary_plot["Commentary"], df_commentary_plot["X_Pos"], df_commentary_plot["Y_Pos"], df_commentary_plot["Align"]):
        fig.add_annotation(text = commentary,
                            x = x_pos,
                            y = y_pos,
                            xref = "paper",
                            yref = "paper",
                            showarrow = False,
                            align = alignment,
                            xanchor = alignment,
                            yanchor = "top")

    #title
    fig.add_annotation(text = '<span style="color:' + MAX_COLOUR + '">July</span> has highest monthly average house prices for third straight year in 2021*',
                        x = -0.062,
                        y = 1.1,
                        xref = "paper",
                        yref = "paper",
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        yanchor = "bottom",
                        font = dict(size = TITLE_SIZE, color = TITLE_COLOUR))

    #sub-title
    fig.add_annotation(text = '*Based on monthly average house price predictions for Sep-Dec 2021',
                        x = -0.062,
                        y = 1.04,
                        xref = "paper",
                        yref = "paper",
                        showarrow = False,
                        align = "left",
                        xanchor = "left",
                        yanchor = "bottom",
                        font = dict(color = TITLE_COLOUR, size = FONT_SIZE + 1))


    return fig

