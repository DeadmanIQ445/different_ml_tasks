import streamlit as st
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import seaborn as sns
import dbscan
import time

st.title('DBSCAN')

@st.cache
def load_data(n_samples):
    data = make_blobs(n_samples=n_samples, n_features=2)
    return data



data_load_state = st.text('Generating data...')
data, y = load_data(int(st.text_input("n_samples", 100)))
data_load_state.text("Done! (using st.cache)")

st.subheader('DBSCAN')
eps = st.slider('eps', value=0.5, min_value=0.0, max_value=1.0, step=0.05)
minPts = st.slider('minPts', value=1, min_value=1, max_value=20, step=1)

db = DBSCAN(eps=eps,min_samples=minPts)

labels = db.fit_predict(data) 
fig, ax = plt.subplots()
scatter = ax.scatter(data[:,0],data[:,1], c=labels)
legend1 = ax.legend(*scatter.legend_elements(),
                    loc="lower left", title="Classes")
ax.add_artist(legend1)

st.pyplot(fig)

