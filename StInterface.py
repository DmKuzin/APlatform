#from typing import Dict
#import time
from st_aggrid import AgGrid
#from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
from st_aggrid import GridOptionsBuilder, JsCode
import streamlit_authenticator as stauth
#import pickle
import pandas as pd
import streamlit as st
import constants
import RequestScraper
import MessageProc
import yaml

# for k, v in st.session_state.items():
#     st.write(k)
#     #st.write(v)
#     #st.session_state[k] = v

if 'discord_table_key' not in st.session_state:
    st.session_state['discord_table_key'] = None

# if 'channel_select' not in st.session_state:
#     st.session_state['channel_select'] = None

logo = constants.APP_LOGO_PATH

st.set_page_config(page_title="Argonauts",
                   page_icon=logo,
                   layout="wide"
                   )

## load hashed passwords
with open(constants.AUTHENTICATION_CONFIG_FILE_PATH) as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
# --- USER AUTHENTICATION ---
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error('Username/password is incorrect')
if authentication_status == None:
    st.warning('Please enter your username and password')

if authentication_status:

    st.sidebar.markdown('<h1 style="text-align: center;">-- ARGONAUTS --</h1>', unsafe_allow_html=True)
    st.sidebar.image(logo, width=constants.IMAGE_LOGO_SIZE)

    # --- LOAD SERVERS FROM FILE ---

    # Read servers table from file
    from_discord_servers_table = pd.read_csv(constants.FROM_DISCORD_SERVERS_TABLE_PATH)
    # user availability to servers
    server_available_user = from_discord_servers_table['user_to_server_availability'] == username
    # Get server names
    server_names = list(set(from_discord_servers_table[server_available_user]['server_name'].to_list()))
    # Get channels from selected server
    server_selected = st.sidebar.selectbox("Servers", server_names, key='server_select')
    # Selected servers names
    selected_server_names = from_discord_servers_table['server_name'] == server_selected
    # user availability to servers
    channel_available_user = from_discord_servers_table['user_to_channel_availability'] == username
    #if sum(channel_available_user) > 0:
    channels_available = from_discord_servers_table[selected_server_names & channel_available_user]['channel_name'].to_list()

    server_id = \
    from_discord_servers_table[from_discord_servers_table['server_name'] == server_selected]['server_id'].to_list()[0]
    # Set channels from selected server
    channel_selected = st.sidebar.selectbox("Channels", channels_available, key='channel_select')

    st.sidebar.write(f'User: {name}')
    authenticator.logout('Logout', "sidebar")

    # Get channel id
    channel_id = None
    if channel_selected is not None:
        channel_id = from_discord_servers_table[from_discord_servers_table['channel_name'] == channel_selected]['channel_id'].to_list()[0]
    else:
        st.warning('No available channels')

    # --- CREATE DISCORD LISTENER ---

    # Create Discord channel listener
    psql_conn = {'host': constants.POSTGRESQL_CONNECTION_HOST,
                 'database': constants.POSTGRESQL_CONNECTION_DATABASE,
                 'user': constants.POSTGRESQL_CONNECTION_USER,
                 'password': constants.POSTGRESQL_CONNECTION_PASSWORD}

    discord_listener = RequestScraper.DiscordBot(constants.AUTHORIZATION_TOKEN,
                                                 server_id,
                                                 channel_id,
                                                 psql_conn)

    # --- LOAD DATA FROM FILE ---

    # Create message logger for discord
    discord_logger = MessageProc.SQLMessageLogger(constants.POSTGRESQL_CONNECTION_HOST,
                                                  constants.POSTGRESQL_CONNECTION_DATABASE,
                                                  constants.POSTGRESQL_CONNECTION_USER,
                                                  constants.POSTGRESQL_CONNECTION_PASSWORD)
    # Create message logger for analyse
    analyse_logger = MessageProc.SQLMessageLogger(constants.POSTGRESQL_CONNECTION_HOST,
                                                  constants.POSTGRESQL_CONNECTION_DATABASE,
                                                  constants.POSTGRESQL_CONNECTION_USER,
                                                  constants.POSTGRESQL_CONNECTION_PASSWORD)

    # Load data from SQL tables
    discord_data = discord_logger.load_data_from_table(constants.DISCORD_SQL_VIEW)
    discord_data = discord_data[discord_data['channel_name'] == channel_selected]

    analyse_data = analyse_logger.load_data_from_table(constants.ANALYSE_SQL_VIEW)
    analyse_data = analyse_data[analyse_data['channel_name'] == channel_selected]

    # Read servers table from file
    to_group_servers_table = pd.read_csv(constants.TO_GROUP_SERVERS_TABLE_PATH)
    to_group_server_id = to_group_servers_table['server_id'].to_list()[0]
    to_group_channel_id = to_group_servers_table['channel_id'].to_list()[0]


    # Bot for send message to group
    #@st.cache_resource
    def discord_bot():
        psql_conn = {'host': constants.POSTGRESQL_CONNECTION_HOST,
                     'database': constants.POSTGRESQL_CONNECTION_DATABASE,
                     'user': constants.POSTGRESQL_CONNECTION_USER,
                     'password': constants.POSTGRESQL_CONNECTION_PASSWORD}

        return RequestScraper.DiscordBot(constants.TO_GROUP_AUTHORIZATION_TOKEN,
                                         to_group_server_id,
                                         to_group_channel_id,
                                         psql_conn)

    # define the columns to be displayed
    # visible_columns = ['message', 'author']
    # cellStyle = {'color': 'rgba(184,185,191,255)',
    #              "font-size": "16px",
    #              }

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
    # try:
    #     selected_row = st.session_state["discord_table_key"]["selectedItems"][0]["rowIndex"]
    # except (KeyError, IndexError):
    #     selected_row = 0

    # --- CONFIGURATE TABLES ---
    selected_row = 0

    columns = ['message',
               'id',
               'datetime',
               'author',
               'status',
               'server_name',
               'channel_name',
               'mentions_id',
               'mentions_username',
               'message_reference_channel_id',
               'message_reference_guild_id',
               'message_reference_message_id',
               'referenced_message_id',
               'referenced_message_content',
               'referenced_message_channel_id',
               'referenced_message_author_username']

    discord_builder = GridOptionsBuilder.from_dataframe(discord_data)
    discord_builder.configure_columns(column_names=columns,
                                      cellStyle=jscode_discord,
                                      wrapText=True,
                                      resizable=True,
                                      flex=1,
                                      autoHeight=True)

    # discord_builder.configure_selection(selection_mode='multiple', pre_selected_rows=[selected_row],
    #                                     header_checkbox=True, use_checkbox=True)

    discord_builder.configure_selection(selection_mode='multiple', header_checkbox=True, use_checkbox=True)
    # discord_builder.configure_default_column(min_column_width=50)
    # Hide support columns
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
    # discord_builder.configure_pagination()
    go_discord = discord_builder.build()
    # go_discord['getRowStyle'] = jscode

    scroll = {'suppressScrollOnNewData': True}

    go_discord.update(scroll)

    # st.write(go_discord)

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
    # analyse_builder.configure_pagination()
    go_analyse = analyse_builder.build()

    scroll = {'suppressScrollOnNewData': True}
    go_analyse.update(scroll)


    # go_analyse['getRowStyle'] = jscode

    # @st.cache_data
    def submit_discord_messages_to_analyse():
        state_discord_table = st.session_state.discord_table_key
        #st.write(state_discord_table)

        if state_discord_table is not None:
            selected_rows = state_discord_table['selectedItems']
            selected_rows_df = pd.DataFrame(selected_rows)
            selected_message_ids = selected_rows_df['id'].tolist()

            # Set selected messages "to_analyse" status
            update_status_list = ",".join("'" + str(i) + "'" for i in selected_message_ids)
            discord_logger.update_status_rows_from_table(constants.DISCORD_SQL_TABLE, update_status_list, MessageProc.MessageStatus.TO_ANALYSE.name)
            status_analyses = MessageProc.MessageStatus.ANALYSE.name
            # Log selected messages to_analyse table
            for idx, row in selected_rows_df.iterrows():
                analyse_logger.log_data_to_table(constants.ANALYSE_SQL_TABLE,
                                                 row['message'],
                                                 str(row['id']),
                                                 row['datetime'],
                                                 row['author'],
                                                 status_analyses,
                                                 row['server_name'],
                                                 row['channel_name'],
                                                 row['mentions_id'],
                                                 row['mentions_username'],
                                                 row['message_reference_channel_id'],
                                                 row['message_reference_guild_id'],
                                                 row['message_reference_message_id'],
                                                 row['referenced_message_id'],
                                                 row['referenced_message_content'],
                                                 row['referenced_message_channel_id'],
                                                 row['referenced_message_author_username'])
        else:
            st.warning('No selected messages for submit')

    # --- CALLBACK FUNCTIONS ---

    # @st.cache_data
    def delete_analyse():
        state_analyse_table = st.session_state.analyse_table_key

        if state_analyse_table is not None:
            selected_rows = state_analyse_table['selectedItems']
            selected_rows_df = pd.DataFrame(selected_rows)
            selected_message_ids = selected_rows_df['id'].tolist()

            # Delete selected messages
            del_ids_list = ",".join("'" + str(i) + "'" for i in selected_message_ids)
            analyse_logger.delete_rows_from_table(constants.ANALYSE_SQL_TABLE, del_ids_list)
        else:
            st.warning('No selected messages for delete')


    # @st.cache_data
    def submit_analyse_messages_to_discord():
        state_analyse_table = st.session_state.analyse_table_key

        if state_analyse_table is not None:
            selected_rows = state_analyse_table['selectedItems']
            selected_rows_df = pd.DataFrame(selected_rows)
            selected_message_ids = selected_rows_df['id'].tolist()
            # Delete selected messages is set flag delete_selected_after_submit
            if st.session_state.delete_selected_after_submit:
                del_ids_list = ",".join("'" + str(i) + "'" for i in selected_message_ids)
                analyse_logger.delete_rows_from_table(constants.ANALYSE_SQL_TABLE, del_ids_list)
            else:
                update_status_list = ",".join("'" + str(i) + "'" for i in selected_message_ids)
                status_summ = MessageProc.MessageStatus.SUMMARIZED.name
                analyse_logger.update_status_rows_from_table(constants.ANALYSE_SQL_TABLE, update_status_list, status_summ)

            summary = st.session_state.text_area_summary

            # Parse the table
            out_text_body = ''
            count = 1
            for item in selected_rows:
                msg = item['message']
                id = item['id']
                author = item['author']
                msg_datetime = item['datetime']

                new_string = 'count: {}\nid: {}\ndatetime: {}\nauthor: {}\nmessage: {' \
                             '}\n'.format(count, id, msg_datetime, author, msg)
                out_text_body += new_string + '\n'
                count += 1

            full_summary = out_text_body + 'Summary: ' + summary
            # Send message to discord channel
            discord_bot().send_message(full_summary)
            # Log summary to table
            analyse_logger.log_summary(constants.SUMMARY_SQL_TABLE, out_text_body, summary)
        else:
            st.warning('No selected messages for submit')

    # @st.cache_data(show_spinner='Reading messages...')
    def add_new_messages_from_discord():
        # with st.spinner('Reading messages...'):
        # state_discord_table = st.session_state.discord_table_key
        last_row = discord_listener.sql_msg_logger.get_last_row_from_table(constants.DISCORD_SQL_VIEW, discord_listener.channel_name)
        if len(last_row) > 0:
            discord_listener.last_message_id = str(last_row['id'].to_list()[0])
        # Read the latest message
        discord_listener.read_latest_messages()


    def add_historical_messages_from_discord():
        # with st.spinner('Reading messages...'):
        num_msg = st.session_state.slider_number_of_messages_read
        # Get VIEW_SIZE latest messages from discord channel
        discord_listener.get_historical_messages(max_num=num_msg)


    # --- BUILD UI ---

    discord_col, analyse_col = st.columns(2, gap='medium')

    with discord_col:
        st.header("Discord")
        with st.form(key='Discord_channel_form'):
            discord_table = AgGrid(discord_data,
                                   gridOptions=go_discord,
                                   height=constants.MESSAGE_TABLE_HEIGHT,
                                   width=constants.MESSAGE_TABLE_WIDTH,
                                   fit_columns_on_grid_load=True,
                                   #columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                                   reload_data=True,
                                   allow_unsafe_jscode=True,
                                   key='discord_table_key')

            # col_add_new_mes_button, col_add_hist_mes_from_discord, col_submit_button = st.columns(3, gap='small')
            # col_add_new_mes_button, col_add_hist_mes_from_discord = st.columns(2, gap='small')
            col_add_new_mes_button, empty_column, col_submit_button = st.columns([2, 5, 2], gap='small')

            with col_add_new_mes_button:
                add_new_message_button = st.form_submit_button(label='Read new messages',
                                                               on_click=add_new_messages_from_discord)

                #with left_col:
                add_hist_mes_from_discord_button = st.form_submit_button(label='Read historical messages',
                                                                         on_click=add_historical_messages_from_discord)
                #with right_col:
                st.slider(label=':envelope_with_arrow: Number of read',
                          min_value=constants.NUM_HISTORICAL_MESSAGE_MIN,
                          max_value=constants.NUM_HISTORICAL_MESSAGE_MAX,
                          value=constants.NUM_DEFAULT_HISTORICAL_MESSAGE,
                          key='slider_number_of_messages_read'
                          #label_visibility='hidden'
                )

            with col_submit_button:
                submit_button_discord = st.form_submit_button(label='Submit selected',
                                                              on_click=submit_discord_messages_to_analyse)


    with analyse_col:
        st.header("Analyse")
        with st.form(key='Analyse_channel_form'):
            analyse_table = AgGrid(analyse_data,
                                   gridOptions=go_analyse,
                                   height=constants.MESSAGE_TABLE_HEIGHT,
                                   width=constants.MESSAGE_TABLE_WIDTH,
                                   fit_columns_on_grid_load=True,
                                   #columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
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
