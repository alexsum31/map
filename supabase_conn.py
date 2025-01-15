#%%%

import os
from supabase import create_client, Client
from pathlib import Path
import pandas as pd

class supabase_conn:
    def __init__(self, project_url: str, api_key: str):
        self.supabase: Client = create_client(project_url, api_key)

    def login_by_email(self, email: str, password: str):
        response = self.supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return response
    def get_img_df(self):
        response = self.supabase.schema("public").table("img_raw").select("*").execute()
        df=pd.DataFrame.from_dict(response.data, orient='columns')
        df['img_dt']=pd.to_datetime(df['img_dt'])
        df['img_dt']= df['img_dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
        return df
    def get_loc_df(self):
        response = self.supabase.schema("public").table("loc_raw").select("*").execute()
        df=pd.DataFrame.from_dict(response.data, orient='columns')
        return df
    def upload_img(self,filename):
        path=('./img/')
        with open(path+filename, 'rb') as f:
            response = self.supabase.storage.from_("img").upload(
                file=f,
                path=filename,
                file_options={"cache-control": "3600", "upsert": "false"},
            )
        return response
    def upload_img_st(self,filename,f):
        response = self.supabase.storage.from_("img").upload(
                file=f,
                path=filename,
                file_options={"cache-control": "3600", "upsert": "false"},
            )
        return response
    def check_url(self,filename):
        response = self.supabase.storage.from_("img").get_public_url(
            filename
            )
        return response
    def img_row_insert(self,dict_str):
        response = self.supabase.schema("public").table("img_raw").insert([dict_str]).execute()
        return response
    def img_raw_maxid(self)->int:
        response = self.supabase.schema("public").table("img_raw").select("seq_id").execute()
        df=pd.DataFrame.from_dict(response.data, orient='columns')
        return int(df['seq_id'].max())
# %%
if __name__ == "__main__":

    print('abc')
# %%
