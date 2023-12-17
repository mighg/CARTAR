import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from math import log2
import numpy as np
import seaborn as sns
import pickle
from scipy.stats import mannwhitneyu

st.set_page_config(page_title='CARTAR', page_icon='logo.png',layout='wide')
mystyle = '''
    <style>
        p {
            text-align: justify;
        }
    </style>
    '''
@st.cache_data
def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def build_markup_for_logo(
    png_file,
    background_position="50% 10%",
    image_width="90%",
    image_height="",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    background-size: %s %s;
                }
                [data-testid="stSidebarNav"]::before {
                content: "";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 15px;
                position: relative;
                top: 100px;
                }
            </style>
            """ % (
        binary_string,
        background_position,
        image_width,
        image_height,
    )

def add_logo(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )

add_logo('logo_v2.png')

st.markdown(mystyle, unsafe_allow_html=True)
st.title('Metastatic gene expression in SKCM')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
st.write(
    'This tool will generate the indicated plot comparing expression values of the chosen gene in the selected scale between the \"Metastatic\", \"Primary tumor\" and \"Normal\" samples of Skin Cutaneous Melanoma (SKCM) and a table with all relevant data. This option is only available for SKCM due to the small number of \"Metastatic\" samples in the rest of the tumors. Data is obtained from TCGA project and GTEX expression data has also been included in the correponding control group.'
)
st.set_option('deprecation.showPyplotGlobalUse', False)

scale_options = ['TPM','log2(TPM+1)']
plot_options = ['Boxplot','Violinplot','Dotplot']

gene = st.text_input('Select gene').upper()
# Identify if indicated gene is present in the data
data = pd.read_csv('Data/log2FC_expression.csv')
if gene == '':
    st.error('Indicate a gene')
elif gene != '' and gene not in data['gene'].values:
    st.error('Indicated gene not found')
selection = st.radio('Choose plot', plot_options)
if selection == 'Boxplot':
    plot = 'Boxplot'
elif selection == 'Violinplot':
    plot = 'Violinplot'
elif selection == 'Dotplot':
    plot = 'Dotplot'
selection2 = st.radio('Choose scale', scale_options)
if selection2 == 'TPM':
    scale = 'TPM'
elif selection2 == 'log2(TPM+1)':
    scale = 'log2(TPM+1)'

# Calculate statistical significance and customize plot function
def plot_significance(tumor,y,bottom,top):
    significant_combinations = []
    data = {'Groups compared':[],'Median Group 1':[],'Group 1 sample size':[], 'Median Group 2':[],'Group 2 sample size':[], 'log2(Fold Change)':[],'Significance':[],'p-value':[]}
    # Get the y-axis limits
    y_range = top - bottom
    # Identify groups with statistical difference
    tumor_types = df['Sample'].unique()
    for i in reversed(range(len(tumor_types))):
        for j in range(i+1, len(tumor_types)):
            tumor1 = tumor_types[i]
            tumor2 = tumor_types[j]
            tumor1_data = df[df['Sample'] == tumor1]['Values']
            tumor2_data = df[df['Sample'] == tumor2]['Values']
            _, p_value = mannwhitneyu(tumor1_data, tumor2_data)
            data['Group 1 sample size'].append(len(tumor1_data))
            data['Group 2 sample size'].append(len(tumor2_data))
            data['Groups compared'].append(f'{tumor1} vs {tumor2}')
            data['Median Group 1'].append(np.median(tumor1_data))
            data['Median Group 2'].append(np.median(tumor2_data))
            data['p-value'].append(p_value)
            if p_value < 0.001:
                data['Significance'].append('<0.001')
            elif p_value < 0.01:
                data['Significance'].append('<0.01')
            elif p_value < 0.05:
                data['Significance'].append('<0.05')
            else: 
                data['Significance'].append('No significant')
            if scale == 'TPM':
                logvalues1 = [log2(value1 + 1) for value1 in tumor1_data]
                logvalues2 = [log2(value2 + 1) for value2 in tumor2_data]
                data['log2(Fold Change)'].append(np.median(logvalues1)-np.median(logvalues2))
            else:
                data['log2(Fold Change)'].append(np.median(tumor1_data)-np.median(tumor2_data))
            if p_value < 0.05:
                if np.median(tumor1_data) > np.median(tumor2_data):
                    k = 0
                else:
                    k = 1
                significant_combinations.append([(i,j),p_value,k])
    # Create table with the results
    table_data = pd.DataFrame(data)
    # Add to the graph the statistical significance bars
    significant_combinations = significant_combinations[::-1]
    for i, significant_combination in enumerate(significant_combinations):
        # Columns corresponding to the datasets of interest
        x1 = significant_combination[0][0]
        x2 = significant_combination[0][1]
        # What level is this bar among the bars above the plot?
        if i == 2:
            level = len(significant_combinations) - i + 1
        else:
            level = len(significant_combinations) - i 
        # Plot the bar
        bar_height = (y_range * 0.07 * level) + top
        bar_tips = bar_height - (y_range * 0.02)
        plt.plot(
            [x1, x1, x2, x2],
            [bar_tips, bar_height, bar_height, bar_tips], lw=1, c='k'
        )
        # Significance level
        p = significant_combination[1]
        if p < 0.001:
            sig_symbol = '***'
        elif p < 0.01:
            sig_symbol = '**'
        elif p < 0.05:
            sig_symbol = '*'
        text_height = bar_height + (y_range * 0.0001)
        plt.text((x1 + x2) * 0.5, text_height, sig_symbol, ha='center', va='bottom', color='black')
    # Customize the plot
    plt.title(f'{gene} expression comparison between SKCM conditions', y=1.03)
    if scale == 'TPM':
        plt.ylabel(f'{gene} expression in TPM')
    else: 
        plt.ylabel(f'{gene} expression in log2(TPM+1)')
    plt.xlabel('SKCM group')
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(left=0.067, bottom=0.155, right=0.968, top=0.91)
    # Show the graph and table
    st.header(plot, divider='rainbow')
    st.pyplot()
    st.write(
        f'The above figure shows the {plot} for {gene} expression in {scale} across \"Metastatic\", \"Primary tumor\" and \"Control\" {tumor} samples and compares the expression between theses groups. Statistical significance is shown between each {tumor} group (***: p_value < 0.001, **: p_value < 0.01, *: p_value < 0.05).'
    )
    st.header('Data table', divider='rainbow')
    st.write(
        f'All relevant data is shown in the table below, including the log2(Fold Change) for each comparison calculated as log2(TPM+1) median of SKCM Group 1 expression - log2(TPM+1) median of SKCM Group 2 expression, and the p-value of each comparison. You can click in the column names to order the rows according to that column from higher to lower or viceversa. By clicking in a cell you can see the value with all the decimals.'
    )
    st.dataframe(table_data, hide_index=True)
    st.write(
        'This table can be download in CSV format to be open in Excel or oher softwares compatible with this format.'
    )  

if st.button(f'Create {plot}'):
    if gene != '': 
        # Identify GTEX tissue sample corresponding to control group of tumor
        gtex_tcga = {'SKCM':'Skin'}
        with open('Data/SKCM.pkl', 'rb') as archivo:
            SKCM = pickle.load(archivo)
        # Get requested information
        groups = [] # Gruops of tumor (Metastatic, Primary or Normal)
        values = [] # Expression values
        for group in SKCM[gene]['SKCM'].keys():
            for value in SKCM[gene]['SKCM'][group]:
                groups.append('SKCM Tumor')
                if scale == 'log2(TPM+1)':
                    value = log2(value+1)
                values.append(value)
        data = {'Sample': groups, 'Values':values}
        df = pd.DataFrame(data)
        group_order = ['Metastatic', 'Primary', 'Normal']
        df['Sample'] = pd.Categorical(df['Sample'], categories=group_order, ordered=True)
        df = df.sort_values(by=['Sample'])
        # Create the boxplot
        if plot == 'Boxplot':
            plt.figure()
            sns.boxplot(data=df, x='Sample', y='Values', hue='Sample', legend=False, showfliers=False, palette={'Primary': 'lightseagreen', 'Normal': 'tan', 'Metastatic':'grey'})
            xmin, xmax, ymin, ymax = plt.axis()
            # Statistical significant differences and customize the plot
            plot_significance('SKCM',0,ymin,ymax)
        # Create the violin plot
        if plot == 'Violinplot':
            sns.violinplot(x='Sample', y='Values', hue='Sample', data=df, inner='quartile', density_norm='width',palette={'Primary': 'lightseagreen', 'Normal': 'tan', 'Metastatic':'grey'}, legend=False)
            xmin, xmax, ymin, ymax = plt.axis()
            # Statistical significant differences and customize the plot
            plot_significance('SKCM',1,ymin,ymax)        
        # Create the dotplot
        if plot == 'Dotplot':
            sns.stripplot(x='Sample', y='Values', jitter=True, data=data, hue='Sample', size=4, palette={'Primary': 'lightseagreen', 'Normal': 'tan', 'Metastatic':'grey'})
            plt.xlim(-0.5, 2.5)
            xmin, xmax, ymin, ymax = plt.axis()
            # Calculate the medians for each group
            medians = df.groupby('Sample', observed=False)['Values'].median()
            # Add a horizontal line for each median within the corresponding group
            n = 0.25
            for tumor, median in medians.items():
                x_start = xmin + n
                x_end = x_start + 0.5
                n += 1
                plt.plot(
                    [x_start, x_end],
                    [median, median], lw=1, c='k', zorder=10000
                )
            # Statistical significant differences and customize the plot
            plot_significance('SKCM',1,ymin,ymax)              