import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon= '🎲'
)


# ===============================================================
#                            BARRA LATERAL
# ===============================================================
st.header('Makertplace - Visão Restaurantes')


#image_path= 'logo.png'
image= Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão Gerencial: métricas gerais de comportamento
        - Visão Tática: indicadores semanais de crescimento
        - Visão geográfica: insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    Comunidade DS
      ''' )