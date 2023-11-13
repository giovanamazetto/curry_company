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


st.set_page_config (page_title='Visão Entregadores', page_icon='🏍', layout='wide')


# -----------------------------
#         Funções
# -----------------------------
def top_delivers(df1, top_asc):
    df2= ( df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City','Time_taken(min)'], ascending= top_asc).reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02= df2.loc[df2['City']== 'Urban',:].head(10)
    df_aux03= df2.loc[df2['City']== 'Semi-Urban',:].head(10)
    df3= pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3
        
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


# Import Dataset
df = pd.read_csv('dataset/train.csv')

# Cleaning Dataset
df1 = clean_code(df)


# ===============================================================
#                            BARRA LATERAL
# ===============================================================
st.header('Makertplace - Visão Entregadores')


image_path= 'logo.png'
image= Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider= st.sidebar.slider(
    'Até qual valor?',
    value= pd.datetime(2022, 4, 13),
    min_value= pd.datetime(2022, 2, 11),
    max_value= pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')
 
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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_',])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #a maior idade
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade)

        with col2:
            #a menor idade
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', menor_idade)
            
        with col3:
            #melhor condicao de veiculo
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)

        with col4:
            #pior condicao de veiculo
            pior_condicao= df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
        
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1,col2= st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por entregador')
            avaliacoes= ( df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                             .groupby('Delivery_person_ID')
                             .mean()
                             .reset_index())
            st.dataframe(avaliacoes)
        
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            #usando o agg para fazer as duas em uma linha só e mostrar em um unico df
            av_trafego= ( df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                             .groupby('Road_traffic_density')
                             .agg({'Delivery_person_Ratings': ['mean','std']}) )
           
            #é bom renomear a coluna pra ficar mais bonita, e só assim da pra resetar o index
            av_trafego.columns=['delivery_mean','delivery_std']
            av_trafego.reset_index()
            st.dataframe(av_trafego)
            
            
            st.markdown('##### Avaliação média por clima')
            #usando o agg para fazer as duas em uma linha só e mostrar em um unico df
            av_clima= ( df1.loc[:,['Weatherconditions','Delivery_person_Ratings']].groupby('Weatherconditions')
                            .agg({'Delivery_person_Ratings': ['mean','std']}) )
            #é bom renomear a coluna pra ficar mais bonita, e só assim da pra resetar o index
            av_clima.columns=['delivery_mean','delivery_std']
            av_clima.reset_index()
            st.dataframe(av_clima)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        
        col1, col2= st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc= True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc= False)
            st.dataframe(df3)
            