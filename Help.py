import streamlit as st
import base64

st.set_page_config(
    page_title='CARTAR',
    page_icon='logo.png',
    layout='wide'
)

st.logo('logo_v2.png', icon_image='logo.png')

mystyle = '''
    <style>
        p {
            text-align: justify;
        }
    </style>
    '''

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
st.title('Welcome to CARTAR')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
st.markdown('### Introduction')
st.markdown('The CARTAR web page offers a suite of tools designed to facilitate the identification of potential targets for Chimeric Antigen Receptor (CAR) therapies. Leveraging expression data from The Cancer Genome Atlas (TCGA) project ([tcga_RSEM_gene_tpm](https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/tcga_RSEM_gene_tpm.gz)) and the Genotype-Tissue Expression (GTEx) project ([gtex_RSEM_gene_tpm](https://toil-xena-hub.s3.us-east-1.amazonaws.com/download/gtex_RSEM_gene_tpm.gz)), our platform focuses on pinpointing tumor-associated antigens located on the cell surface ensuring target selectivity, and assessing specificity.')
st.markdown('CARTAR is based on RNA sequencing expression data of 10,522 samples from the TCGA project and 7,858 samples from the GTEx project, using a standard pre-processing pipeline. Raw data was meticulously processed to isolate genes located in the __plasma membrane (GO:0005886)__. These membrane-bound proteins serve as prime candidates for CAR therapy targeting. Additionally, the dataset was annotated with tumor types and conditions (primary tumor, metastatic, or control), with GTEx data serving as control samples where applicable.')
st.markdown('This website is free and open to all users and there is no login requirement. The code used for raw files preprocessing is available at [GitHub](https://github.com/mighg/CARTAR).')
st.markdown('### CARTAR tools')
st.markdown('- __Tumor-associated antigens:__ identify tumor-associated antigens.')
st.markdown('- __Tumor expression change:__ explore fold change expression values of a gene or set of genes accross specified tumors.')
st.markdown('- __Tumor median expression:__ visualize median expression values of a candidate gene across primary tumors, metastatic (if available), and control samples.')
st.markdown('- __Tumor gene expression:__ analyze expression values of a specific gene across primary tumor and control samples of specified tumors.')
st.markdown('- __Tissue gene expression:__ study off-tumor gene expression to assess specificity of candidate target genes.')
st.markdown('- __Metastatic gene expression:__ analyze expression values of a specific gene across primary tumor, metastatic and control samples on Skin Cutaneous Melanoma (SKCM).')
st.markdown('- __Logic-gated CAR:__ explore the correlation between the expression values of two genes in primary tumor and control samples of a specified tumor for the design of dual- targeting CAR therapy.')
st.markdown('- __Cell line selector:__ identify cancer cell lines with desired expression values of target gene.')
st.markdown('### Methodology')
st.markdown('__Raw data__')
st.markdown('The Cancer Genome Atlas (TCGA) project provides RNA sequencing (RNA-Seq) data encompassing 9,795 tumor samples, spanning 33 distinct cancer types, alongside 727 samples corresponding to adjacent normal tissue, referred here as control. To solve the inherent imbalance in sample sizes between tumor and control datasets, which compromise statistical significance in differential analyses, the inclusion of RNA-Seq data from 8,295 control samples sourced from the Genotype-Tissue Expression (GTEx) project were included ([Figure 1](https://doi.org/10.1093/bib/bbae326)). This addition ensures a comprehensive and representative dataset, mitigating the potential biases and fortifying the robustness of subsequent statistical analyses.')
st.image('Figure 1.png', use_column_width=True)
st.markdown('The recomputed raw RNA-Seq data from TCGA (tcga RSEM gene tpm) and GTEx (gtex RSEM gene tpm) were obtained through the UCSC Xena project, ensuring a harmonized and reliable foundation for subsequent analyses.  Phenotype data from both projects were downloaded from the UCSC Xena project for sample identification (TCGA phenotype and GTEX phenotype). On the other hand, data from 1,479 cancer cell lines were obtained, including metadata, by downloading the relevant information from the DepMap Public 23Q4 files (ExpressionProteinCodingGenes, DepMap23Q4Model v2).')
st.markdown('__Data processing__')
st.markdown('Raw data files underwent pre-processing ([Figure 2](https://doi.org/10.1093/bib/bbae326)). Additionally, the expression files from TCGA and GTEx were combined, retaining only the genes located in the plasma membrane (GO: 0005886), as CARs target tumor cells’ surface antigens. P-values were calculated with the Mann-Whitney U test and multiple test correction was applied when required to calculate the adjusted p-value.')
st.image('Figure 2.png', use_column_width=True)
st.markdown('### Cookie policy')
st.markdown('Please be aware that this web tool utilizes cookies established by Streamlit for enhanced user experience and functionality. By continuing to use the tool, you agree to the usage of these cookies.')
st.markdown('### Contact us')
st.markdown('For any questions or requests about CARTAR, please contact us: miguel.gamarra@usc.es')
create_footer()
