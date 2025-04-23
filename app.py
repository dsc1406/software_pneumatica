import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go

def main_page():
    # ------------------------------------------- SIDEBAR ------------------------------------------------------------#
    path = os.path.join('arquivos', 'banco_dados_pneumatica.csv')
    df = pd.read_csv(path, index_col=0)
    
    with st.sidebar:
        dict_tipo_cil = {'Norma - ISO 15552': 15552, 'Compacto - ISO 21287': 21287}
        tipo_cilindro = st.selectbox('Selecione o tipo de Cilindro', dict_tipo_cil.keys(), index=None, placeholder='Normal ou Compacto')

        if tipo_cilindro != None:
            df_filtrado = df.loc[df['Norma'] == dict_tipo_cil[tipo_cilindro]]
            tamanho_cilindro = st.selectbox('Selecione o Ø do Êmbolo em (mm)', df_filtrado['Ø Êmbolo (mm)']. unique(), index=None, placeholder='Selecione o Tamanho')
            pressao = st.number_input('Digite a Pressão da linha (Bar)', min_value=0.0, step=0.1, value=7.0, placeholder='Valor em Bar...')
            possui_alav = st.checkbox('Possui Braço de Alavanca?')
        
            if possui_alav:
                braco_alavanca = st.number_input('Braço de Alavanca (mm)', min_value=0.0, step=0.1, value=None, placeholder='Valor em mm...')

    tab1, tab2, tab3 = st.tabs(['Instruções', 'Resultados', 'Dimensões'])

    if tipo_cilindro != None:
        if tamanho_cilindro != None and pressao != (None or 0):
            if pressao <= 12:
                with tab2:
                    # --------------------------------------------CALCULOS, METRICS E GRÁFICOS---------------------------------------------------------#
                    pressao_pascal = pressao * 100000
                    area_embolo = np.pi * (tamanho_cilindro/2000)**2
                    forca_avanco = pressao_pascal * area_embolo

                    df_filtrado = df_filtrado.loc[df_filtrado['Ø Êmbolo (mm)'] == tamanho_cilindro,:].reset_index(drop=True)
                    diametro_haste = df_filtrado.loc[0, 'Ø Haste (mm)']
                    area_haste = np.pi * (diametro_haste/2000)**2
                    area_recuo = area_embolo - area_haste
                    forca_recuo = pressao_pascal * area_recuo

                    if dict_tipo_cil[tipo_cilindro] == 15552:
                        forca_ava_lim = area_embolo * 100000 * 12
                        forca_rec_lim = area_recuo * 100000 * 12
                    else:
                        forca_ava_lim = area_embolo * 100000 * 10
                        forca_rec_lim = area_recuo * 100000 * 10               

                    st.subheader("Resultados do Cálculo")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Força de avanço", f"{round(forca_avanco)} N", border=True)
                    col2.metric("Força de recuo", f"{round(forca_recuo)} N",border=True)

                    forcas_atuais = [round(forca_avanco), round(forca_recuo)]
                    forcas_limite = [round(forca_ava_lim), round(forca_rec_lim)]      
                    categorias = ['Avanço', 'Recuo']

                    chart_col1, chart_col2 = st.columns(2)

                    with chart_col1:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=categorias,
                            y=forcas_limite,
                            name='Limite',
                            marker_color='#A0A0A0',
                            text=forcas_limite,
                            textposition='outside',
                            textfont=dict(color='blue')
                        ))

                        fig.add_trace(go.Bar(
                            x=categorias,
                            y=forcas_atuais,
                            name='Atual',
                            marker_color='#4E79A7',
                            text=forcas_atuais,
                            textposition='outside',
                            textfont=dict(color='blue')
                        ))

                        fig.update_layout(
                            title='Força de Avanço e Recuo',
                            barmode='overlay',  # sobreposição das barras
                            yaxis_title='Força (N)',
                            xaxis_title='Tipo de Força',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

                    if possui_alav == True and braco_alavanca != None:
                        torque_avanço = forca_avanco * (braco_alavanca/1000)
                        torque_recuo = forca_recuo * (braco_alavanca/1000)

                        torque_ava_lim = forca_ava_lim * (braco_alavanca/1000)
                        torque_rec_lim = forca_rec_lim * (braco_alavanca/1000)

                        col3.metric("Torque de avanço", f"{round(torque_avanço)} Nm", border=True)
                        col4.metric("Torque de recuo", f"{round(torque_recuo)} Nm",border=True)

                        torque_atuais = [round(torque_avanço), round(torque_recuo)]
                        torque_limite = [round(torque_ava_lim), round(torque_rec_lim)]      
                        categorias = ['Avanço', 'Recuo']
                        
                        with chart_col2:
                            fig_torque = go.Figure()
                            fig_torque.add_trace(go.Bar(
                                x=categorias,
                                y=torque_limite,
                                name='Limite',
                                marker_color='#A0A0A0',
                                text=torque_limite,
                                textposition='outside',
                                textfont=dict(color='blue')
                            ))

                            fig_torque.add_trace(go.Bar(
                                x=categorias,
                                y=torque_atuais,
                                name='Atual',
                                marker_color='#4E79A7',
                                text=torque_atuais,
                                textposition='outside',
                                textfont=dict(color='blue')
                            ))

                            fig_torque.update_layout(
                                title='Torque de Avanço e Recuo',
                                barmode='overlay',  # sobreposição das barras
                                yaxis_title='Torque (Nm)',
                                xaxis_title='Tipo de Torque',
                                height=500
                            )

                            st.plotly_chart(fig_torque, use_container_width=True)    
                with tab3:
                    with st.container(border=True):
                        fabricante = st.radio('Selecione o Fabricante:', df_filtrado['Fabricante'].unique(), horizontal=True)
                    
                    df_filtrado_show = df_filtrado.loc[df_filtrado['Fabricante'] == fabricante,['Norma', 'Modelo', 'Ø Êmbolo (mm)','Curso (mm)', 'Comprimento Total (mm)', 'Rosca Haste', 'Conexão Pneumática', '▯ Distância Quadrada Fixações (mm)', 'Parafuso de Fixação']].reset_index(drop=True)
                    df_filtrado_pressure = df_filtrado.loc[df_filtrado['Fabricante'] == fabricante,['Pressão Máxima (Bar)']].reset_index(drop=True)
                    df_filtrado_show[['Comprimento Total (mm)', 'Curso (mm)']] = df_filtrado_show[[ 'Comprimento Total (mm)', 'Curso (mm)']].astype('int')

                    if df_filtrado_pressure.loc[0, 'Pressão Máxima (Bar)'] >= pressao:
                        st.table(df_filtrado_show.set_index('Norma').sort_values('Curso (mm)'))    
                    else:
                        st.warning('Somente os Cilindro ISO 15552 da FESTO suportam pressão maior que 10 bar')        
            else:
                st.sidebar.warning('Pressão Máxima permitida 12 bar.')
        else:
            st.sidebar.info('Selecione o Tamanho e a Pressão inciar os cálculos')
    else:
        st.sidebar.info('Selecione o Tipo de Cilindro')

    with tab1:
        st.markdown("""
                    
        # 🔧 **PneuMate** - Dimensionador de Cilindros Pneumáticos 
        Desenvolvido por Diego Carneiro
                    
        ---                      

        🚀 **Objetivo do aplicativo**  
        Este software foi desenvolvido para **substituir as tradicionais tabelas de dimensionamento** de cilindros pneumáticos fornecidas pelos fabricantes, tornando o processo de seleção muito mais prático, rápido e visual.

        ---

        ## ⚙️ **Como utilizar**

        A navegação é simples e dividida em abas. Aqui vai um passo a passo:

        ### 1️⃣ **Configuração inicial (Sidebar à esquerda)**  
        Preencha as seguintes informações:
        - 🛠️ **Tipo de cilindro**: Normal (ISO 15552) ou Compacto (ISO 21287)  
        - 📏 **Diâmetro do êmbolo**: Escolha entre os diâmetros padrão disponíveis  
        - 💨 **Pressão de operação**: Digite o valor desejado em bar  

        🔁 **(Opcional)**:  
        Se o projeto utilizar um **braço de alavanca**, habilite essa opção e informe o comprimento do braço em milímetros.

        ---

        ## 📊 **Resultados**  
        Nesta aba você encontrará:
        - 🔹 **Força de avanço**
        - 🔸 **Força de recuo**  
        Ambas serão calculadas automaticamente com base nas informações fornecidas.  
        Se o braço de alavanca estiver habilitado, será exibido também:
        - 🔁 **Torque gerado** no avanço e retorno

        ---

        ## 📐 **Dimensões dos Cilindros**  
        Aqui você poderá:
        - 🏢 Selecionar o **fabricante** desejado (Festo ou SMC)
        - 📋 Ver a **tabela com os principais dimensionais** do cilindro selecionado, incluindo:
        - Comprimento total  
        - Comprimento do corpo  
        - Rosca da haste  
        - Conexão Pneumática, entre outros

        🔎 Os dados seguem os padrões normativos ISO, e foram coletados com base em **modelos de referência** de cada marca.  
        ⚠️ Para modelos diferentes dos listados, recomendamos consulta direta ao site do fabricante.

        ---

        ## 📌 **Informações importantes**

        🔧 **Pressão máxima de operação:**
        - **Festo ISO 15552** → até **12 bar**  
        - **Demais casos** → limite de **10 bar**

        ✅ As forças calculadas consideram esse limite. Utilize com atenção!

        ---

        ## 💡 Dica final:
        Este app é ideal para engenheiros, projetistas e técnicos que desejam:
        - Reduzir tempo de dimensionamento  
        - Minimizar erros de projeto  
        - Visualizar de forma clara e objetiva os resultados

        📱 100% compatível com dispositivos móveis e desktops.

        ---

        ### 🚀 Simples, técnico e poderoso. Comece agora mesmo e otimize seus projetos!
        """)


def main():
    st.set_page_config(page_title="Calculo de Cilindros", layout="wide", initial_sidebar_state='expanded')

    main_page() 

if __name__ == "__main__":
    main()