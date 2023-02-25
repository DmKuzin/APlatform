from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
# from StreamlitWebPlatform.Run import message_proc
import pandas as pd
import streamlit as st
import constants
import RequestScraper
import MessageProc

logo = constants.APP_LOGO_PATH

st.set_page_config(page_title="Argonauts",
                   page_icon=logo,
                   layout="wide"
                   )
st.sidebar.image(logo, width=300)

server_select = st.sidebar.selectbox(
    "Servers",
    ("Server-1", "Server-2", "Server-3")
)

# st.write('selected server:', server_select)

channel_select = st.sidebar.selectbox(
    "Channels",
    ("Channel-1", "Channel-2", "Channel-3")
)

discord_logger = MessageProc.MessageLogger(max_rows=constants.VIEW_SIZE)
analyse_logger = MessageProc.MessageLogger(max_rows=constants.VIEW_SIZE)

discord_data = discord_logger.load_data(filename=constants.DISCORD_FILE_PATH)
analyse_data = analyse_logger.load_data(filename=constants.ANALYSE_FILE_PATH)

discord_bot = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                        constants.SERVER_ID,
                                        constants.CHANNEL_ID,
                                        constants.DISCORD_FILE_PATH)

# define the columns to be displayed
# visible_columns = ['message', 'author']
cellStyle = {'color': 'rgba(184,185,191,255)',
             "font-size": "16px",
             }

jscode_discord = JsCode("""
            function(params) {
                if (params.data.status === "FROM_DISCORD") {
                    return {
                        'color': 'rgba(184,185,191,255)',
                        "font-size": "16px",
                        'backgroundColor': 'rgba(38,39,48,255)'
                    }
                }
                if (params.data.status === 'TO_ANALYSE') {
                    return {
                        'color': 'rgba(81, 82, 89, 1)',
                        "font-size": "16px",
                        'backgroundColor': 'rgba(38,39,48,255)'
                    }
                }
            };
""")

jscode_analyse = JsCode("""
            function(params) {
                if (params.data.status === "ANALYSE") {
                    return {
                        'color': 'rgba(184,185,191,255)',
                        "font-size": "16px",
                        'backgroundColor': 'rgba(38,39,48,255)'
                    }
                }
                if (params.data.status === 'SUMMARIZED') {
                    return {
                        'color': 'rgba(81, 82, 89, 1)',
                        "font-size": "16px",
                        'backgroundColor': 'rgba(38,39,48,255)'
                    }
                }
            };
""")
columns = ['message', 'id', 'datetime', 'author', 'status', 'server_id', 'channel_id']
discord_builder = GridOptionsBuilder.from_dataframe(discord_data)
discord_builder.configure_columns(column_names=columns,
                                  cellStyle=jscode_discord,
                                  wrapText=True,
                                  resizable=True,
                                  flex=1,
                                  autoHeight=True)

discord_builder.configure_selection(selection_mode='multiple', header_checkbox=True, use_checkbox=True)
# discord_builder.configure_default_column(min_column_width=50)
for col in columns:
    discord_builder.configure_column(col, hide=True)

discord_builder.configure_column('message', hide=False)
discord_builder.configure_column('author', hide=False)
# Set column header names
discord_builder.configure_column("message", headerName="Message")
discord_builder.configure_column("author", headerName="Author")
# discord_builder.configure_default_column(suppressMenu=True, wrapHeaderText=True, autoHeaderHeight=True)
# discord_builder.configure_column("message", {"width": 10})
# discord_builder.configure_column('message', width=100)
discord_builder.configure_side_bar()
discord_builder.configure_pagination()
go_discord = discord_builder.build()
# go_discord['getRowStyle'] = jscode

analyse_builder = GridOptionsBuilder.from_dataframe(analyse_data)
analyse_builder.configure_columns(column_names=columns,
                                  cellStyle=jscode_analyse,
                                  wrapText=True,
                                  resizable=True,
                                  flex=1,
                                  autoHeight=True)

analyse_builder.configure_selection(selection_mode='multiple', header_checkbox=True, use_checkbox=True)
# analyse_builder.configure_default_column(min_column_width=50)
for col in columns:
    analyse_builder.configure_column(col, hide=True)

analyse_builder.configure_column("message", hide=False)
analyse_builder.configure_column("author", hide=False)
# Set column header names
analyse_builder.configure_column("message", headerName="Message")
analyse_builder.configure_column("author", headerName="Author")
# gridOptions = {'headerHeight': 150}
# analyse_builder.configure_grid_options(groupHeaderHeight=75)
# analyse_builder.configure_column('message', width=100)
analyse_builder.configure_side_bar()
analyse_builder.configure_pagination()
go_analyse = analyse_builder.build()


# go_analyse['getRowStyle'] = jscode


def submit_discord_messages_to_analyse():
    state_discord_table = st.session_state.discord_table_key
    selected_rows = state_discord_table['selectedItems']
    selected_rows_df = pd.DataFrame(selected_rows)
    selected_message_ids = selected_rows_df['id'].tolist()

    # Set selected messages "to_analyse" status
    current_discord_data = discord_logger.load_data(filename=constants.DISCORD_FILE_PATH)
    idx = current_discord_data[current_discord_data['id'].isin(selected_message_ids)].index
    current_discord_data.loc[idx, 'status'] = MessageProc.MessageStatus.TO_ANALYSE.name
    current_discord_data.to_pickle(path=constants.DISCORD_FILE_PATH)

    # Add selected messages to analyse
    current_analyse_data = analyse_logger.load_data(filename=constants.ANALYSE_FILE_PATH)
    selected_rows_df['status'] = MessageProc.MessageStatus.ANALYSE.name
    added_analyse_data = pd.concat([current_analyse_data, selected_rows_df],
                                   axis=0, ignore_index=True)
    added_analyse_data.to_pickle(path=constants.ANALYSE_FILE_PATH)


def delete_analyse():
    # clear_logger = MessageProc.MessageLogger()
    # clear_logger.save_data(filename=constants.ANALYSE_FILE_PATH)
    state_analyse_table = st.session_state.analyse_table_key
    selected_rows = state_analyse_table['selectedItems']
    selected_rows_df = pd.DataFrame(selected_rows)
    selected_message_ids = selected_rows_df['id'].tolist()

    # Set selected messages "to_analyse" status
    current_analyse_data = analyse_logger.load_data(filename=constants.ANALYSE_FILE_PATH)
    idx = current_analyse_data[current_analyse_data['id'].isin(selected_message_ids)].index
    current_analyse_data.drop(idx, inplace=True)
    current_analyse_data.to_pickle(path=constants.ANALYSE_FILE_PATH)


def submit_analyse_messages_to_discord():
    state_analyse_table = st.session_state.analyse_table_key
    selected_rows = state_analyse_table['selectedItems']
    selected_rows_df = pd.DataFrame(selected_rows)
    selected_message_ids = selected_rows_df['id'].tolist()

    # Set selected messages "to_analyse" status
    current_analyse_data = analyse_logger.load_data(filename=constants.ANALYSE_FILE_PATH)
    idx = current_analyse_data[current_analyse_data['id'].isin(selected_message_ids)].index

    if st.session_state.delete_selected_after_submit:
        current_analyse_data.drop(idx, inplace=True)
    else:
        current_analyse_data.loc[idx, 'status'] = MessageProc.MessageStatus.SUMMARIZED.name

    current_analyse_data.to_pickle(path=constants.ANALYSE_FILE_PATH)

    summary = st.session_state.text_area_summary
    discord_bot.send_message(summary)


discord_col, analyse_col = st.columns(2, gap='medium')

with discord_col:
    st.header("Discord")
    with st.form(key='Discord_channel_form', ):
        discord_table = AgGrid(discord_data,
                               gridOptions=go_discord,
                               height=600,
                               width=150,
                               columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                               # fit_columns_on_grid_load=True,
                               reload_data=True,
                               allow_unsafe_jscode=True,
                               key='discord_table_key')
        submit_button_discord = st.form_submit_button(label='Submit selected',
                                                      on_click=submit_discord_messages_to_analyse)

with analyse_col:
    st.header("Analyse")
    with st.form(key='Analyse_channel_form'):
        analyse_table = AgGrid(analyse_data,
                               gridOptions=go_analyse,
                               height=600,
                               width=150,
                               # fit_columns_on_grid_load=True,
                               columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                               reload_data=True,
                               allow_unsafe_jscode=True,
                               key='analyse_table_key')

        col_del_all_button, col_del_sel_button = st.columns(2, gap='small')

        del_button_analyse = st.form_submit_button(label='Delete selected messages', on_click=delete_analyse)

        st.text_area(label='Summary', key='text_area_summary')

        col_button, col_check_box = st.columns(2, gap='small')

        with col_button:
            submit_button_analyse = st.form_submit_button(label='Submit summary',
                                                          on_click=submit_analyse_messages_to_discord)
        with col_check_box:
            st.checkbox(label='Delete selected after submit', key='delete_selected_after_submit')

# if st.button('Copy Selected Rows'):
#     clear_logger = message_proc.MessageLogger()
#     clear_logger.save_data(filename=ANALYSE_FILE_PATH)
#     st.experimental_rerun()
#     # selected_rows = discord_table.selected_rows
#     # selected_rows_df = pd.DataFrame(selected_rows)
#     # st.write(selected_rows_df)
#     #analyse_data = pd.concat([selected_rows_df,  analyse_data], axis=0, ignore_index=True)

# data2 = data2.append(selected_rows, ignore_index=True)
# table2.update_grid(data2, GridUpdateMode.REPLACE)


# discord_table

# st.write(df.selected_rows[0].values('Message'))

# create a Python class that has the following functions:
#     1. Periodically download updates from excel file to pandas dataframe and write them to .streamlit AgGrid table
# 2. in the constructor, the pandas dataframe update period from the excel file should be set
# 3. in the class constructor, the number of rows for the AgGrid table should be set
# 4. in the class constructor, the path to the excel file from which pandas dataframe updates are made should be set
# 5. AgGrid settings in the form of GridOptionsBuilder should be passed to the class constructor

# %%
