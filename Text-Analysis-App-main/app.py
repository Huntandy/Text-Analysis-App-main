import dash
from dash.dependencies import Input, Output, State
from dash import html
# import dash_html_components as html
from dash import dcc
# import dash_core_components as dcc
# import dash_table
from dash import dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import nltk
from decimal import Decimal, ROUND_HALF_UP
import re
from nltk.corpus import stopwords
import base64
import io
from zipfile import ZipFile
import random
import ast
import textstat

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
image_filename = './resources/logo_only2.png' 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

code_desc_df = pd.read_csv("./resources/Code_Description.csv", encoding="utf-8")
readability_df = pd.read_csv("./resources/Readability_Description.csv", encoding="utf-8")
fog_df = pd.read_csv("./resources/fog_index.csv", encoding="utf-8")
dach_df = pd.read_csv("./resources/dach_index.csv", encoding="utf-8")
flesch_df = pd.read_csv("./resources/flesch_index.csv", encoding="utf-8")
fm_df = pd.read_csv("./resources/fm_index.csv", encoding="utf-8")

elementary_en_words_list = list(set(open("./resources/gept1st.txt", "r", encoding="utf-8").read().split("\n")))
intermediate_en_words_list = list(set(open("./resources/gept2nd.txt", "r", encoding="utf-8").read().split("\n")))
advanced_en_words_list = list(set(open("./resources/gept3rd.txt", "r", encoding="utf-8").read().split("\n")))

external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Corpus Text Analysis'

mark_colors_graph = ["#EEA9A9", "#FB9966", "#FFBA84", "#DAC9A6", "#F7C242", "#B5CAA0", "#86C166", "#A8D8B9", "#66BAB7", "#81C7D4", "#58B2DC", 
                    "#7B90D2", "#9B90C2", "#8F77B5", "#B481BB", "#91989F", "#DC9FB4", "#FEDFE1", "#E87A90", "#B19693", "#DB8E71", "#BC9F77",
                    "#F9BF45", "#E9CD4C", "#91AD70", "#A5A051", "#86A697", "#7DB9DE", "#8B81C3", "#F4A7B9", "#F8C3CD", "#B4A582", "#D9CD90"]
mark_colors_text = ["#EEA9A9", "#FB9966", "#FFBA84", "#DAC9A6", "#F7C242", "#B5CAA0", "#A8D8B9", "#66BAB7", "#81C7D4", "#58B2DC", "#A5DEE4",
                    "#DC9FB4", "#FEDFE1", "#F9BF45", "#E9CD4C", "#91AD70", "#86A697", "#7DB9DE", "#8B81C3", "#F4A7B9", "#F8C3CD", "#D9CD90"]

server = app.server

app.layout = html.Div(children=[
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'display':'inline-block', 'width': '2.5%', 'height': '2.5%'}),
    html.H1(children='Corpus Text Analysis', style={'display':'inline-block', 'margin': '10px'}),
    html.Br(),
    html.H5("This corpus text analysis web-based app is a tool that allows users to upload several English text files for analysis and visualization of \U0001F505 Linguistics Features and \U0001F505 Readability. The two tables below show the descriptions of the measurement indices used in this app. We hope you enjoy using it! \U0001F970"),
    html.P("Here's a description of the linguistic features used as indicators on this website: \U0001F4DD"),
    dash_table.DataTable(columns=[{"name": i, "id": i} for i in code_desc_df.columns],
                         data=code_desc_df.to_dict('records'),
                         style_data={'height': '5px',},
                         ),
    html.P("Here's a description of the readability metrics used as indicators on this website: \U0001F4DD"),
    dash_table.DataTable(columns=[{"name": i, "id": i} for i in readability_df.columns],
                         data=readability_df.to_dict('records'),
                         style_data={'height': '5px',},
                         ),
    
    html.Br(),
    html.H2(children='Linguistic Features \u2712'),
    html.P("\U0001F514 Please upload a .zip file containing two or more English text files in the .txt format. \U0001F514"),
    html.P("\u26A0 The file names for the text files should consist entirely of Latin characters. \u26A0"),
    dcc.Upload(
        id='upload-txtdata',
        children=html.Div([
            'Drag and Drop or ', html.A('Select a .zip File')
            ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
            },
        accept=".zip",
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.P(id='done-hint3'),
    # html.Label(["\u2700 The Threshold of Word Frequency", dcc.Slider(id='freq-table-slider', min=3, max=50, value=3, marks={str(num): str(num) for num in range(3,51)}, step=None)]),
    html.Label(["\u2700 The Threshold of Word Frequency (minimum value is 3)", dcc.Input(id='freq-table-slider', type='number', min=3)]),
    html.Button('Submit', id='ling_freq', n_clicks=0),
    html.Div(id='output-txtdata-upload'),
    html.Br(),

    html.Br(),
    html.H2(children='Readability \U0001F4D6'),
    html.P("\U0001F514 Please upload a .zip file containing two or more English text files in the .txt format. \U0001F514"),
    html.P("\u26A0 The file names for the text files should consist entirely of Latin characters. \u26A0"),
    dcc.Upload(
        id='upload-txtdata2',
        children=html.Div([
            'Drag and Drop or ', html.A('Select a .zip File')
            ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
            },
        accept=".zip",
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.P(id='done-hint'),
    html.Label(["Please select a readability formula", dcc.Dropdown(options=[{'label': 'Gunning Fog', 'value': 'Gunning Fog'},
                                                                             {'label': "The New Dale-Chall", 'value': "The New Dale-Chall"},
                                                                             {'label':'Flesch Reading Ease score', 'value':'Flesch Reading Ease score'}], 
                                                                    id="formula-selection", placeholder="Select a formula",)]),
    dcc.Store(id='formula_data'),
    html.Div(id='output-txtdata2-upload'),
    dcc.Store(id='formula_data-table'),
    html.Br(),
])

def parse_zip_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    zip_str = io.BytesIO(decoded)
    zip_obj = ZipFile(zip_str, 'r')
    return zip_obj

def parse_excel_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    return df

@app.callback(Output('done-hint3', 'children'),
              Input('upload-txtdata', 'contents'),
              Input('upload-txtdata', 'filename'),
              Input('upload-txtdata', 'last_modified'),
)
def update_ling_uploaded(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        return [html.Mark('Uploaded!', style={"background": "#FAD689","padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",})]

@app.callback(Output('output-txtdata-upload', 'children'),
              Input('upload-txtdata', 'contents'),
              Input('upload-txtdata', 'filename'),
              Input('upload-txtdata', 'last_modified'),
              Input('freq-table-slider', 'value'),
              Input('ling_freq', 'n_clicks'),
)
def update_linguistic_output(list_of_contents, list_of_names, list_of_dates, threshold, n_clicks):
    if n_clicks > 0:
        if list_of_contents is not None:
            children = [
                parse_zip_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]

            txt_files = []
            contents = []
            zipInfo = children[0].infolist()
            for member in zipInfo:
                member.filename = member.filename.encode('cp437').decode('big5')
                txt_files.append(member.filename)
                content = children[0].read(member)
                content = io.StringIO(content.decode('utf-8')).read()
                contents.append(content)
            
            texts = []
            en_txt_files = []

            for i, f in enumerate(txt_files):
                if re.search(r'[\u4e00-\u9fff]+', f) is None:
                    text = " ".join(contents[i].split("\n"))
                    texts.append(text)
                    en_txt_files.append(f)
            
            tokens_count = []
            sents_count = []
            mls = [] ## mean length of sentence
            freq_words_in_text = {}

            verb_ratio = []
            noun_ratio = []
            adj_ratio = []
            adv_ratio = []
            conj_ratio = []
            pron_ratio = []
            num_ratio = []
            prt_ratio = []
            adp_ratio = []

            LD = []
            T = []
            TTR = []
            LV = []
            VV1 = []
            VV2 = []
            NV = []
            AdjV = []
            AdvV = []
            ModV = []

            diff_ws_ratios = []

            for i, t in enumerate(texts):
                pos_text = []
                tokens = []
                content_words = []
                verb_ws = []
                noun_ws = []
                adj_ws = []
                adv_ws = []
                conj_ws = []
                pron_ws = []
                adp_ws = []
                prt_ws = []
                num_ws = []
                for word, pos in nltk.pos_tag(nltk.word_tokenize(t), tagset='universal'): 
                    word = word.lower()
                    if pos == 'ADV':
                        pos_text.append("ADV")
                        tokens.append(word)
                        content_words.append(word)
                        adv_ws.append(word)
                    elif pos == 'ADJ':
                        pos_text.append("ADJ")
                        tokens.append(word)
                        content_words.append(word)
                        adj_ws.append(word)
                    elif pos == 'NOUN':
                        pos_text.append("NOUN")
                        tokens.append(word)
                        content_words.append(word)
                        noun_ws.append(word)
                    elif pos == 'VERB':
                        pos_text.append("VERB")
                        tokens.append(word)
                        content_words.append(word)
                        verb_ws.append(word)
                    elif pos == 'CONJ':
                        pos_text.append("CONJ")
                        tokens.append(word)
                        conj_ws.append(word)
                    elif pos == 'PRON':
                        pos_text.append("PRON")
                        tokens.append(word)
                        pron_ws.append(word)
                    elif pos == 'NUM':
                        pos_text.append("NUM")
                        tokens.append(word)
                        num_ws.append(word)
                    elif pos == 'PRT':
                        pos_text.append("PRT")
                        tokens.append(word)
                        prt_ws.append(word)
                    elif pos == 'ADP':
                        pos_text.append("ADP")
                        tokens.append(word)
                        adp_ws.append(word)
                    elif pos == 'DET':
                        tokens.append(word)
                        
                difficult_ws = [t for t in tokens if textstat.syllable_count(t) >= 2]
                diff_ws_ratio = float(Decimal(float((Decimal(len(difficult_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
                diff_ws_ratios.append(diff_ws_ratio)
                
                verb_ratio.append(float(Decimal(float((Decimal(len(verb_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                noun_ratio.append(float(Decimal(float((Decimal(len(noun_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                adj_ratio.append(float(Decimal(float((Decimal(len(adj_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                adv_ratio.append(float(Decimal(float((Decimal(len(adv_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                conj_ratio.append(float(Decimal(float((Decimal(len(conj_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                pron_ratio.append(float(Decimal(float((Decimal(len(pron_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                num_ratio.append(float(Decimal(float((Decimal(len(adp_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                prt_ratio.append(float(Decimal(float((Decimal(len(prt_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                adp_ratio.append(float(Decimal(float((Decimal(len(num_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                
                freq_words = {}
                stop_words = set(stopwords.words('english'))
                
                for ctoken in content_words:
                    if ctoken not in stop_words:
                        if freq_words.get(ctoken) is None:
                            freq_words[ctoken] = 1
                        else:
                            freq_words[ctoken] += 1
                        
                freq_words_in_text[en_txt_files[i].strip(".txt")] = freq_words
                
                tokens_count.append(len(tokens))
                sents = re.split(r"(?<!\w\.\w.)(?<![A-Z]\.)(?<![A-Z][a-z]\.)(?<=\.|\?)", t)
                sents = [s for s in sents if s != "" and len(s) > 1]
                
                sents_count.append(len(sents))
                mls.append(float(Decimal(float((Decimal(len(tokens))/Decimal(len(sents))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                
                LD.append(float(Decimal(float(Decimal(len(content_words))/Decimal(len(pos_text)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                types = list(set(tokens))
                ttr = float(Decimal(float((Decimal(len(types))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
                T.append(len(types))
                TTR.append(ttr)
                
                if len(verb_ws) == 0:
                    VV1.append(0)
                else:
                    VV1.append(float(Decimal(float(Decimal(len(list(set(verb_ws))))/Decimal(len(verb_ws)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                    
                if len(content_words) == 0:
                    LV.append(0)
                    NV.append(0)
                    AdjV.append(0)
                    AdvV.append(0)
                    ModV.append(0)
                else:
                    LV.append(float(Decimal(float(Decimal(len(list(set(content_words))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                    NV.append(float(Decimal(float(Decimal(len(list(set(noun_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                    AdjV.append(float(Decimal(float(Decimal(len(list(set(adj_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                    AdvV.append(float(Decimal(float(Decimal(len(list(set(adv_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                    ModV.append(float(Decimal(float((Decimal(len(list(set(adv_ws))))+Decimal(len(list(set(adj_ws)))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                
                if len(verb_ws) == 0 or len(content_words) == 0:
                    VV2.append(0)
                else:
                    VV2.append(float(Decimal(float(Decimal(len(list(set(verb_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))

            en_threshold_ws_text = []
            threshold_ws = []
            for v in freq_words_in_text.get(en_txt_files[0].strip(".txt")):
                if freq_words_in_text.get(en_txt_files[0].strip(".txt")).get(v) >= threshold:
                    threshold_ws.append(v)

            en_threshold_ws_text.append(threshold_ws)

            indicators_init = [en_txt_files[0].strip(".txt"), "WC", "SC", "MLS", "VR", "NR", "AdvR", "AdjR", "PronR", "ConjR", "AdpR",
                            "PrtR", "QR", "LD", "NDW", "TTR", "LV", "VV1", "VV2", "NV", "AdjV", "AdvV", "ModV", "DiWR", "HW"]

            quantity_init = [" ", tokens_count[0], sents_count[0], mls[0], 
                            verb_ratio[0], noun_ratio[0], adv_ratio[0], adj_ratio[0],
                            pron_ratio[0], conj_ratio[0], adp_ratio[0], prt_ratio[0], num_ratio[0],
                            LD[0], T[0], TTR[0], LV[0], VV1[0], VV2[0], NV[0], AdjV[0], AdvV[0], ModV[0], diff_ws_ratios[0], ", ".join(threshold_ws)]

            en_df = pd.DataFrame({"Indicator": indicators_init, "Quantity": quantity_init})
            for i, txt_f in enumerate(en_txt_files):
                if i == 0: 
                    pass
                else:
                    threshold_ws = []
                    for v in freq_words_in_text.get(txt_f.strip(".txt")):
                        if freq_words_in_text.get(txt_f.strip(".txt")).get(v) >= threshold:
                            if len(v) > 1:
                                threshold_ws.append(v)
                    en_threshold_ws_text.append(threshold_ws)
                    
                    indicators = [txt_f.strip(".txt"), "WC", "SC", "MLS", "VR", "NR", "AdvR", "AdjR", "PronR", "ConjR", "AdpR",
                                "PrtR", "QR", "LD", "NDW", "TTR", "LV", "VV1", "VV2", "NV", "AdjV", "AdvV", "ModV", "DiWR", "HW"]

                    quantity = [" ", tokens_count[i], sents_count[i], mls[i], 
                                verb_ratio[i], noun_ratio[i], adv_ratio[i], adj_ratio[i],
                                pron_ratio[i], conj_ratio[i], adp_ratio[i], prt_ratio[i], num_ratio[i],
                                LD[i], T[i], TTR[i], LV[i], VV1[i], VV2[i], NV[i], AdjV[i], AdvV[i], ModV[i], diff_ws_ratios[i], ", ".join(threshold_ws)]

                    space = " "
                    en_temp_df = pd.DataFrame({"Indicator"+space*(i+2): indicators, "Quantity"+space*(i+2): quantity})
                    en_df = pd.concat([en_df, en_temp_df], axis=1)

            w_text_names = []
            w_indics = []
            w_quans = []
            s_text_names = []
            s_indics = []
            s_quans = []
            v_text_names = []
            v_indics = []
            v_quans = []
            n_text_names = []
            n_indics = []
            n_quans = []
            ad_text_names = []
            ad_indics = []
            ad_quans = []
            a_text_names = []
            a_indics = []
            a_quans = []
            fc_text_names = []
            fc_indics = []
            fc_quans = []
            lc_text_names = []
            lc_indics = []
            lc_quans = []

            for i, zt in enumerate(en_txt_files):
                w_quans.append(tokens_count[i])
                s_quans.append(sents_count[i])
                s_quans.append(mls[i])
                v_quans.append(verb_ratio[i])
                n_quans.append(noun_ratio[i])
                ad_quans.append(adv_ratio[i])
                a_quans.append(adj_ratio[i])
                fc_quans.append(pron_ratio[i])
                fc_quans.append(conj_ratio[i])
                fc_quans.append(adp_ratio[i])
                fc_quans.append(prt_ratio[i])
                fc_quans.append(num_ratio[i])
                lc_quans.append(LD[i])
                w_quans.append(T[i])
                lc_quans.append(TTR[i])
                lc_quans.append(LV[i])
                v_quans.append(VV1[i])
                v_quans.append(VV2[i])
                n_quans.append(NV[i])
                a_quans.append(AdjV[i])
                ad_quans.append(AdvV[i])
                a_quans.append(ModV[i])
                lc_quans.append(diff_ws_ratios[i])
                for wc in ["WC", "NDW"]:
                    w_text_names.append(zt.strip(".txt"))
                    w_indics.append(wc)
                for sc in ["SC", "MLS"]:
                    s_text_names.append(zt.strip(".txt"))
                    s_indics.append(sc)
                for vc in ["VR", "VV1", "VV2"]:
                    v_text_names.append(zt.strip(".txt"))
                    v_indics.append(vc)
                for nc in ["NR", "NV"]:
                    n_text_names.append(zt.strip(".txt"))
                    n_indics.append(nc)
                for adc in ["AdvR", "AdvV"]:
                    ad_text_names.append(zt.strip(".txt"))
                    ad_indics.append(adc)
                for ac in ["AdjR", "AdjV", "ModV"]:
                    a_text_names.append(zt.strip(".txt"))
                    a_indics.append(ac)
                for fc in ["PronR", "ConjR", "AdpR", "PrtR", "QR"]:
                    fc_text_names.append(zt.strip(".txt"))
                    fc_indics.append(fc)
                for lc in ["LD", "LV", "TTR", "DiWR"]:
                    lc_text_names.append(zt.strip(".txt"))
                    lc_indics.append(lc)
                    
            w_en_treemap_df = pd.DataFrame({"Text":w_text_names, "Indicator":w_indics, "Quantity":w_quans})
            s_en_treemap_df = pd.DataFrame({"Text":s_text_names, "Indicator":s_indics, "Quantity":s_quans})
            v_en_treemap_df = pd.DataFrame({"Text":v_text_names, "Indicator":v_indics, "Quantity":v_quans})
            n_en_treemap_df = pd.DataFrame({"Text":n_text_names, "Indicator":n_indics, "Quantity":n_quans})
            ad_en_treemap_df = pd.DataFrame({"Text":ad_text_names, "Indicator":ad_indics, "Quantity":ad_quans})
            a_en_treemap_df = pd.DataFrame({"Text":a_text_names, "Indicator":a_indics, "Quantity":a_quans})
            fc_en_treemap_df = pd.DataFrame({"Text":fc_text_names, "Indicator":fc_indics, "Quantity":fc_quans})
            lc_en_treemap_df = pd.DataFrame({"Text":lc_text_names, "Indicator":lc_indics, "Quantity":lc_quans})

            return [html.Div(children=[
                        dcc.Loading(id="loading-2", children=[dash_table.DataTable(columns=[{"name": i, "id": i} for i in en_df.columns],
                                                                                    data=en_df.to_dict('records'), export_format='xlsx',
                                                                                    style_cell={'overflow': 'hidden',
                                                                                                'textOverflow': 'ellipsis',
                                                                                                'maxWidth': 0}),], type="default"),
                        dcc.Graph(figure=px.treemap(w_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(s_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(v_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(n_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(ad_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(a_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(fc_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        dcc.Graph(figure=px.treemap(lc_en_treemap_df, path=['Indicator', 'Text'], values='Quantity',color='Text')), 
                        ])]

@app.callback(Output('formula_data', 'value'),
              Output('formula_data-table', 'data'),
              Output('done-hint', 'children'),
              Input('upload-txtdata2', 'contents'),
              Input('upload-txtdata2', 'filename'),
              Input('upload-txtdata2', 'last_modified'),
)
def update_readability(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_zip_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]

        txt_files = []
        contents = []
        zipInfo = children[0].infolist()
        for member in zipInfo:
            member.filename = member.filename.encode('cp437').decode('big5')
            txt_files.append(member.filename)
            content = children[0].read(member)
            content = io.StringIO(content.decode('utf-8')).read()
            contents.append(content)
        
        texts = []
        en_txt_files = []

        x_axis = []

        for i, f in enumerate(txt_files):
            if re.search(r'[\u4e00-\u9fff]+', f) is None:
                text = " ".join(contents[i].split("\n"))
                texts.append(text)
                en_txt_files.append(f)
                x_axis.append(f.strip(".txt"))

        fog_scores = [] 
        dach_scores = []
        flesch_scores = []

        tokens_count = []
        sents_count = []
        mls = []

        verb_ratio = []
        noun_ratio = []
        adj_ratio = []
        adv_ratio = []
        conj_ratio = []
        pron_ratio = []
        num_ratio = []
        prt_ratio = []
        adp_ratio = []

        LD = []
        T = []
        TTR = []
        LV = []
        VV1 = []
        VV2 = []
        NV = []
        AdjV = []
        AdvV = []
        ModV = []

        diff_ws_ratios = []
        odw_ws_ratios = []
        word_scores_ratios = []

        for i, t in enumerate(texts):
            pos_text = []
            tokens = []
            content_words = []
            verb_ws = []
            noun_ws = []
            adj_ws = []
            adv_ws = []
            conj_ws = []
            pron_ws = []
            adp_ws = []
            prt_ws = []
            num_ws = []
            for word, pos in nltk.pos_tag(nltk.word_tokenize(t), tagset='universal'): 
                word = word.lower()
                if pos == 'ADV':
                    pos_text.append("ADV")
                    tokens.append(word)
                    content_words.append(word)
                    adv_ws.append(word)
                elif pos == 'ADJ':
                    pos_text.append("ADJ")
                    tokens.append(word)
                    content_words.append(word)
                    adj_ws.append(word)
                elif pos == 'NOUN':
                    pos_text.append("NOUN")
                    tokens.append(word)
                    content_words.append(word)
                    noun_ws.append(word)
                elif pos == 'VERB':
                    pos_text.append("VERB")
                    tokens.append(word)
                    content_words.append(word)
                    verb_ws.append(word)
                elif pos == 'CONJ':
                    pos_text.append("CONJ")
                    tokens.append(word)
                    conj_ws.append(word)
                elif pos == 'PRON':
                    pos_text.append("PRON")
                    tokens.append(word)
                    pron_ws.append(word)
                elif pos == 'NUM':
                    pos_text.append("NUM")
                    tokens.append(word)
                    num_ws.append(word)
                elif pos == 'PRT':
                    pos_text.append("PRT")
                    tokens.append(word)
                    prt_ws.append(word)
                elif pos == 'ADP':
                    pos_text.append("ADP")
                    tokens.append(word)
                    adp_ws.append(word)
                elif pos == 'DET':
                    tokens.append(word)

            word_scores = []
            odw_ws = []
            for vocab in tokens:
                if vocab in elementary_en_words_list and textstat.syllable_count(vocab) <= 3:
                    word_scores.append(1)
                elif vocab in elementary_en_words_list and textstat.syllable_count(vocab) > 3:
                    word_scores.append(2)
                elif vocab in intermediate_en_words_list and textstat.syllable_count(vocab) < 3:
                    word_scores.append(3)
                elif vocab in intermediate_en_words_list and textstat.syllable_count(vocab) == 3:
                    word_scores.append(4)
                elif vocab in intermediate_en_words_list and textstat.syllable_count(vocab) > 3:
                    word_scores.append(5)
                elif vocab in advanced_en_words_list and textstat.syllable_count(vocab) <= 3:
                    word_scores.append(6)
                elif vocab in advanced_en_words_list and textstat.syllable_count(vocab) > 3:
                    word_scores.append(7)
                else:
                    odw_ws.append(vocab)

            odw_ws_ratio = float(Decimal(float((Decimal(len(odw_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
            word_scores_ratio = float(Decimal(float((Decimal(len(word_scores))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
            odw_ws_ratios.append(odw_ws_ratio)
            word_scores_ratios.append(word_scores_ratio)
                    
            difficult_ws = [t for t in tokens if textstat.syllable_count(t) >= 2]
            diff_ws_ratio = float(Decimal(float((Decimal(len(difficult_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
            diff_ws_ratios.append(diff_ws_ratio)
            sents = re.split(r"(?<!\w\.\w.)(?<![A-Z]\.)(?<![A-Z][a-z]\.)(?<=\.|\?)", t)
            sents = [s for s in sents if s != "" and len(s) > 1]

            msl = float(Decimal(float((Decimal(len(tokens))/Decimal(len(sents))))).quantize(Decimal('.000'), ROUND_HALF_UP))
            fog_score = float(Decimal(0.4)*(Decimal(msl)+(Decimal(100)*Decimal(diff_ws_ratio))))
            difficult_words_per = Decimal(100)-(((Decimal(len(tokens))-Decimal(len(difficult_ws)))/Decimal(len(tokens)))*Decimal(100))
            dach_score = float(Decimal(3.6365)+((Decimal(0.1579)*difficult_words_per)+(Decimal(0.0496)*(Decimal(msl)))))
            flesch_score = textstat.flesch_reading_ease(t)
            fog_scores.append(fog_score)
            dach_scores.append(dach_score)
            flesch_scores.append(flesch_score)

            verb_ratio.append(float(Decimal(float((Decimal(len(verb_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            noun_ratio.append(float(Decimal(float((Decimal(len(noun_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            adj_ratio.append(float(Decimal(float((Decimal(len(adj_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            adv_ratio.append(float(Decimal(float((Decimal(len(adv_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            conj_ratio.append(float(Decimal(float((Decimal(len(conj_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            pron_ratio.append(float(Decimal(float((Decimal(len(pron_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            num_ratio.append(float(Decimal(float((Decimal(len(adp_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            prt_ratio.append(float(Decimal(float((Decimal(len(prt_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            adp_ratio.append(float(Decimal(float((Decimal(len(num_ws))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            
            tokens_count.append(len(tokens))
            sents = re.split(r"(?<!\w\.\w.)(?<![A-Z]\.)(?<![A-Z][a-z]\.)(?<=\.|\?)", t)
            sents = [s for s in sents if s != "" and len(s) > 1]
            
            sents_count.append(len(sents))
            mls.append(float(Decimal(float((Decimal(len(tokens))/Decimal(len(sents))))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            LD.append(float(Decimal(float(Decimal(len(content_words))/Decimal(len(pos_text)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            types = list(set(tokens))
            ttr = float(Decimal(float((Decimal(len(types))/Decimal(len(tokens))))).quantize(Decimal('.000'), ROUND_HALF_UP))
            T.append(len(types))
            TTR.append(ttr)
            
            if len(verb_ws) == 0:
                VV1.append(0)
            else:
                VV1.append(float(Decimal(float(Decimal(len(list(set(verb_ws))))/Decimal(len(verb_ws)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                
            if len(content_words) == 0:
                LV.append(0)
                NV.append(0)
                AdjV.append(0)
                AdvV.append(0)
                ModV.append(0)
            else:
                LV.append(float(Decimal(float(Decimal(len(list(set(content_words))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                NV.append(float(Decimal(float(Decimal(len(list(set(noun_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                AdjV.append(float(Decimal(float(Decimal(len(list(set(adj_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                AdvV.append(float(Decimal(float(Decimal(len(list(set(adv_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
                ModV.append(float(Decimal(float((Decimal(len(list(set(adv_ws))))+Decimal(len(list(set(adj_ws)))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))
            
            if len(verb_ws) == 0 or len(content_words) == 0:
                VV2.append(0)
            else:
                VV2.append(float(Decimal(float(Decimal(len(list(set(verb_ws))))/Decimal(len(content_words)))).quantize(Decimal('.000'), ROUND_HALF_UP)))

        indicators_init = ["WC", "SC", "MLS", "VR", "NR", "AdvR", "AdjR", "PronR", "ConjR", "AdpR",
                        "PrtR", "QR", "LD", "NDW", "TTR", "LV", "VV1", "VV2", "NV", "AdjV", "AdvV", "ModV", "DiWR", "AWLS", "ODWR"]

        quantity_init = [tokens_count[0], sents_count[0], mls[0], 
                        verb_ratio[0], noun_ratio[0], adv_ratio[0], adj_ratio[0],
                        pron_ratio[0], conj_ratio[0], adp_ratio[0], prt_ratio[0], num_ratio[0],
                        LD[0], T[0], TTR[0], LV[0], VV1[0], VV2[0], NV[0], AdjV[0], AdvV[0], ModV[0], 
                        diff_ws_ratios[0], word_scores_ratios[0], odw_ws_ratios[0]]

        en_df = pd.DataFrame({en_txt_files[0].strip(".txt"): indicators_init, en_txt_files[0].strip(".txt")+"_Quantity": quantity_init})
        
        for i, txt_f in enumerate(en_txt_files):
            if i == 0: 
                pass
            else:
                indicators = ["WC", "SC", "MLS", "VR", "NR", "AdvR", "AdjR", "PronR", "ConjR", "AdpR",
                            "PrtR", "QR", "LD", "NDW", "TTR", "LV", "VV1", "VV2", "NV", "AdjV", "AdvV", "ModV", "DiWR", "AWLS", "ODWR"]

                quantity = [tokens_count[i], sents_count[i], mls[i], 
                            verb_ratio[i], noun_ratio[i], adv_ratio[i], adj_ratio[i],
                            pron_ratio[i], conj_ratio[i], adp_ratio[i], prt_ratio[i], num_ratio[i],
                            LD[i], T[i], TTR[i], LV[i], VV1[i], VV2[i], NV[i], AdjV[i], AdvV[i], ModV[i], 
                            diff_ws_ratios[i], word_scores_ratios[i], odw_ws_ratios[i]]

                space = " "
                en_temp_df = pd.DataFrame({txt_f.strip(".txt"): indicators, txt_f.strip(".txt")+"_Quantity": quantity})
                en_df = pd.concat([en_df, en_temp_df], axis=1)
        
        fog_data = [{'x': x_axis, 'y': fog_scores, 'type': 'bar'}]
        dach_data = [{'x': x_axis, 'y': dach_scores, 'type': 'bar'}]
        flesch_data = [{'x': x_axis, 'y': flesch_scores, 'type': 'bar'}]
        
        return [fog_data, dach_data, flesch_data], en_df.to_json(orient="columns"), [html.Mark('Uploaded!', style={"background": "#FAD689","padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",})]

@app.callback(Output('output-txtdata2-upload', 'children'),
              Input('formula_data', 'value'),
              Input('formula-selection', 'value'),
)
def update_readability_graph(data, formula_selected):
    if formula_selected == "Gunning Fog":
        output_data = data[0]
        fig = go.Bar(x=output_data[0].get("x"), y=output_data[0].get("y"), 
                    marker_color=[random.choice(mark_colors_graph) for i in range(len(output_data[0].get("x")))], 
                    text=[round(d, 3) for d in output_data[0].get("y")], textposition="outside")
        title = "Gunning Fog"
        layout =  go.Layout(title=title,
                            margin={'l': 40, 'b': 60, 't': 50, 'r': 50},
                            xaxis={'title': 'Text'},
                            yaxis={'title': 'Score'},
                            hovermode='closest', 
                            uniformtext_minsize=8, uniformtext_mode='hide')
        desc_df = fog_df
    elif formula_selected == "The New Dale-Chall":
        output_data = data[1]
        fig = go.Bar(x=output_data[0].get("x"), y=output_data[0].get("y"), 
                    marker_color=[random.choice(mark_colors_graph) for i in range(len(output_data[0].get("x")))], 
                    text=[round(d, 3) for d in output_data[0].get("y")], textposition="outside")
        title = "The New Dale-Chall"
        layout =  go.Layout(title=title,
                            margin={'l': 40, 'b': 60, 't': 50, 'r': 50},
                            xaxis={'title': 'Text'},
                            yaxis={'title': 'Score'},
                            hovermode='closest', 
                            uniformtext_minsize=8, uniformtext_mode='hide')
        desc_df = dach_df
    
    elif formula_selected == "Flesch Reading Ease score":
        output_data = data[2]
        fig = go.Bar(x=output_data[0].get("x"), y=output_data[0].get("y"), 
                    marker_color=[random.choice(mark_colors_graph) for i in range(len(output_data[0].get("x")))], 
                    text=[round(d, 0) for d in output_data[0].get("y")], textposition="outside")
        title = "Flesch Reading Ease score"
        layout =  go.Layout(title=title,
                            margin={'l': 40, 'b': 60, 't': 50, 'r': 50},
                            xaxis={'title': 'Text'},
                            yaxis={'title': 'Score'},
                            hovermode='closest', 
                            uniformtext_minsize=8, uniformtext_mode='hide')
        desc_df = flesch_df

    return [html.Div(children=[
                        dcc.Graph(figure={'data': [fig],
                                         'layout': layout}
                                         ),
                        html.Br(),
                        dash_table.DataTable(columns=[{"name": i, "id": i} for i in desc_df.columns],
                                                data=desc_df.to_dict('records'),
                                                style_data={'height': '5px',},),
                        html.Br(),
                        html.H4("Create your own diversity formula! \U0001F4CF"),
                        html.H5("Example formula: 0.3588*AWLS+0.2377*MLS+0.3524*DiWR+0.0206*TTR+0.0305*ODWR"),
                        html.P('\U0001F538 The AWLS is an indicator of the average word level score of each word. The word level score is determined by evaluating if a word is at the Elementary level of GEPT and if the syllabus count is less than 3, the word will be scored as one point. There are seven levels in total, and the score increases as the level increases.'),
                        html.P('\U0001F538 The out-of-dictionary word ratio (ODWR) indicates the ratio of out-of-dictionary (GEPT) words to total words.'),
                        html.P('\U0001F538 The total weight is capped at 1.'),
                        html.Label(["Description of the example rubrics:",
                                    dash_table.DataTable(columns=[{"name": i, "id": i} for i in fm_df.columns],
                                                        data=fm_df.to_dict('records'),
                                                        style_data={'height': '5px',},
                                                        )]),
                        
                        html.Label(["Please choose the number of features you would like to take into consideration. ",
                                    dcc.Dropdown(options=[{'label': i, 'value': i} for i in range(2,7)], 
                                                placeholder="Please choose the number of features you would like to take into consideration. ",
                                                id="feature-num-selection")]),
                        html.Div(id="features-weights-selection"),
                        html.Div(id="self-formula"),
                        html.Div(id="self-formula-2results"),
                        html.Div(id="self-formula-3results"),
                        html.Div(id="self-formula-4results"),
                        html.Div(id="self-formula-5results"),
                        html.Div(id="self-formula-6results"),
                        ])]

@app.callback(Output('features-weights-selection', 'children'),
              Input('formula_data-table', 'data'),
              Input('feature-num-selection', 'value')
)
def update_features_selection_dropdown(records, feature_num):
    records = ast.literal_eval(records)
    columns = []
    contents = []
    for r in records:
        columns.append(r)
        values = records.get(r)
        temp = []
        for i in values:
            temp.append(values.get(i))
        contents.append(temp)

    output_content = {}
    for i, c in enumerate(columns):
        output_content[c] = contents[i]

    df = pd.DataFrame(output_content)
    all_features = list(df[columns[0]])
    dropdown_output = []

    for i in range(int(feature_num)):
        dropdown_output.append(html.Label(["Feature "+str(i+1), 
                                            dcc.Dropdown(options=[{'label': i, 'value': i} for i in all_features], 
                                                        placeholder="Select a feature",
                                                        id="feature-selection"+str(i+1))]))
        dropdown_output.append(html.Label(["Weight "+str(i+1), 
                                            dcc.Input(id='weights-selection'+str(i+1), type='number')]))
        dropdown_output.append(html.P(id="selection-descr"+str(i+1)))
        dropdown_output.append(dcc.Store(id='resi-quota'+str(i+1)))

    dropdown_output.append(html.Label(["Make Your Formula a Name! \U0001F52E", 
                                        dcc.Input(id='formula_name', type='text')]))
    dropdown_output.append(html.Button('Submit', id='formula-finished', n_clicks=0))
    
    return dropdown_output

@app.callback(Output('selection-descr1', 'children'),
              Output('resi-quota1', 'value'),
              Input('feature-selection1', 'value'),
              Input('weights-selection1', 'value'),
)
def update_1feature_weights_selection(f1, w1):
    if f1 is not None and w1 is not None:
        quota = float(Decimal("1") - Decimal(str(w1)))
        return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f1, w=w1, q=quota)], quota

@app.callback(Output('selection-descr2', 'children'),
              Output('resi-quota2', 'value'),
              Input('feature-selection2', 'value'),
              Input('weights-selection2', 'value'),
              Input('resi-quota1', 'value'),
)
def update_2feature_weights_selection(f2, w2, rq1):
    if f2 is not None and w2 is not None:
        if rq1 is None:
            return ["Please select the first feature in advance!"], 0
        else:
            quota = float(Decimal(str(rq1)) - Decimal(str(w2)))
            return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f2, w=w2, q=quota)], quota

@app.callback(Output('selection-descr3', 'children'),
              Output('resi-quota3', 'value'),
              Input('feature-selection3', 'value'),
              Input('weights-selection3', 'value'),
              Input('resi-quota2', 'value'),
)
def update_3feature_weights_selection(f3, w3, rq2):
    if f3 is not None and w3 is not None:
        if rq2 is None:
            return ["Please select the second feature!"], 0
        else:
            quota = float(Decimal(str(rq2)) - Decimal(str(w3)))
            return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f3, w=w3, q=quota)], quota

@app.callback(Output('selection-descr4', 'children'),
              Output('resi-quota4', 'value'),
              Input('feature-selection4', 'value'),
              Input('weights-selection4', 'value'),
              Input('resi-quota3', 'value'),
)
def update_4feature_weights_selection(f4, w4, rq3):
    if f4 is not None and w4 is not None:
        if rq3 is None:
            return ["Please select the third feature!"], 0
        else:
            quota = float(Decimal(str(rq3)) - Decimal(str(w4)))
            return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f4, w=w4, q=quota)], quota

@app.callback(Output('selection-descr5', 'children'),
              Output('resi-quota5', 'value'),
              Input('feature-selection5', 'value'),
              Input('weights-selection5', 'value'),
              Input('resi-quota4', 'value'),
)
def update_5feature_weights_selection(f5, w5, rq4):
    if f5 is not None and w5 is not None:
        if rq4 is None:
            return ["Please select the fourth feature!"], 0
        else:
            quota = float(Decimal(str(rq4)) - Decimal(str(w5)))
            return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f5, w=w5, q=quota)], quota

@app.callback(Output('selection-descr6', 'children'),
              Output('resi-quota6', 'value'),
              Input('feature-selection6', 'value'),
              Input('weights-selection6', 'value'),
              Input('resi-quota5', 'value'),
)
def update_6feature_weights_selection(f6, w6, rq5):
    if f6 is not None and w6 is not None:
        if rq5 is None:
            return ["Please select the fifth feature!"], 0
        else:
            quota = float(Decimal(str(rq5)) - Decimal(str(w6)))
            return ["The selected feature is {f}, with a weight of {w}, and a quota of {q}.".format(f=f6, w=w6, q=quota)], quota

@app.callback(Output('self-formula-2results', 'children'),
              Input('formula-finished', 'n_clicks'),
              Input('formula_data-table', 'data'),
              Input('feature-selection1', 'value'),
              Input('feature-selection2', 'value'),
              Input('weights-selection1', 'value'),
              Input('weights-selection2', 'value'),
              Input('resi-quota1', 'value'),
              Input('resi-quota2', 'value'),
              Input("formula_name", "value"),
              Input('feature-num-selection', 'value')
)
def update_formula_2results(n_clicks, records, f1, f2, w1, w2, rq1, rq2, formula_name, features_num):
    if n_clicks > 0:
        if int(features_num) == 2:
            records = ast.literal_eval(records)
            columns = []
            contents = []
            for r in records:
                columns.append(r)
                values = records.get(r)
                temp = []
                for i in values:
                    temp.append(values.get(i))
                contents.append(temp)

            output_content = {}
            for i, c in enumerate(columns):
                output_content[c] = contents[i]

            df = pd.DataFrame(output_content)

            self_formula_scores1 = []
            self_formula_scores2 = []
            zh_columns = []
            en_columns = []
            plot_data = []
            if w1 is None or w2 is None or f1 is None or f2 is None:
                return ["\u2757 Please finish the formula!"]
            elif float(w1) < 0 or float(w2) < 0:
                return ["\u2757 Please set the weight to be greater than 0!"]
            elif float(w1) > 1 or float(w2) > 1:
                return ["\u2757 Please set the weight to be smaller than 1!"]
            elif float(rq1) < 0 or float(rq2) < 0:
                return ["\u2757 The total weight is limited to 1. Your total weight is greater than 1."]
            elif len(list(set([f1,f2]))) < int(features_num):
                return ["\u2757 Please don't choose duplicate features."]
            else:
                final_formula = str(w1)+"*"+f1+"+"+str(w2)+"*"+f2
                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c) is None:
                        if re.search("_Quantity", c): pass
                        else: en_columns.append(c)

                for ec in en_columns:
                    for i, indicator in enumerate(df[ec]):
                        if indicator == f1:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                            else:
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                        elif indicator == f2:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                            else:
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)


                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c):
                        if re.search("_Quantity", c): pass
                        else: zh_columns.append(c)
                
                for zc in zh_columns:
                    for i, indicator in enumerate(df[zc]):
                        if indicator == f1:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                        elif indicator == f2:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)

            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores1, name=f1, marker_color='rgb(158,202,225)', text=self_formula_scores1, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores2, name=f2, marker_color='#DB4D6D', text=self_formula_scores2, textposition="inside"))

            if formula_name is None:
                formula_name = "Testing"
            
            layout =  go.Layout(title='Reading Ease Score of '+formula_name,
                                xaxis={'title': 'Text'},
                                yaxis={'title': 'Score'},
                                margin={'l': 50, 'b': 60, 't': 50, 'r': 50},
                                hovermode='closest', barmode='stack',
                                uniformtext_minsize=8, uniformtext_mode='hide')
            figure = go.Figure(data=plot_data, layout=layout)

            total_scores = [round(self_formula_scores1[i]+self_formula_scores2[i],3) for i in range(len(self_formula_scores1))]
            formula_score_df = pd.DataFrame({"Text":en_columns+zh_columns, f1:self_formula_scores1, f2:self_formula_scores2, "Total Score":total_scores})
            features_df = formula_score_df.reindex(sorted(formula_score_df.columns[1:-1]), axis=1)
            head_df = formula_score_df[formula_score_df.columns[0]].to_frame()
            end_df = formula_score_df[formula_score_df.columns[-1]].to_frame()
            formula_score_df = pd.concat([head_df, features_df, end_df], axis=1)
            
            return html.Div([html.Mark("Your formula - "+formula_name+" is: "+final_formula, style={"background": random.choice(mark_colors_text),"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                            dcc.Graph(figure={'data': plot_data,'layout': layout,}),
                            html.Br(),
                            dash_table.DataTable(columns=[{"name": i, "id": i} for i in formula_score_df.columns],
                                                data=formula_score_df.to_dict('records'), export_format='xlsx',
                                                style_cell={'overflow': 'hidden',
                                                            'textOverflow': 'ellipsis',
                                                            'maxWidth': 0})])
        
@app.callback(Output('self-formula-3results', 'children'),
              Input('formula-finished', 'n_clicks'),
              Input('formula_data-table', 'data'),
              Input('feature-selection1', 'value'),
              Input('feature-selection2', 'value'),
              Input('feature-selection3', 'value'),
              Input('weights-selection1', 'value'),
              Input('weights-selection2', 'value'),
              Input('weights-selection3', 'value'),
              Input('resi-quota1', 'value'),
              Input('resi-quota2', 'value'),
              Input('resi-quota3', 'value'),
              Input("formula_name", "value"),
              Input('feature-num-selection', 'value')
)
def update_formula_5results(n_clicks, records, f1, f2, f3, w1, w2, w3, rq1, rq2, rq3, formula_name, features_num):
    if n_clicks > 0:
        if int(features_num) == 3:
            records = ast.literal_eval(records)
            columns = []
            contents = []
            for r in records:
                columns.append(r)
                values = records.get(r)
                temp = []
                for i in values:
                    temp.append(values.get(i))
                contents.append(temp)

            output_content = {}
            for i, c in enumerate(columns):
                output_content[c] = contents[i]

            df = pd.DataFrame(output_content)

            self_formula_scores1 = []
            self_formula_scores2 = []
            self_formula_scores3 = []
            zh_columns = []
            en_columns = []
            plot_data = []
            if w1 is None or w2 is None or w3 is None or f1 is None or f2 is None or f3 is None:
                return ["\u2757 Please finish the formula!"]
            elif float(w1) < 0 or float(w2) < 0 or float(w3) < 0:
                return ["\u2757 Please set the weight to be greater than 0!"]
            elif float(w1) > 1 or float(w2) > 1 or float(w3) > 1:
                return ["\u2757 Please set the weight to be smaller than 1!"]
            elif float(rq1) < 0 or float(rq2) < 0 or float(rq3) < 0:
                return ["\u2757 The total weight is limited to 1. Your total weight is greater than 1."]
            elif len(list(set([f1,f2,f3]))) < int(features_num):
                return ["\u2757 Please don't choose duplicate features."]
            else:
                final_formula = str(w1)+"*"+f1+"+"+str(w2)+"*"+f2+"+"+str(w3)+"*"+f3
                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c) is None:
                        if re.search("_Quantity", c): pass
                        else: en_columns.append(c)

                for ec in en_columns:
                    for i, indicator in enumerate(df[ec]):
                        if indicator == f1:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                            else:
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                        elif indicator == f2:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                            else:
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                        elif indicator == f3:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                            else:
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)


                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c):
                        if re.search("_Quantity", c): pass
                        else: zh_columns.append(c)
                
                for zc in zh_columns:
                    for i, indicator in enumerate(df[zc]):
                        if indicator == f1:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                        elif indicator == f2:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                        elif indicator == f3:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
            
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores1, name=f1, marker_color='rgb(158,202,225)', text=self_formula_scores1, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores2, name=f2, marker_color='#DB4D6D', text=self_formula_scores2, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores3, name=f3, marker_color='#986DB2', text=self_formula_scores3, textposition="inside"))

            if formula_name is None:
                formula_name = "Testing"
            
            layout =  go.Layout(title='Reading Ease Score of '+formula_name,
                                xaxis={'title': 'Text'},
                                yaxis={'title': 'Score'},
                                margin={'l': 50, 'b': 60, 't': 50, 'r': 50},
                                hovermode='closest', barmode='stack',
                                uniformtext_minsize=8, uniformtext_mode='hide')
            figure = go.Figure(data=plot_data, layout=layout)

            total_scores = [round(self_formula_scores1[i]+self_formula_scores2[i]+self_formula_scores3[i],3) for i in range(len(self_formula_scores1))]
            formula_score_df = pd.DataFrame({"Text":en_columns+zh_columns, f1:self_formula_scores1, f2:self_formula_scores2,
                                            f3:self_formula_scores3, "Total Score":total_scores})
            features_df = formula_score_df.reindex(sorted(formula_score_df.columns[1:-1]), axis=1)
            head_df = formula_score_df[formula_score_df.columns[0]].to_frame()
            end_df = formula_score_df[formula_score_df.columns[-1]].to_frame()
            formula_score_df = pd.concat([head_df, features_df, end_df], axis=1)
            
            return html.Div([html.Mark("Your formula - "+formula_name+" is: "+final_formula, style={"background": random.choice(mark_colors_text),"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                            dcc.Graph(figure={'data': plot_data,'layout': layout,}),
                            html.Br(),
                            dash_table.DataTable(columns=[{"name": i, "id": i} for i in formula_score_df.columns],
                                                data=formula_score_df.to_dict('records'), export_format='xlsx',
                                                style_cell={'overflow': 'hidden',
                                                            'textOverflow': 'ellipsis',
                                                            'maxWidth': 0})])

@app.callback(Output('self-formula-4results', 'children'),
              Input('formula-finished', 'n_clicks'),
              Input('formula_data-table', 'data'),
              Input('feature-selection1', 'value'),
              Input('feature-selection2', 'value'),
              Input('feature-selection3', 'value'),
              Input('feature-selection4', 'value'),

              Input('weights-selection1', 'value'),
              Input('weights-selection2', 'value'),
              Input('weights-selection3', 'value'),
              Input('weights-selection4', 'value'),

              Input('resi-quota1', 'value'),
              Input('resi-quota2', 'value'),
              Input('resi-quota3', 'value'),
              Input('resi-quota4', 'value'),

              Input("formula_name", "value"),
              Input('feature-num-selection', 'value')
)
def update_formula_4results(n_clicks, records, f1, f2, f3, f4, w1, w2, w3, w4, rq1, rq2, rq3, rq4, formula_name, features_num):
    if n_clicks > 0:
        if int(features_num) == 4:
            records = ast.literal_eval(records)
            columns = []
            contents = []
            for r in records:
                columns.append(r)
                values = records.get(r)
                temp = []
                for i in values:
                    temp.append(values.get(i))
                contents.append(temp)

            output_content = {}
            for i, c in enumerate(columns):
                output_content[c] = contents[i]

            df = pd.DataFrame(output_content)

            self_formula_scores1 = []
            self_formula_scores2 = []
            self_formula_scores3 = []
            self_formula_scores4 = []
            zh_columns = []
            en_columns = []
            plot_data = []
            if w1 is None or w2 is None or w3 is None or w4 is None or f1 is None or f2 is None or f3 is None or f4 is None:
                return ["\u2757 Please finish the formula!"]
            elif float(w1) < 0 or float(w2) < 0 or float(w3) < 0 or float(w4) < 0:
                return ["\u2757 Please set the weight to be greater than 0!"]
            elif float(w1) > 1 or float(w2) > 1 or float(w3) > 1 or float(w4) > 1:
                return ["\u2757 Please set the weight to be smaller than 1!"]
            elif float(rq1) < 0 or float(rq2) < 0 or float(rq3) < 0 or float(rq4) < 0:
                return ["\u2757 The total weight is limited to 1. Your total weight is greater than 1."]
            elif len(list(set([f1,f2,f3,f4]))) < int(features_num):
                return ["\u2757 Please don't choose duplicate features."]
            else:
                final_formula = str(w1)+"*"+f1+"+"+str(w2)+"*"+f2+"+"+str(w3)+"*"+f3+"+"+str(w4)+"*"+f4
                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c) is None:
                        if re.search("_Quantity", c): pass
                        else: en_columns.append(c)

                for ec in en_columns:
                    for i, indicator in enumerate(df[ec]):
                        if indicator == f1:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                            else:
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                        elif indicator == f2:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                            else:
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                        elif indicator == f3:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                            else:
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                        elif indicator == f4:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)
                            else:
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)


                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c):
                        if re.search("_Quantity", c): pass
                        else: zh_columns.append(c)
                
                for zc in zh_columns:
                    for i, indicator in enumerate(df[zc]):
                        if indicator == f1:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                        elif indicator == f2:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                        elif indicator == f3:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                        elif indicator == f4:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
            
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores1, name=f1, marker_color='rgb(158,202,225)', text=self_formula_scores1, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores2, name=f2, marker_color='#DB4D6D', text=self_formula_scores2, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores3, name=f3, marker_color='#986DB2', text=self_formula_scores3, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores4, name=f4, marker_color='#EEA9A9', text=self_formula_scores4, textposition="inside"))

            if formula_name is None:
                formula_name = "Testing"
            
            layout =  go.Layout(title='Reading Ease Score of '+formula_name,
                                xaxis={'title': 'Text'},
                                yaxis={'title': 'Score'},
                                margin={'l': 50, 'b': 60, 't': 50, 'r': 50},
                                hovermode='closest', barmode='stack',
                                uniformtext_minsize=8, uniformtext_mode='hide')
            figure = go.Figure(data=plot_data, layout=layout)

            total_scores = [round(self_formula_scores1[i]+self_formula_scores2[i]+self_formula_scores3[i]+self_formula_scores4[i],3) for i in range(len(self_formula_scores1))]
            formula_score_df = pd.DataFrame({"Text":en_columns+zh_columns, f1:self_formula_scores1, f2:self_formula_scores2,
                                            f3:self_formula_scores3, f4:self_formula_scores4, "Total Score":total_scores})
            features_df = formula_score_df.reindex(sorted(formula_score_df.columns[1:-1]), axis=1)
            head_df = formula_score_df[formula_score_df.columns[0]].to_frame()
            end_df = formula_score_df[formula_score_df.columns[-1]].to_frame()
            formula_score_df = pd.concat([head_df, features_df, end_df], axis=1)
            
            return html.Div([html.Mark("Your formula - "+formula_name+" is: "+final_formula, style={"background": random.choice(mark_colors_text),"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                            dcc.Graph(figure={'data': plot_data,'layout': layout,}),
                            html.Br(),
                            dash_table.DataTable(columns=[{"name": i, "id": i} for i in formula_score_df.columns],
                                                data=formula_score_df.to_dict('records'), export_format='xlsx',
                                                style_cell={'overflow': 'hidden',
                                                            'textOverflow': 'ellipsis',
                                                            'maxWidth': 0})])

@app.callback(Output('self-formula-5results', 'children'),
              Input('formula-finished', 'n_clicks'),
              Input('formula_data-table', 'data'),
              Input('feature-selection1', 'value'),
              Input('feature-selection2', 'value'),
              Input('feature-selection3', 'value'),
              Input('feature-selection4', 'value'),
              Input('feature-selection5', 'value'),

              Input('weights-selection1', 'value'),
              Input('weights-selection2', 'value'),
              Input('weights-selection3', 'value'),
              Input('weights-selection4', 'value'),
              Input('weights-selection5', 'value'),

              Input('resi-quota1', 'value'),
              Input('resi-quota2', 'value'),
              Input('resi-quota3', 'value'),
              Input('resi-quota4', 'value'),
              Input('resi-quota5', 'value'),

              Input("formula_name", "value"),
              Input('feature-num-selection', 'value')
)
def update_formula_5results(n_clicks, records, f1, f2, f3, f4, f5, w1, w2, w3, w4, w5, rq1, rq2, rq3, rq4, rq5, formula_name, features_num):
    if n_clicks > 0:
        if int(features_num) == 5:
            records = ast.literal_eval(records)
            columns = []
            contents = []
            for r in records:
                columns.append(r)
                values = records.get(r)
                temp = []
                for i in values:
                    temp.append(values.get(i))
                contents.append(temp)

            output_content = {}
            for i, c in enumerate(columns):
                output_content[c] = contents[i]

            df = pd.DataFrame(output_content)

            self_formula_scores1 = []
            self_formula_scores2 = []
            self_formula_scores3 = []
            self_formula_scores4 = []
            self_formula_scores5 = []
            zh_columns = []
            en_columns = []
            plot_data = []
            if w1 is None or w2 is None or w3 is None or w4 is None or w5 is None or f1 is None or f2 is None or f3 is None or f4 is None or f5 is None:
                return ["\u2757 Please finish the formula!"]
            elif float(w1) < 0 or float(w2) < 0 or float(w3) < 0 or float(w4) < 0 or float(w5) < 0:
                return ["\u2757 Please set the weight to be greater than 0!"]
            elif float(w1) > 1 or float(w2) > 1 or float(w3) > 1 or float(w4) > 1 or float(w5) > 1:
                return ["\u2757 Please set the weight to be smaller than 1!"]
            elif float(rq1) < 0 or float(rq2) < 0 or float(rq3) < 0 or float(rq4) < 0 or float(rq5) < 0:
                return ["\u2757 The total weight is limited to 1. Your total weight is greater than 1."]
            elif len(list(set([f1,f2,f3,f4,f5]))) < int(features_num):
                return ["\u2757 Please don't choose duplicate features."]
            else:
                final_formula = str(w1)+"*"+f1+"+"+str(w2)+"*"+f2+"+"+str(w3)+"*"+f3+"+"+str(w4)+"*"+f4+"+"+str(w5)+"*"+f5
                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c) is None:
                        if re.search("_Quantity", c): pass
                        else: en_columns.append(c)

                for ec in en_columns:
                    for i, indicator in enumerate(df[ec]):
                        if indicator == f1:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                            else:
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                        elif indicator == f2:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                            else:
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                        elif indicator == f3:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                            else:
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                        elif indicator == f4:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)
                            else:
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)
                        elif indicator == f5:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores5.append(score)
                            else:
                                score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores5.append(score)


                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c):
                        if re.search("_Quantity", c): pass
                        else: zh_columns.append(c)
                
                for zc in zh_columns:
                    for i, indicator in enumerate(df[zc]):
                        if indicator == f1:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                        elif indicator == f2:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                        elif indicator == f3:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                        elif indicator == f4:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                        elif indicator == f5:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                                else:
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                                else:
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
            
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores1, name=f1, marker_color='rgb(158,202,225)', text=self_formula_scores1, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores2, name=f2, marker_color='#DB4D6D', text=self_formula_scores2, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores3, name=f3, marker_color='#986DB2', text=self_formula_scores3, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores4, name=f4, marker_color='#EEA9A9', text=self_formula_scores4, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores5, name=f5, marker_color='#89916B', text=self_formula_scores5, textposition="inside"))

            if formula_name is None:
                formula_name = "Testing"
            
            layout =  go.Layout(title='Reading Ease Score of '+formula_name,
                                xaxis={'title': 'Text'},
                                yaxis={'title': 'Score'},
                                margin={'l': 50, 'b': 60, 't': 50, 'r': 50},
                                hovermode='closest', barmode='stack',
                                uniformtext_minsize=8, uniformtext_mode='hide')
            figure = go.Figure(data=plot_data, layout=layout)

            total_scores = [round(self_formula_scores1[i]+self_formula_scores2[i]+self_formula_scores3[i]+self_formula_scores4[i]+self_formula_scores5[i],3) for i in range(len(self_formula_scores1))]
            formula_score_df = pd.DataFrame({"Text":en_columns+zh_columns, f1:self_formula_scores1, f2:self_formula_scores2,
                                            f3:self_formula_scores3, f4:self_formula_scores4, f5:self_formula_scores5, "Total Score":total_scores})
            features_df = formula_score_df.reindex(sorted(formula_score_df.columns[1:-1]), axis=1)
            head_df = formula_score_df[formula_score_df.columns[0]].to_frame()
            end_df = formula_score_df[formula_score_df.columns[-1]].to_frame()
            formula_score_df = pd.concat([head_df, features_df, end_df], axis=1)
            
            return html.Div([html.Mark("Your formula - "+formula_name+" is: "+final_formula, style={"background": random.choice(mark_colors_text),"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                            dcc.Graph(figure={'data': plot_data,'layout': layout,}),
                            html.Br(),
                            dash_table.DataTable(columns=[{"name": i, "id": i} for i in formula_score_df.columns],
                                                data=formula_score_df.to_dict('records'), export_format='xlsx',
                                                style_cell={'overflow': 'hidden',
                                                            'textOverflow': 'ellipsis',
                                                            'maxWidth': 0})])

@app.callback(Output('self-formula-6results', 'children'),
              Input('formula-finished', 'n_clicks'),
              Input('formula_data-table', 'data'),
              Input('feature-selection1', 'value'),
              Input('feature-selection2', 'value'),
              Input('feature-selection3', 'value'),
              Input('feature-selection4', 'value'),
              Input('feature-selection5', 'value'),
              Input('feature-selection6', 'value'),

              Input('weights-selection1', 'value'),
              Input('weights-selection2', 'value'),
              Input('weights-selection3', 'value'),
              Input('weights-selection4', 'value'),
              Input('weights-selection5', 'value'),
              Input('weights-selection6', 'value'),

              Input('resi-quota1', 'value'),
              Input('resi-quota2', 'value'),
              Input('resi-quota3', 'value'),
              Input('resi-quota4', 'value'),
              Input('resi-quota5', 'value'),
              Input('resi-quota6', 'value'),

              Input("formula_name", "value"),
              Input('feature-num-selection', 'value')
)
def update_formula_6results(n_clicks, records, f1, f2, f3, f4, f5, f6, w1, w2, w3, w4, w5, w6, rq1, rq2, rq3, rq4, rq5, rq6, formula_name, features_num):
    if n_clicks > 0:
        if int(features_num) == 6:
            records = ast.literal_eval(records)
            columns = []
            contents = []
            for r in records:
                columns.append(r)
                values = records.get(r)
                temp = []
                for i in values:
                    temp.append(values.get(i))
                contents.append(temp)

            output_content = {}
            for i, c in enumerate(columns):
                output_content[c] = contents[i]

            df = pd.DataFrame(output_content)

            self_formula_scores1 = []
            self_formula_scores2 = []
            self_formula_scores3 = []
            self_formula_scores4 = []
            self_formula_scores5 = []
            self_formula_scores6 = []
            zh_columns = []
            en_columns = []
            plot_data = []
            if w1 is None or w2 is None or w3 is None or w4 is None or w5 is None or w6 is None or f1 is None or f2 is None or f3 is None or f4 is None or f5 is None or f6 is None:
                return ["\u2757 Please finish the formula!"]
            elif float(w1) < 0 or float(w2) < 0 or float(w3) < 0 or float(w4) < 0 or float(w5) < 0 or float(w6) < 0:
                return ["\u2757 Please set the weight to be greater than 0!"]
            elif float(w1) > 1 or float(w2) > 1 or float(w3) > 1 or float(w4) > 1 or float(w5) > 1 or float(w6) > 1:
                return ["\u2757 Please set the weight to be smaller than 1!"]
            elif float(rq1) < 0 or float(rq2) < 0 or float(rq3) < 0 or float(rq4) < 0 or float(rq5) < 0 or float(rq6) < 0:
                return ["\u2757 The total weight is limited to 1. Your total weight is greater than 1."]
            elif len(list(set([f1,f2,f3,f4,f5,f6]))) < int(features_num):
                return ["\u2757 Please don't choose duplicate features."]
            else:
                final_formula = str(w1)+"*"+f1+"+"+str(w2)+"*"+f2+"+"+str(w3)+"*"+f3+"+"+str(w4)+"*"+f4+"+"+str(w5)+"*"+f5+"+"+str(w6)+"*"+f6
                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c) is None:
                        if re.search("_Quantity", c): pass
                        else: en_columns.append(c)

                for ec in en_columns:
                    for i, indicator in enumerate(df[ec]):
                        if indicator == f1:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                            else:
                                score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores1.append(score)
                        elif indicator == f2:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                            else:
                                score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores2.append(score)
                        elif indicator == f3:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                            else:
                                score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores3.append(score)
                        elif indicator == f4:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)
                            else:
                                score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores4.append(score)
                        elif indicator == f5:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores5.append(score)
                            else:
                                score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores5.append(score)
                        elif indicator == f6:
                            value = df[ec+"_Quantity"][i]
                            if value == 0:
                                value = 0.000001
                                score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores6.append(score)
                            else:
                                score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                self_formula_scores6.append(score)


                for c in df.columns.values:
                    if re.search(r'[\u4e00-\u9fff]+', c):
                        if re.search("_Quantity", c): pass
                        else: zh_columns.append(c)
                
                for zc in zh_columns:
                    for i, indicator in enumerate(df[zc]):
                        if indicator == f1:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                                else:
                                    score = float((Decimal(str(w1))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores1.append(score)
                        elif indicator == f2:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                                else:
                                    score = float((Decimal(str(w2))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores2.append(score)
                        elif indicator == f3:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                                else:
                                    score = float((Decimal(str(w3))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores3.append(score)
                        elif indicator == f4:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                                else:
                                    score = float((Decimal(str(w4))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores4.append(score)
                        elif indicator == f5:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                                else:
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                                else:
                                    score = float((Decimal(str(w5))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores5.append(score)
                        elif indicator == f6:
                            if zh_columns.index(zc) == 0:
                                czi = 0
                                for zi, cc in enumerate(df.columns.values):
                                    if cc == zc:
                                        czi = zi + 1
                                value = df[df.columns.values[czi]][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores6.append(score)
                                else:
                                    score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores6.append(score)
                            else:
                                value = df[zc+"_Quantity"][i]
                                if value == 0:
                                    value = 0.000001
                                    score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores6.append(score)
                                else:
                                    score = float((Decimal(str(w6))*Decimal(str(value))).quantize(Decimal('.000'), ROUND_HALF_UP))
                                    self_formula_scores6.append(score)
            
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores1, name=f1, marker_color='rgb(158,202,225)', text=self_formula_scores1, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores2, name=f2, marker_color='#DB4D6D', text=self_formula_scores2, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores3, name=f3, marker_color='#986DB2', text=self_formula_scores3, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores4, name=f4, marker_color='#EEA9A9', text=self_formula_scores4, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores5, name=f5, marker_color='#89916B', text=self_formula_scores5, textposition="inside"))
            plot_data.append(go.Bar(x=en_columns+zh_columns, y=self_formula_scores6, name=f6, marker_color='#69B0AC', text=self_formula_scores6, textposition="inside"))

            if formula_name is None:
                formula_name = "Testing"
            
            layout =  go.Layout(title='Reading Ease Score of '+formula_name,
                                xaxis={'title': 'Text'},
                                yaxis={'title': 'Score'},
                                margin={'l': 50, 'b': 60, 't': 50, 'r': 50},
                                hovermode='closest', barmode='stack',
                                uniformtext_minsize=8, uniformtext_mode='hide')
            figure = go.Figure(data=plot_data, layout=layout)

            total_scores = [round(self_formula_scores1[i]+self_formula_scores2[i]+self_formula_scores3[i]+self_formula_scores4[i]+self_formula_scores5[i]+self_formula_scores6[i],3) for i in range(len(self_formula_scores1))]
            formula_score_df = pd.DataFrame({"Text":en_columns+zh_columns, f1:self_formula_scores1, f2:self_formula_scores2,
                                            f3:self_formula_scores3, f4:self_formula_scores4, f5:self_formula_scores5, 
                                            f6:self_formula_scores6, "Total Score":total_scores})
            features_df = formula_score_df.reindex(sorted(formula_score_df.columns[1:-1]), axis=1)
            head_df = formula_score_df[formula_score_df.columns[0]].to_frame()
            end_df = formula_score_df[formula_score_df.columns[-1]].to_frame()
            formula_score_df = pd.concat([head_df, features_df, end_df], axis=1)
            
            return html.Div([html.Mark("Your formula - "+formula_name+" is: "+final_formula, style={"background": random.choice(mark_colors_text),"padding": "0.1em 0.4em","margin": "0 0.2em","line-height": "1","border-radius": "0.35em",}),
                            dcc.Graph(figure={'data': plot_data,'layout': layout,}),
                            html.Br(),
                            dash_table.DataTable(columns=[{"name": i, "id": i} for i in formula_score_df.columns],
                                                data=formula_score_df.to_dict('records'), export_format='xlsx',
                                                style_cell={'overflow': 'hidden',
                                                            'textOverflow': 'ellipsis',
                                                            'maxWidth': 0})])

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)