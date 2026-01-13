import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from collections import Counter
import re

# Configuration de la page
st.set_page_config(
    page_title="SentimentScope - Analyse NLP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Télécharger les ressources NLTK nécessaires
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except:
        pass

download_nltk_data()

# Fonction d'analyse de sentiment
def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = "Positif"
            emoji = "😊"
            color = "#28a745"
        elif polarity < -0.1:
            sentiment = "Négatif"
            emoji = "😞"
            color = "#dc3545"
        else:
            sentiment = "Neutre"
            emoji = "😐"
            color = "#ffc107"
        
        return {
            'sentiment': sentiment,
            'emoji': emoji,
            'polarity': polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'color': color
        }
    except:
        return None

# Nettoyage du texte
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Header
st.title("📊 SentimentScope")
st.markdown("### Analyse de Sentiments avec NLP")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.radio(
        "Mode d'analyse",
        ["Texte Simple", "Analyse Multiple", "Upload CSV"]
    )
    
    st.markdown("---")
    st.info("💡 **À propos**\n\nSentimentScope utilise TextBlob pour analyser les sentiments dans les textes.")

# MODE 1: Texte Simple
if mode == "Texte Simple":
    st.header("✍️ Analyse de Texte Simple")
    
    text_input = st.text_area(
        "Entrez votre texte ici",
        height=150,
        placeholder="Écrivez ou collez votre texte pour analyser le sentiment..."
    )
    
    if st.button("🔍 Analyser", type="primary"):
        if text_input.strip():
            result = analyze_sentiment(text_input)
            
            if result:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Sentiment",
                        f"{result['emoji']} {result['sentiment']}"
                    )
                
                with col2:
                    st.metric(
                        "Polarité",
                        f"{result['polarity']:.2f}",
                        help="De -1 (très négatif) à +1 (très positif)"
                    )
                
                with col3:
                    st.metric(
                        "Subjectivité",
                        f"{result['subjectivity']:.2f}",
                        help="De 0 (objectif) à 1 (subjectif)"
                    )
                
                # Jauge de polarité
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['polarity'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': result['color']},
                        'steps': [
                            {'range': [-1, -0.1], 'color': "#ffebee"},
                            {'range': [-0.1, 0.1], 'color': "#fff9e6"},
                            {'range': [0.1, 1], 'color': "#e8f5e9"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': result['polarity']
                        }
                    },
                    title={'text': "Score de Sentiment"}
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Veuillez entrer du texte à analyser.")

# MODE 2: Analyse Multiple
elif mode == "Analyse Multiple":
    st.header("📝 Analyse de Textes Multiples")
    
    num_texts = st.number_input("Nombre de textes à analyser", min_value=2, max_value=10, value=3)
    
    texts = []
    for i in range(num_texts):
        text = st.text_area(f"Texte {i+1}", key=f"text_{i}", height=80)
        texts.append(text)
    
    if st.button("🔍 Analyser Tous", type="primary"):
        valid_texts = [t for t in texts if t.strip()]
        
        if valid_texts:
            results = []
            for idx, text in enumerate(valid_texts):
                result = analyze_sentiment(text)
                if result:
                    results.append({
                        'Texte': f"Texte {idx+1}",
                        'Sentiment': result['sentiment'],
                        'Polarité': result['polarity'],
                        'Subjectivité': result['subjectivity']
                    })
            
            if results:
                df = pd.DataFrame(results)
                
                # Afficher le tableau
                st.dataframe(df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    sentiment_counts = df['Sentiment'].value_counts()
                    fig_pie = px.pie(
                        values=sentiment_counts.values,
                        names=sentiment_counts.index,
                        title="Distribution des Sentiments",
                        color=sentiment_counts.index,
                        color_discrete_map={
                            'Positif': '#28a745',
                            'Négatif': '#dc3545',
                            'Neutre': '#ffc107'
                        }
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Bar chart
                    fig_bar = px.bar(
                        df,
                        x='Texte',
                        y='Polarité',
                        title="Score de Polarité par Texte",
                        color='Sentiment',
                        color_discrete_map={
                            'Positif': '#28a745',
                            'Négatif': '#dc3545',
                            'Neutre': '#ffc107'
                        }
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("⚠️ Veuillez entrer au moins un texte valide.")

# MODE 3: Upload CSV
elif mode == "Upload CSV":
    st.header("📤 Upload de Fichier CSV")
    
    st.info("📋 **Format attendu** : Le fichier CSV doit contenir une colonne nommée 'text' ou 'texte'")
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Trouver la colonne de texte
            text_col = None
            for col in df.columns:
                if col.lower() in ['text', 'texte', 'comment', 'commentaire', 'review', 'avis']:
                    text_col = col
                    break
            
            if text_col:
                st.success(f"✅ Colonne '{text_col}' détectée !")
                
                if st.button("🚀 Lancer l'Analyse", type="primary"):
                    with st.spinner("Analyse en cours..."):
                        results = []
                        for text in df[text_col]:
                            if pd.notna(text) and str(text).strip():
                                result = analyze_sentiment(str(text))
                                if result:
                                    results.append({
                                        'Texte Original': str(text)[:100] + "..." if len(str(text)) > 100 else str(text),
                                        'Sentiment': result['sentiment'],
                                        'Polarité': result['polarity'],
                                        'Subjectivité': result['subjectivity']
                                    })
                        
                        if results:
                            results_df = pd.DataFrame(results)
                            
                            # Statistiques
                            st.header("📊 Résultats de l'Analyse")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Analysés", len(results_df))
                            
                            with col2:
                                positifs = len(results_df[results_df['Sentiment'] == 'Positif'])
                                st.metric("😊 Positifs", positifs)
                            
                            with col3:
                                negatifs = len(results_df[results_df['Sentiment'] == 'Négatif'])
                                st.metric("😞 Négatifs", negatifs)
                            
                            with col4:
                                neutres = len(results_df[results_df['Sentiment'] == 'Neutre'])
                                st.metric("😐 Neutres", neutres)
                            
                            # Tableau des résultats
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Visualisations
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Pie chart
                                sentiment_counts = results_df['Sentiment'].value_counts()
                                fig_pie = px.pie(
                                    values=sentiment_counts.values,
                                    names=sentiment_counts.index,
                                    title="Distribution des Sentiments",
                                    color=sentiment_counts.index,
                                    color_discrete_map={
                                        'Positif': '#28a745',
                                        'Négatif': '#dc3545',
                                        'Neutre': '#ffc107'
                                    }
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            with col2:
                                # Histogramme de polarité
                                fig_hist = px.histogram(
                                    results_df,
                                    x='Polarité',
                                    nbins=20,
                                    title="Distribution de la Polarité",
                                    color='Sentiment',
                                    color_discrete_map={
                                        'Positif': '#28a745',
                                        'Négatif': '#dc3545',
                                        'Neutre': '#ffc107'
                                    }
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                            
                            # Word Cloud
                            st.header("☁️ Nuage de Mots")
                            all_text = ' '.join(df[text_col].dropna().astype(str))
                            cleaned_text = clean_text(all_text)
                            
                            if cleaned_text:
                                wordcloud = WordCloud(
                                    width=800,
                                    height=400,
                                    background_color='white',
                                    colormap='viridis'
                                ).generate(cleaned_text)
                                
                                fig, ax = plt.subplots(figsize=(10, 5))
                                ax.imshow(wordcloud, interpolation='bilinear')
                                ax.axis('off')
                                st.pyplot(fig)
                            
                            # Bouton de téléchargement
                            csv = results_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="💾 Télécharger les Résultats (CSV)",
                                data=csv,
                                file_name="sentiment_analysis_results.csv",
                                mime="text/csv"
                            )
            else:
                st.error("❌ Aucune colonne de texte trouvée. Veuillez vérifier votre fichier.")
        
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier : {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "📊 SentimentScope - Analyse de Sentiments avec NLP | Développé avec Streamlit & TextBlob"
    "</div>",
    unsafe_allow_html=True
)
