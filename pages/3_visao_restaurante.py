# Libraries

import pandas as pd
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static
import numpy as np
import datetime

st.set_page_config (page_title='Visão Restaurante', page_icon='🍽', layout='wide')


# ===============================================================
#                              Funções
# ===============================================================
def avg_std_time_on_traffic(df1):
    cols = ['Time_taken(min)','City','Road_traffic_density']

    df_aux= df1.loc[:, cols].groupby(['City','Road_traffic_density']).agg( {'Time_taken(min)':['mean','std']} )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='avg_time',
                      color= 'std_time', color_continuous_scale= 'RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig

def avg_std_time_graph(df1):
    df_aux= df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg( {'Time_taken(min)':['mean','std']} )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig= go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], 
                         error_y=dict(type='data', array= df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery(df1, festival, op):
    """ Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros: 
        input:
            - df: Dataframe com os dados necessários para o cálculo
            - op: tipo de operação que precisa ser calculado
                'avg_time': calcula o tempo médio
                'std_time': calcula o desvio padrao do tempo
         output:
            - df: Dataframe com duas colunas e uma linha            
    """
    #tempo medio festival
    cols = ['Time_taken(min)','Festival']
    df_aux= df1.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)':['mean','std']} )
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)

    return df_aux

def distance(df1, fig):
        if fig == False:
            #distancia media
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_longitude', 'Restaurant_latitude']

            df1['distance'] = (df1.loc[:,cols].apply(lambda x:
                                    haversine(
                                        (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1))

            avg_distance = np.round(df1['distance'].mean(),2)
            
            return avg_distance
        
        else:
            #distancia media
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_longitude', 'Restaurant_latitude']

            df1['distance'] = (df1.loc[:,cols].apply(lambda x:
                                    haversine(
                                        (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1))
           
            avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
           
            return fig
            
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
   
       Tipo de limpeza: 
        1. remoção dos dados nulos
        2. mudança do tipo da coluna de dados
        3. remoção dos espaços das variáveis de texto
        4. formatação da coluna de datas
        5. limpeza da coluna de tempo (remoção do texto da variável numérica)
    
        Input: Dataframe
        Output: Dataframe
    """
    # retirando os valores nan
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # convertendo o type
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # removendo espaço dentro de strings/texto/object
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    # limpando a coluna do tempo
    df1['Time_taken(min)']= df1['Time_taken(min)'].apply(lambda x: x.split ( '(min)' ) [1] )
    df1['Time_taken(min)']= df1['Time_taken(min)'].astype(int)

    return df1

# ===============================================================
#                        Importando e limpando
# ===============================================================

# Import Dataset
df = pd.read_csv('dataset/train.csv')

# Cleaning Dataset
df1 = clean_code(df)


# ===============================================================
#                            BARRA LATERAL
# ===============================================================
st.header('Makertplace - Visão Restaurantes')


image_path= 'logo.png'
image= Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider=( st.sidebar.slider(
    'Até qual valor?',
    value= datetime.datetime(2022, 4, 13),
    min_value= datetime.datetime(2022, 2, 11),
    max_value= datetime.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY') )
 
st.sidebar.markdown("""---""")

traffic_options= st.sidebar.multiselect(
    'Quais as condicões do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low','Medium','High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1= df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1= df1.loc[linhas_selecionadas, :]

# ===============================================================
#                       LAYOUT NO STREAMLIT
# ===============================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica',])

with tab1:
    with st.container():
        st.markdown('## Overall Metrics')
        
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        
        with col1:
            #entregadores unicos
            delivery_unique= len(df1.loc[:,'Delivery_person_ID'].unique())
            
            col1.metric('Entregadores únicos',delivery_unique)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('Distância média',avg_distance)
            
        with col3:
            df_aux= avg_std_time_delivery (df1, 'Yes', 'avg_time')
            col3.metric('Tempo com festival',df_aux)
            
            
        with col4:
            df_aux= avg_std_time_delivery (df1, 'Yes', 'std_time')
            col4.metric('STD com festival',df_aux)
            
            
        with col5:
            #tempo medio sem festival
            df_aux= avg_std_time_delivery (df1, 'No', 'avg_time')
            col5.metric('Tempo sem festival',df_aux)
            
        with col6:
            #desvio padrao entrega sem festival
            df_aux= avg_std_time_delivery (df1, 'No', 'std_time')
            col6.metric('STD sem festival',df_aux)
        
    with st.container():
        st.markdown("""---""")
        col1,col2 = st.columns(2)
        
        with col1:
            st.markdown('#### Tempo médio de entrega por cidade')            
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        
        with col2:
            st.markdown('#### Distribuição da distância')
            cols = ['Time_taken(min)','City', 'Type_of_order']
            df_aux= df1.loc[:, cols].groupby(['City','Type_of_order']).agg( {'Time_taken(min)':['mean','std']} )
            df_aux.columns = ['avg_time','std_time']
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux)
        
    with st.container():
        st.markdown("""---""")
        st.markdown('#### Distribuição do tempo')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = distance(df1,fig=True)
            st.plotly_chart(fig, use_container_width=True)
           
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
        
   
        
         
