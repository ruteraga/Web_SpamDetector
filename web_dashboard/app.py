import streamlit as st 
import tensorflow as tf

message=st.text_input("Enter your message:","Congratulations! You’ve won a $500 Amazon gift card. Claim it here [Link]")
model=tf.keras.models.load_model('text_model.keras')

if not message:
    st.write("No message was provided.")

else:
    message=tf.expand_dims(message, -1)
    prediction=model.predict(message)
    pred_n=prediction[0][0]
    pred_prob=tf.sigmoid(pred_n).numpy()
    perc=pred_prob*100
    text_type =" spam" if pred_prob> 0.5 else "ham"
    st.write("The message is ", text_type, " with the probability of being a spam of: ", perc, " %")