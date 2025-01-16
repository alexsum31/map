import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium ,folium_static
from folium.plugins import Draw ,BeautifyIcon
import datetime
import pandas as pd
from streamlit.components.v1 import html
from supabase_conn import supabase_conn
import uuid
from st_login_form import login_form
from PIL import Image, ImageFile,ImageChops, ExifTags
import math
import base64
from io import BytesIO

SUPABASE_PROJECT_URL=st.secrets['SUPABASE_URL']
SUPABASE_API_KEY=st.secrets['SUPABASE_KEY']
SUPABASE_UR=st.secrets['LOGIN_USER']
SUPABASE_PD=st.secrets['LOGIN_PW']
#XLSPATH='loc.xlsx'


def cropimage(image_file):
    img = Image.open(image_file)
    have_date='2020:01:01 00:00:00'
    have_orientation=='0'
    exif = img._getexif()
    
    if exif is not None:
        for (tag, value) in exif.items():
            key = ExifTags.TAGS.get(tag, tag)
            if key=='DateTimeDigitized':
                have_date=str(value)
            if key=='Orientation':
                have_orientation=str(value)
                
        if have_orientation == '3':
            img=img.rotate(180, expand=True)
        elif have_orientation== '6':
            img=img.rotate(270, expand=True)
        elif have_orientation == '8':
            img=img.rotate(90, expand=True)     
    # try:
        # for orientation in ExifTags.TAGS.keys():
        #     if ExifTags.TAGS[orientation]=='Orientation':
        #         break
        # exif = img._getexif()
        # if exif[orientation] == 3:
        #     img=img.rotate(180, expand=True)
        # elif exif[orientation] == 6:
        #     img=img.rotate(270, expand=True)
        # elif exif[orientation] == 8:
        #     img=img.rotate(90, expand=True)       
    # except:
    #     print("no tag")
    height=img.height
    width=img.width
    if width>height : 
        new_width  = int(500)#int(600 *((100-border)/100))
        new_height = int(math.ceil(new_width * height / width ))
    else:
        #new_height = 750
        new_height  =int(500)#int(600 *((100-border)/100))
        new_width  = int(math.ceil(new_height * width / height))
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS) ,have_date ,have_orientation

# function for read excel to list
def read_excel_to_list(file_path):
    df = pd.read_excel(file_path,sheet_name='loc_raw')
    #datetime to date
    #df['img_dt']=df['img_dt'].dt.strftime('%Y-%m-%d')
    return df.head(10)
def read_excel_img_to_list(file_path):
    df = pd.read_excel(file_path,sheet_name='img_raw')
    #datetime to date
    df['img_dt']=df['img_dt'].dt.strftime('%Y-%m-%d')
    return df
# function add line to map
def add_line_map(fullmap,df,line_name,group_name):
    colorname=df['line_color'].iloc[0]
    line_list=df.values.tolist()
    line_list=[(x[3],x[4]) for x in line_list]
    return folium.PolyLine(line_list,color=colorname,weight=5, tooltip=group_name)

#function add marker to map
def add_marker_map(fullmap,df,group_name,img_df):
    def calculate_age(date1_str, date2_str):
       
        date1 = datetime.datetime.strptime(date1_str, '%Y-%m-%d')
        date2 = datetime.datetime.strptime(date2_str, '%Y-%m-%d')
       
        years_diff = date1.year - date2.year
        months_diff = date1.month - date2.month
        
        if date1.day < date2.day:
            months_diff -= 1

        if months_diff < 0:
            years_diff -= 1
            months_diff += 12

        return f"{years_diff}Y{months_diff}M"
   
    location_list=df.values.tolist()

    
    
    location_list=[(x[3],x[4],x[1]) for x in location_list]
    for x in location_list:
        img_df_filter=img_df[img_df['name']==x[2]]
        sort_img = img_df_filter['img'].tolist()
        sort_dt = img_df_filter['img_dt'].tolist()
    
        #print(sort_dt[0])

        year_ago=calculate_age(sort_dt[0],'2020-10-31')    
        max_len_of_img=len(sort_img)-1
        html_str = f"""
            <br>
            <img id="sort_img" src="{sort_img[0]}" style="width: 200px;" >
            <div style="text-align:center;">
            <p>{x[2]}<br>
            <span id="sort_dt">{sort_dt[0]}</span> / <span id="year_old">{year_ago}</span>
            </p>
            </div>
            <div style="text-align:center;padding: 5px;">
              <button onclick="if(parseInt(document.getElementById('count').innerHTML) > 0) {{
                    document.getElementById('count').innerHTML--; 
                    var dates = {sort_dt};
                    var img_num = {sort_img};
                    var date2 = new Date(dates[parseInt(document.getElementById('count').innerHTML) % dates.length]);
                    var date1 = new Date('October 31, 2020 12:00:00');
                    var diffInMonths = (date2.getFullYear() - date1.getFullYear()) * 12 + (date2.getMonth() - date1.getMonth());
                    var years = Math.floor(diffInMonths / 12);
                    var months = (diffInMonths % 12) -1;
                    document.getElementById('sort_dt').innerHTML = dates[parseInt(document.getElementById('count').innerHTML) % dates.length];
                    document.getElementById('sort_img').src = img_num[parseInt(document.getElementById('count').innerHTML) % img_num.length];
                    document.getElementById('year_old').innerHTML = ''+ years +'Y'+ months +'M';
                }}">
                <</button>           
                <span id="count">0</span> / {max_len_of_img}
                <button onclick="document.getElementById('count').innerHTML++; 
                var dates = {sort_dt};
                var img_num = {sort_img};
                var date2 = new Date(dates[parseInt(document.getElementById('count').innerHTML) % dates.length]);
                var date1 = new Date('October 31, 2020 12:00:00');
                var diffInMonths = (date2.getFullYear() - date1.getFullYear()) * 12 + (date2.getMonth() - date1.getMonth());
                var years = Math.floor(diffInMonths / 12);
                var months = (diffInMonths % 12) -1;
                document.getElementById('sort_dt').innerHTML = dates[parseInt(document.getElementById('count').innerHTML) % dates.length];
                document.getElementById('sort_img').src = img_num[parseInt(document.getElementById('count').innerHTML) % img_num.length];
                document.getElementById('year_old').innerHTML = ''+ years +'Y'+ months +'M';
                ">></button>
                    </div>
            """
#{count_value}
        current_bg='white'
        current_font='black'
        if sort_img[0]=='https://kycvtdlganlfymsyczpu.supabase.co/storage/v1/object/public/img/no_img.jpeg':
            current_bg='black'
            current_font='white'
        folium.Marker((x[0],x[1]),popup=html_str,icon=folium.DivIcon(
                                        icon_size=(150,36),
                                        icon_anchor=(0,0),
                                    html=f'<div style="font-size: 8pt;background-color:{current_bg};color:{current_font};width: 25%;text-align:center;">{x[2]}</div>',
                                        )
                      ).add_to(group_name)
   

def draw_all_mark(df,fullmap,df_img):
    new_df=df.groupby(['group','line']).count().reset_index()

    n_line_name_list=new_df['line'].unique().tolist()
    n_group_list=new_df['group'].unique().tolist()

    for group in n_group_list:
        group_map_name = folium.FeatureGroup(group).add_to(fullmap)
      
        #check df for each group and line if yes to run, else skip
        for line in n_line_name_list:
            group_filter_df_point=df[(df['line']==line) & (df['group']==group)& (df['point_draw']=='Y')]
            group_filter_df_line=df[(df['line']==line) & (df['group']==group)& (df['line_draw']=='Y')]
            
            if group_filter_df_line.shape[0]>1:
                
                add_line_map(fullmap,group_filter_df_line,line,group).add_to(group_map_name)
                add_marker_map(fullmap,group_filter_df_point,group_map_name,df_img)
      
 
 
def main_app_draw_map():
    r=supabase_conn(SUPABASE_PROJECT_URL, SUPABASE_API_KEY)
    r.login_by_email(SUPABASE_UR, SUPABASE_PD)
    df=r.get_loc_df()
    img_df=r.get_img_df()
    
    #if 'map' not in st.session_state or st.session_state.map is None:
    m = folium.Map(location=[22.32176,114.122024], tiles="Cartodb Positron",zoom_start=11)####center on Liberty Bell, add marker #11
    #.add_child(folium.LatLngPopup())
    draw_all_mark(df,m,img_df)
    
    folium.LayerControl().add_to(m)

    #Draw(export=True).add_to(m)
    
    #st.session_state.map = m
    folium.Map()
    st_folium(m, width=900,use_container_width=True, returned_objects=[])
    
def draw_uploader():
    r=supabase_conn(SUPABASE_PROJECT_URL, SUPABASE_API_KEY)
    r.login_by_email(SUPABASE_UR, SUPABASE_PD)
    df=r.get_loc_df()
    uploaded_file=st.file_uploader("Upload file", type=['jpeg','jpg'])
    if uploaded_file is not None:
        buffered = BytesIO()
        resize_img , pic_date ,ori_str=cropimage(uploaded_file)
        date_format = "%Y:%m:%d %H:%M:%S"
        date_time_obj = datetime.datetime.strptime(pic_date, date_format)
        resize_img.save(buffered, format="JPEG")
        f=buffered.getvalue()
        st.image(uploaded_file,width=60)
        st.write(ori_str)
        st.write(f'Take picture {pic_date}')
        with st.form(key='my_form',clear_on_submit=True):
            location_list=df['name'].unique().tolist()
            select_location=st.selectbox('Select location',location_list)
            picture_dt= st.date_input("Photo Date",value=date_time_obj)
            formatted_date = picture_dt.strftime('%Y-%m-%d')
            submit_button = st.form_submit_button(label='Submit')
            
            if submit_button:
               
                generated_uuid = uuid.uuid4()
                r.upload_img_st(str(generated_uuid)+'.jpeg',f)
                url_path_full=r.check_url(str(generated_uuid)+'.jpeg')
                max_num=r.img_raw_maxid()+1
                null_dict=  dict_str ={
                                    'seq_id': max_num,
                                    'name': select_location,
                                    'img':url_path_full,
                                    'img_dt': formatted_date 
                            }
                msg=r.img_row_insert(dict_str)
                
                st.write(msg)


if __name__ == "__main__":
    st.set_page_config(page_title='Map')
    loginSection = st.container()
    headerSection = st.container()

    
    with headerSection:
        #if 'authenticated' not in st.session_state:
        client = login_form(allow_create =False)
     
        if st.session_state["authenticated"]:
            main_app_draw_map()
            if st.session_state["username"]:
                draw_uploader()

                