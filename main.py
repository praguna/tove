from glob import glob
import streamlit as st
import argparse, os, glob
import json
from PIL import Image


number_of_files = 'number of files'
number_of_jpegs = 'number_of_images'
files_config_present = 'files_config_present'
config_info = 'config_info'


def get_all_files(root):
     return [os.path.basename(f) for f in glob.glob(os.path.join(root , "*"))]


def data_set_widget(path):
    datasets = get_all_files(path)
    # Add a selectbox to the sidebar:
    dataset = st.sidebar.selectbox(
        'Select your dataset below',
        datasets
    )
    curr_path = os.path.join(path, dataset)
    return curr_path

def get_values_of_data(images):
    l =  [img.split('_')[:-1] for img in images]
    proper = list(map(list, zip(*l)))
    return [list(set(p)) for p in proper], l 


def suggested_values(img_split, selected_primary_values):
     r = set()
     for v in img_split:
         for e in selected_primary_values:
            try: v.index(e)
            except ValueError: continue
            r.add(','.join(v))
     return list(r)
    
def _update_slider(keys, values):
    for k, v in zip(keys, values.split(',')):
        st.session_state[str(k)] = v
        

def exp_config_display_widegt(path):

    files = get_all_files(path)
    images = [f for f in files if f.endswith('jpg') or f.endswith('png') or f.endswith('jpeg') or f.endswith('bmp')]
    config_json = [f for f in files if f == 'config.json']
    sub_info = {'message' : 'No config file found, ignoring names (create as {names : [__] ... })'}
    
    if len(config_json) > 0:
        with open(os.path.join(path, config_json[0]), 'r+') as f:
            sub_info = json.load(f)
    
    info = {
        number_of_files : len(files),
        number_of_jpegs: len(images),
        files_config_present: len(config_json) > 0,
        config_info : sub_info
    }

    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")

    st.sidebar.subheader('Experiment Configurations:')

    st.sidebar.write(info)

    return info, images



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tove App')

    parser.add_argument('--data', action='append', help="Data Folder Path")
    
    try:
        args = parser.parse_args()
        path = args.data[0]
        if not os.path.exists(path): raise Exception()

    except Exception:
        raise Exception("Invalid Folder Path Arguments")


    curr_path = data_set_widget(path)

    info, images = exp_config_display_widegt(curr_path)

    values, img_split = get_values_of_data(images)

    if len(images) > 0:
        ext = images[0][images[0].index('_.') + 1 : ]

    selected_values = []
    labels = info[config_info]['names'] if info[files_config_present] else None
    init_val = info[config_info]['init'] if info[files_config_present] and 'init' in info[config_info] else None
    primary_index =  info[config_info]['primary_index'] if info[files_config_present] and 'primary_index' in info[config_info] else None
    if primary_index and labels:
        primary_index_pos = [labels.index(p) for p in primary_index]

    with st.expander("options"):
        for i, v in enumerate(values):
            label = labels[i] if labels and len(labels) > i else f'variable {i+1}'
            try:
                mv = sorted([int(e) for e in v])
                mv = [str(e) for e in mv]
            except Exception:
                mv = v
            if len(v) == 1: selected_values.append(st.radio(label, mv))
            else: selected_values.append(st.select_slider(label, mv , value=init_val[i] if init_val and len(init_val) > i else None, key=str(i)))
    try:
        image = Image.open(os.path.join(curr_path, '_'.join(selected_values + [ext])))
        st.image(image, caption='Data')
    except FileNotFoundError:
        st.warning('This Experiment was not found! Try other values!')
        if primary_index_pos:
            selected_primary_values = [e for p, e in enumerate(selected_values) if p in primary_index_pos]
            suggestions = suggested_values(img_split, selected_primary_values)
            st.write('Suggested :')
            for i in range(min(len(suggestions), 10)):
                c1, c2 = st.columns(2)
                with c1:
                    st.text(suggestions[i])
                with c2:
                    st.button('apply', key=f'apply_{i}', on_click=_update_slider, kwargs={"values" : suggestions[i], "keys" : range(len(labels))})


    # hide streamlit
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 