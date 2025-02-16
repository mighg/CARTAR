import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from math import log2
import pickle
import numpy as np
import seaborn as sns
import plotly.express as px
import base64

st.set_page_config(page_title='CARTAR', page_icon='logo.png',layout='wide')
mystyle = '''
    <style>
        p {
            text-align: justify;
        }
    </style>
    '''

st.logo('logo_v2.png', icon_image='logo.png')

st.markdown(
    """
    <style>
    [data-testid="stElementToolbar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create footer
def create_footer():
    footer_container = st.container()
    with footer_container:
        st.markdown("<br>" * 1, unsafe_allow_html=True)
        st.markdown("""
                <style>
                .footer-content {
                    background-color: #f0f2f6;
                    color: #262730;
                    padding: 10px;
                    text-align: center;
                    font-size: 10.5px;
                }
                @media (prefers-color-scheme: dark) {
                    .footer-content {
                        background-color: #262730;
                        color: #ffffff;
                    }
                    .footer-content a {
                        color: #4da6ff;
                    }
                }
                </style>
                <div class="footer-content">
                    How to cite: Miguel Hernandez-Gamarra, Alba Salgado-Roo, Eduardo Dominguez, Elena María Goiricelaya Seco, Sara Veiga-Rúa, Lucía F Pedrera-Garbayo, Ángel Carracedo, Catarina Allegue, CARTAR: a comprehensive web tool for identifying potential targets in chimeric antigen receptor therapies using TCGA and GTEx data, Briefings in Bioinformatics, Volume 25, Issue 4, July 2024, bbae326, <a href="https://doi.org/10.1093/bib/bbae326">https://doi.org/10.1093/bib/bbae326</a>.
                </div>
                """, unsafe_allow_html=True)

st.markdown(mystyle, unsafe_allow_html=True)
st.title('Gene correlation for logic gating CAR')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
st.write('This tool can be used to explore the correlation between two genes expression values in "Primary tumor" and "Control" samples of a specified tumor to assess the potential of their combination for a logic-gated CAR therapy (OR-gate, AND-gate, NOT-gate, or IF-BETTER-gate).')
st.markdown('- **OR-gate:** effector cell activation upon binding to either one of two antigens. This strategy can be used when either one of the antigens is highly expressed in "Primary tumor" samples, while their expression is low in "Control" samples.')
st.markdown('- **AND-gate:** effector cell activation upon binding to both antigens simultaneously. This strategy can be used when both antigens are expressed in "Primary tumor" samples, while none or only one of the antigens is expressed in "Control" samples.')
st.markdown('- **NOT-gate:** effector cell activation upon binding to one antigen while the second antigen is not recognised. This strategy can be used when the antigen triggering the cytotoxic activity is present in certain healthy tissues and you want to increase selectivity by including an antigen that respresses this activity and is only expressed in the healthy tissues. To identify these antigens you must go to **Tissue gene expression tool**.')
st.markdown('- **IF-BETTER-gate:** effector cell activation upon binding to high CAR target expression. Activation is not triggered upon binding to low CAR targer expression, unless the second antigen is present.')
#st.set_option('deprecation.showPyplotGlobalUse', False)

tumor_options  = ['ACC','BLCA','BRCA','CESC','CHOL','COAD','DLBC','ESCA','GBM','HNSC','KICH','KIRC','KIRP','LAML','LGG','LIHC','LUAD','LUSC','OV','PAAD','PCPG','PRAD','READ','SARC','SKCM','STAD','TGCT','THCA','THYM','UCEC','UCS']
scale_options = ['TPM','log2(TPM+1)']
# Abbreviation dictionary
abbreviations = {'ACC':'Adrenocortical carcinoma','BLCA':'Bladder Urothelial Carcinoma','BRCA':'Breast invasive carcinoma',
                 'CESC':'Cervical squamous cell carcinoma and endocervical adenocarcinoma','CHOL':'Cholangio carcinoma',
                 'COAD':'Colon adenocarcinoma','DLBC':'Lymphoid Neoplasm Diffuse Large B-cell Lymphoma','ESCA':'Esophageal carcinoma',
                 'GBM':'Glioblastoma multiforme','HNSC':'Head and Neck squamous cell carcinoma','KICH':'Kidney Chromophobe',
                 'KIRC':'Kidney renal clear cell carcinoma','KIRP':'Kidney renal papillary cell carcinoma',
                 'LAML':'Acute Myeloid Leukemia','LGG':'Brain Lower Grade Glioma','LIHC':'Liver hepatocellular carcinoma',
                 'LUAD':'Lung adenocarcinoma','LUSC':'Lung squamous cell carcinoma','OV':'Ovarian serous cystadenocarcinoma',
                 'PAAD':'Pancreatic adenocarcinoma','PCPG':'Pheochromocytoma and Paraganglioma','PRAD':'Prostate adenocarcinoma',
                 'READ':'Rectum adenocarcinoma','SARC':'Sarcoma','SKCM':'Skin Cutaneous Melanoma','STAD':'Stomach adenocarcinoma',
                 'TGCT':'Testicular Germ Cell Tumors','THCA':'Thyroid carcinoma','THYM':'Thymoma',
                 'UCEC':'Uterine Corpus Endometrial Carcinoma','UCS':'Uterine Carcinosarcoma'}

gene1 = st.text_input('Enter first gene symbol').upper().strip(' ')
# Identify if indicated gene is present in the data
data = pd.read_csv('Data/log2FC_expression.csv')
if gene1 == '':
    st.error('Introduce gene symbol. You can try CEACAM6')
if 'MORF' not in gene1:
    if 'ORF' in gene1:
        gene1 = gene1.replace('ORF','orf')
elif gene1 != '' and gene1 not in data['gene'].values:
    st.error(f'{gene1} gene symbol not found')
gene2 = st.text_input('Enter second gene symbol').upper().strip(' ')
if gene2 == '':
    st.error('Introduce gene symbol. You can try DPEP1')
if 'MORF' not in gene2:
    if 'ORF' in gene2:
        gene2 = gene2.replace('ORF','orf')
elif gene2 != '' and gene2 not in data['gene'].values:
    st.error(f'{gene2} gene symbol not found')
tumor = st.selectbox('Choose tumor', tumor_options)
# Expander to show abbreviation meaning
with st.expander('Extension of tumor abbreviations\' meaning'):
    for abbreviation, meaning in abbreviations.items():
        st.write(f"**{abbreviation}:** {meaning}")
selection = st.radio('Choose scale', scale_options)
if selection == 'TPM':
    scale = 'TPM'
elif selection == 'log2(TPM+1)':
    scale = 'log2(TPM+1)'
st.info('TPM = Transcript Per Million')

# Dictionary with the tumor:GTEx healthy tissue correspondance
gtex_tcga = {'ACC':'Adrenal Gland','BLCA':'Bladder','BRCA':'Breast','CESC':'Cervix Uteri', 'COAD':'Colon', 'DLBC':'Blood',
                    'ESCA':'Esophagus','GBM':'Brain','KICH':'Kidney','KIRC':'Kidney','KIRP':'Kidney','LAML':'Bone Marrow','LGG':'Brain',
                    'LIHC':'Liver','LUAD':'Lung','LUSC':'Lung','OV':'Ovary','PAAD':'Pancreas','PRAD':'Prostate','READ':'Colon','SKCM':'Skin',
                    'STAD':'Stomach','TGCT':'Testis','THCA':'Thyroid','THYM':'Blood','UCEC':'Uterus','UCS':'Uterus'}

if st.button(f'Show correlation'):
    if gene1 != '' and gene2 != '':
        # If gene in data
        if gene1 in data['gene'].values and gene2 in data['gene'].values:  
            if 'A' <= gene1[0] <= 'C':
                gtex1 = 'Data/gtex_AC.pkl'
                tcga1 = 'Data/tcga_AC.pkl'
            elif 'D' <= gene1[0] <= 'J':
                gtex1 = 'Data/gtex_DJ.pkl'
                tcga1 = 'Data/tcga_DJ.pkl'
            elif 'K' <= gene1[0] <= 'N':
                gtex1 = 'Data/gtex_KN.pkl'
                tcga1 = 'Data/tcga_KN.pkl'
            elif 'O' <= gene1[0] <= 'R':   
                gtex1 = 'Data/gtex_OR.pkl'
                tcga1 = 'Data/tcga_OR.pkl'
            elif 'S' <= gene1[0] <= 'T':   
                gtex1 = 'Data/gtex_ST.pkl'
                tcga1 = 'Data/tcga_ST.pkl'
            elif 'U' <= gene1[0] <= 'Z':   
                gtex1 = 'Data/gtex_UZ.pkl'
                tcga1 = 'Data/tcga_UZ.pkl'
            if 'A' <= gene2[0] <= 'C':
                gtex2 = 'Data/gtex_AC.pkl'
                tcga2 = 'Data/tcga_AC.pkl'
            elif 'D' <= gene2[0] <= 'J':
                gtex2 = 'Data/gtex_DJ.pkl'
                tcga2 = 'Data/tcga_DJ.pkl'
            elif 'K' <= gene2[0] <= 'N':
                gtex2 = 'Data/gtex_KN.pkl'
                tcga2 = 'Data/tcga_KN.pkl'
            elif 'O' <= gene2[0] <= 'R':   
                gtex2 = 'Data/gtex_OR.pkl'
                tcga2 = 'Data/tcga_OR.pkl'
            elif 'S' <= gene2[0] <= 'T':   
                gtex2 = 'Data/gtex_ST.pkl'
                tcga2 = 'Data/tcga_ST.pkl'
            elif 'U' <= gene2[0] <= 'Z':   
                gtex2 = 'Data/gtex_UZ.pkl'
                tcga2 = 'Data/tcga_UZ.pkl'
            # Create the dicitionary with all the data
            groups = [] # Groups of tumor (Primary or Control)
            values1 = [] # Gene1 expression values 
            values2 = [] # Gene2 expression values 
            #If both genes in same file get the desired data
            if gtex1 == gtex2:
                with open(tcga1, 'rb') as archivo:
                    tcga = pickle.load(archivo)
                for group in tcga[gene1][tumor].keys():
                    for value in tcga[gene1][tumor][group]:
                        if group == 'Normal':
                            group = 'Control'
                        groups.append(group)
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values1.append(value)
                for group in tcga[gene2][tumor].keys():
                    for value in tcga[gene2][tumor][group]:
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values2.append(value)
                if tumor in gtex_tcga.keys():            
                    with open(gtex1, 'rb') as archivo:
                        gtex = pickle.load(archivo)
                    for value in gtex[gene1][gtex_tcga[tumor]]:
                        groups.append('Control')
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values1.append(value)   
                    for value in gtex[gene2][gtex_tcga[tumor]]:
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values2.append(value)   
            #If genes in different files get data from respective files
            else:
                with open(tcga1, 'rb') as archivo:
                    tcga1 = pickle.load(archivo)
                for group in tcga1[gene1][tumor].keys():
                    for value in tcga1[gene1][tumor][group]:
                        if group == 'Normal':
                            group = 'Control'
                        groups.append(group)
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values1.append(value)
                with open(tcga2, 'rb') as archivo:
                    tcga2 = pickle.load(archivo)
                for group in tcga2[gene2][tumor].keys():
                    for value in tcga2[gene2][tumor][group]:
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values2.append(value)
                if tumor in gtex_tcga.keys():            
                    with open(gtex1, 'rb') as archivo:
                        gtex1 = pickle.load(archivo)
                    for value in gtex1[gene1][gtex_tcga[tumor]]:
                        groups.append('Control')
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values1.append(value)  
                    with open(gtex2, 'rb') as archivo:
                        gtex2 = pickle.load(archivo)    
                    for value in gtex2[gene2][gtex_tcga[tumor]]:
                        if scale == 'log2(TPM+1)':
                            value = log2(value+1)
                        values2.append(value)  
            data = {'Sample':groups, f'{gene1} expression':values1, f'{gene2} expression':values2}
            # Create correlation plot
            df = pd.DataFrame(data)          
            fig = px.scatter(data, x=f'{gene2} expression', y=f'{gene1} expression', color='Sample', color_discrete_sequence=['#20b2aa','#d2b48c'])
            # Customize graph titile and axis names
            if scale == 'log2(TPM+1)':
                fig.update_layout(title=f'{gene1} and {gene2} expression correlation in {tumor} samples', title_x=0.2, xaxis_title=f'{gene2} expression in log2(TPM+1)', yaxis_title= f'{gene1} expression in log2(TPM+1)')
            else:
                fig.update_layout(title=f'{gene1} and {gene2} expression correlation in {tumor} samples', title_x=0.2, xaxis_title=f'{gene2} expression in TPM', yaxis_title= f'{gene1} expression in TPM')
            # Create table with the results
            table_data = pd.DataFrame(data)
            if scale == 'TPM':
                plt.ylabel(f'{gene1} expression in TPM')
                plt.xlabel(f'{gene2} expression in TPM')
            else: 
                plt.ylabel(f'{gene1} expression in log2(TPM+1)')
                plt.xlabel(f'{gene2} expression in log2(TPM+1)')
            plt.xticks(rotation=45, ha='right')
            # Show the graph and table
            st.header('Correlation plot', divider='rainbow')
            st.plotly_chart(fig,use_container_width=True)
            st.write(
                f'The presented figure illustrates the expression correlation between {gene1} and {gene2} in {scale} within the {tumor}, showcasing the comparison of expression levels between "Primary Tumor" and "Control" samples.'
            )
            st.header('Data table', divider='rainbow')
            st.write(
                f'The table below displays the expression values of each gene for all samples. You can enhance your exploration by clicking on the column names to sort the tumors based on that column either from highest to lowest or vice versa.'
            )
            st.dataframe(table_data, hide_index=True)
            table = table_data.to_csv(encoding='utf-8', index=False)
            b64 = base64.b64encode(table.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="table.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)   
        else: 
            st.error('Review the introduced genes. One or both of them are not present in the dataset') 
    elif gene1 == '' and gene2 == '':
        st.error('Introduce desired gene symbols to see correlation')
    elif gene1 == '':
        st.error('You need to indicate the first gene symbol to see correlation')
    elif gene2 == '':
        st.error('You need to indicate the second gene symbol to see correlation')
create_footer()
