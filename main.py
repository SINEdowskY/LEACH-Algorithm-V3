import streamlit as st
from environment import Environment
st.set_option('deprecation.showPyplotGlobalUse', False)

amount_of_nodes = st.sidebar.slider("Nodes amount:", min_value=50, max_value=100)
number_of_rounds = st.sidebar.slider("Rounds amount:", min_value=100, max_value=200)
start = st.sidebar.button("Start")
env = Environment(amount_of_nodes, number_of_rounds)

if start:
    for i in range(number_of_rounds):
        st.title(f"Round {i+1}.")
        print(f"round{i+1}")
        st.pyplot(env.draw_graph())
        st.dataframe(env.graph_df, width=10000)
    st.title("Tests")
    st.pyplot(env.draw_tests_plot())
else:
    st.title("Leach Algorithm")