import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Dmitriy Kuzin"]
usernames = ["dkuzin"]
passwords = ["Argonauts1"]

hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("wb") as file:
#     pickle.dump(hashed_passwords, file)
with open('hashed_pw.pkl', 'wb') as f:
    # Dump the data to the file using the pickle.dump() function
    pickle.dump(hashed_passwords, f)
#%%
